#!/usr/bin/env python3
"""Conservative Vietnamese review guard. No rewriting or semantic certification.

Exit 0: no detected lint/risk findings, or internally consistent verification.
Exit 1: findings or invalid/stale record. Exit 2: usage/input error.
A check record is an explicit reviewer attestation, NOT a signature or proof of meaning.
Reviewer identity/role is self-identified, not authenticated. Paths stay under cwd;
this is a file-scope guard, not a complete sandbox or protection against races.
Lint line/column positions are 1-based Unicode code-point offsets, not bytes,
UTF-16 units, display cells, or grapheme-cluster counts.
Anyone able to rewrite it can recompute its checksum. Recheck after every edit.
"""
import argparse
import difflib
import hashlib
import json
import re
import sys
import unicodedata
from pathlib import Path

VERSION = '2.0.0'
SCHEMA = 2
PROTOCOL = 'edit-compare-review-check; any byte change requires a new review and record'
WORDS = {
    'condition_changed': r'\b(?:chỉ khi|nếu|khi|miễn là|với điều kiện|trong trường hợp)\b',
    'exception_changed': r'\b(?:trừ khi|ngoại trừ|trừ|ngoại lệ)\b',
    'quantifier_changed': r'\b(?:tất cả|mọi|mỗi|một số|ít nhất|nhiều nhất|chỉ|duy nhất)\b',
    'time_changed': r'\b(?:đã|đang|sẽ|vừa|sắp|trước khi|sau khi)\b',
    'comparison_changed': r'\b(?:hơn|kém|bằng|so với|thay vì|không phải|mà là)\b',
    'negation_changed': r'\b(?:không|chẳng|chưa|chả|đừng|không hề)\b',
    'modality_changed': r'\b(?:có thể|phải|cần|nên|được phép|bắt buộc|chắc chắn|có lẽ)\b',
    'causality_changed': r'\b(?:bởi vì|vì|do|nên|do đó|vì vậy|dẫn đến|khiến)\b',
    'attribution_changed': r'\b(?:theo|cho biết|cho rằng|nói rằng|khẳng định|báo cáo|trích dẫn)\b',
}

def canonical(obj):
    return json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode('utf-8')

def sha(data): return hashlib.sha256(data).hexdigest()

def safe_path(raw):
    """Reject traversal, hidden components, and resolved paths outside cwd.

    Resolve every path before use, including output parents and existing symlinks.
    This assumes a trusted local workspace without concurrent symlink replacement.
    """
    root = Path.cwd().resolve()
    path = Path(raw)
    if '..' in path.parts:
        raise ValueError('Parent traversal is not allowed.')
    absolute = path if path.is_absolute() else root / path
    try:
        relative = absolute.relative_to(root)
    except ValueError:
        raise ValueError('Path must stay under the current working directory.') from None
    if any(part.startswith('.') for part in relative.parts):
        raise ValueError('Dot-prefixed path components are not allowed.')
    resolved = absolute.resolve()
    try:
        relative = resolved.relative_to(root)
    except ValueError:
        raise ValueError('Resolved path escapes the current working directory.') from None
    if any(part.startswith('.') for part in relative.parts):
        raise ValueError('Resolved dot-prefixed path components are not allowed.')
    if resolved.exists() and not resolved.is_file():
        raise ValueError('A regular file is required; directories, pipes and devices are not allowed.')
    return resolved


def read(path):
    data = Path(path).read_bytes()
    return data, data.decode('utf-8')

def protected(text):
    """Return exact spans; code fences may be indented up to 3 spaces.

    Unclosed fences protect to EOF. Inline code pairs exact backtick lengths.
    This intentionally is a small Markdown recognizer, not a full parser.
    """
    spans = []
    offset = 0
    fence = None
    for line in text.splitlines(keepends=True):
        if fence:
            marker, length, start = fence
            if re.match(r'^ {0,3}' + re.escape(marker) + '{' + str(length) + r',}[ \t]*(?:\r?\n)?$', line):
                spans.append((start, offset + len(line)))
                fence = None
        else:
            m = re.match(r'^ {0,3}(`{3,}|~{3,})(.*)', line)
            if m:
                fence = (m[1][0], len(m[1]), offset)
        offset += len(line)
    if fence: spans.append((fence[2], len(text)))
    def overlaps(a,b): return any(a < y and b > x for x,y in spans)
    for m in re.finditer(r'(?<!`)(`+)(?!`)([\s\S]*?)(?<!`)\1(?!`)', text):
        if not overlaps(*m.span()): spans.append(m.span())
    for m in re.finditer(r'(?:https?://|www\.)[^\s<>`]+', text, re.I):
        end=m.end()
        while end>m.start() and text[end-1] in '.,;:!?': end-=1
        if not overlaps(m.start(),end): spans.append((m.start(),end))
    # Preserve front matter, comments, markup attributes and link destinations.
    # This is deliberately not a full CommonMark/HTML parser.
    patterns = [r'\A---[ \t]*\r?\n[\s\S]*?\n(?:---|\.\.\.)[ \t]*(?:\r?\n|$)',
                r'<!--[\s\S]*?(?:-->|$)',
                r'“[^”\n]*”|«[^»\n]*»|"[^"\n]*"',
                r'<[^<>\n]*>',
                r'(?<=\])\((?:[^()\n]|\([^()\n]*\))*\)',
                r'(?m)^ {0,3}\[[^]\n]+\]:[^\n]*']
    for pattern in patterns:
        for m in re.finditer(pattern, text):
            spans.append(m.span())
    merged=[]
    for a,b in sorted(spans):
        if merged and a <= merged[-1][1]: merged[-1]=(merged[-1][0],max(b,merged[-1][1]))
        else: merged.append((a,b))
    return merged

def mask(text):
    chars = list(text)
    for a,b in protected(text):
        chars[a:b] = ['\n' if c == '\n' else ' ' for c in text[a:b]]
    return ''.join(chars)

def lint(text, terms=None):
    spans = protected(text)
    # Work only on unprotected segments; mask padding must never create findings.
    segments=[]; pos=0
    for a,b in spans:
        segments.append((pos,text[pos:a]));pos=b
    segments.append((pos,text[pos:]))
    result=[]
    def add(code, index, message):
        result.append({'code':code,'line':text.count('\n',0,index)+1,
                       'column':index-text.rfind('\n',0,index),'message':message})
    for start, segment in segments:
        normalized = unicodedata.normalize('NFC',segment)
        if normalized != segment:
            # The first differing code point identifies the first changed cluster.
            first = next((i for i, (old, new) in enumerate(zip(segment, normalized)) if old != new), min(len(segment), len(normalized)))
            add('unicode_nfc',start+first,'Non-NFC text: review Unicode normalization; no automatic edit.')
        for match in re.finditer(r'[\u200b\u200c\u200d\u2060\ufeff]',segment):
            add('zero_width',start+match.start(),'Invisible Unicode character: review intent before changing.')
        for match in re.finditer(r'(?<=[^\s]) {2,}(?=[^\s])',segment):
            add('repeated_spaces',start+match.start(),'Repeated internal spaces: review formatting intent.')
        for match in re.finditer(r'[^\S\r\n]+(?=[,.;:!?])',segment):
            add('space_before_punctuation',start+match.start(),'Space before punctuation: review typography.')
    terms = terms or {}
    allowed = {unicodedata.normalize('NFC',x).casefold() for x in terms.get('allow',[])}
    for term in terms.get('flag',[]):
        if unicodedata.normalize('NFC',term).casefold() in allowed: continue
        for start,segment in segments:
            for match in re.finditer(r'(?<!\w)' + re.escape(term) + r'(?!\w)',segment,re.I):
                add('project_term',start+match.start(),'Project term to review, not an automatic replacement.')
                result[-1]['term']=term
    return sorted(result,key=lambda d:(d['line'],d['column'],d['code']))

def diff(before, after, before_bytes=None, after_bytes=None, terms=None):
    # Normalize only the semantic-token view, never source/protected text or hashes.
    a,b = unicodedata.normalize('NFC',mask(before)),unicodedata.normalize('NFC',mask(after))
    risks=[]
    def risk(code,old,new):
        if old != new:
            risks.append({'code':code,'before':old,'after':new,'message':'Changed surface evidence; human review required.'})
    risk('numbers_changed',re.findall(r'\d+(?:[.,:/-]\d+)*',a),re.findall(r'\d+(?:[.,:/-]\d+)*',b))
    for code,pattern in WORDS.items():
        risk(code,re.findall(pattern,a.casefold()),re.findall(pattern,b.casefold()))
    # Catch token redistribution across sentence boundaries even when global counts agree.
    def sentence_cues(text):
        return [{code:re.findall(pattern,sentence.casefold()) for code,pattern in WORDS.items()}
                for sentence in re.split(r'[.!?]+(?:[ \t]+|\n|$)|\n+',text) if sentence.strip()]
    if any(re.search(pattern,a.casefold()) or re.search(pattern,b.casefold()) for pattern in WORDS.values()):
        risk('sentence_scope_changed',sentence_cues(a),sentence_cues(b))
    risk('protected_changed',[before[x:y] for x,y in protected(before)], [after[x:y] for x,y in protected(after)])
    if terms and terms.get('protect'):
        def inventory(text):
            return [(term,len(re.findall(r'(?<!\w)'+re.escape(term)+r'(?!\w)',text))) for term in terms['protect']]
        risk('project_protected_changed',inventory(before),inventory(after))
    # Unified diff lines are LF-delimited; Unicode separators and CR alone
    # are content, not line breaks. Keep CRLF and final-newline status exact.
    def lf_lines(text):
        parts = text.split('\n')
        return [part + '\n' for part in parts[:-1]] + ([parts[-1]] if parts[-1] else [])
    lines = difflib.unified_diff(lf_lines(before), lf_lines(after), fromfile='before', tofile='after')
    textual_diff = ''.join(line if line.endswith('\n') else line + '\n\\ No newline at end of file\n' for line in lines)
    return {'unified_diff':textual_diff,'changed': before_bytes != after_bytes if before_bytes is not None else before != after,
            'human_review_required':True,'risks':risks,
            'limitations':'Heuristic surface checks can miss meaning, names, scope, and reordered claims. No semantic proof.'}

def load_json_file(path):
    if path is None: return None, None
    data,text = read(path)
    value=json.loads(text)
    if not isinstance(value,dict): raise ValueError('Configuration must be a JSON object.')
    return value,sha(data)

def validate_terms(value):
    if value is None: return {}
    if set(value)-{'allow','flag','protect'}: raise ValueError('Unknown term configuration key.')
    for key,items in value.items():
        if not isinstance(items,list) or len(items)>1000 or any(not isinstance(x,str) or not x.strip() or len(x)>200 or '\n' in x for x in items):
            raise ValueError('Term lists require at most 1000 nonempty literal strings, each at most 200 characters.')
    return value

def payload(bb,bt,ab,at,reviewer,review,mode='edit',terms=None,terms_hash=None,dispositions=None,dispositions_hash=None,strict=False):
    comparison=diff(bt,at,bb,ab,terms) if mode=='edit' else None
    diagnostics={'before':lint(bt,terms) if mode=='edit' else [],'after':lint(at,terms)}
    items=[]
    for origin, findings in list(diagnostics.items()) + [('comparison',comparison['risks'] if comparison else [])]:
        for index,finding in enumerate(findings):
            # Bind decisions to exact inputs as well as the finding, not mutable line numbers alone.
            ident=sha(canonical([sha(bb),sha(ab),mode,terms_hash,origin,index,finding]))[:24]
            items.append({'id':ident,'origin':origin,'finding':finding})
    decisions=dispositions or {}
    known={item['id'] for item in items}
    if set(decisions)-known: raise ValueError('Disposition does not match a current finding.')
    for ident,decision in decisions.items():
        if not isinstance(decision,dict) or set(decision)!={'decision','reason'} or decision['decision'] not in ('kept','resolved','needs_author') or not isinstance(decision['reason'],str) or not decision['reason'].strip():
            raise ValueError('Each disposition needs decision kept/resolved/needs_author and a nonempty reason.')
    complete=known==set(decisions) and all(x['decision']!='needs_author' for x in decisions.values())
    if strict and not complete: raise ValueError('Every finding requires a resolved or kept disposition; unresolved findings remain.')
    result={'schema_version':SCHEMA,'tool_version':VERSION,'revision_protocol':PROTOCOL,
            'mode':mode,'before_sha256':sha(bb),'after_sha256':sha(ab),
            'diagnostics':diagnostics,'comparison':comparison,'reviewer':reviewer,'review':review,
            'terms_sha256':terms_hash,'dispositions_sha256':dispositions_hash,
            'review_items':items,'dispositions':decisions,'review_complete':complete,
            'require_dispositions':strict,'attestation_only':True}
    if mode=='compose':
        result['material_sha256']=sha(bb)
        result['limitations']='Prompt/material binding only. No semantic comparison or evidence-grounding certification.'
    return result

def emit(value, as_json=True):
    # All outputs remain machine readable; --json explicitly documents the contract.
    print(json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2))

def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    sub=parser.add_subparsers(dest='command',required=True)
    p=sub.add_parser('lint');p.add_argument('file');p.add_argument('--json',action='store_true')
    for cmd in ('diff','check','verify'):
        p=sub.add_parser(cmd);p.add_argument('before');p.add_argument('after');p.add_argument('--json',action='store_true')
        if cmd in ('check','verify'): p.add_argument('--record',required=True)
        if cmd=='check':
            p.add_argument('--review',required=True,help='Explicit reviewer attestation; never claim unperformed human approval')
            p.add_argument('--reviewer',required=True,help='Self-identified reviewer name and role (for example: Meiiie, AI assistant)')
    for p in sub.choices.values():
        p.add_argument('--terms',help='Explicit safe JSON literal allow/flag/protect lists')
        if p.prog.split()[-1] != 'lint': p.add_argument('--mode',choices=('edit','compose'),default='edit')
        if p.prog.split()[-1] in ('check','verify'):
            p.add_argument('--dispositions',help='Explicit JSON mapping finding ids to decision and reason')
            p.add_argument('--require-dispositions',action='store_true')
    args=parser.parse_args(argv)
    try:
        # Validate every requested path before reading any file.
        for field in ('file', 'before', 'after', 'record', 'terms', 'dispositions'):
            if getattr(args, field, None) is not None:
                setattr(args, field, safe_path(getattr(args, field)))
        term_data,term_hash=load_json_file(args.terms)
        terms=validate_terms(term_data)
        if args.command=='lint':
            _,text=read(args.file);d=lint(text,terms);emit({'diagnostics':d});return int(bool(d))
        bb,bt=read(args.before);ab,at=read(args.after)
        comparison=diff(bt,at,bb,ab,terms) if args.mode=='edit' else None
        if args.command=='diff':
            emit(comparison if comparison is not None else {'mode':'compose','comparison':None,'material_sha256':sha(bb),'after_sha256':sha(ab),'human_review_required':True});return int(bool(comparison and comparison['risks']))
        decisions,decisions_hash=load_json_file(args.dispositions)
        options=(args.mode,terms,term_hash,decisions,decisions_hash,args.require_dispositions)
        if args.command=='check':
            if not args.review.strip() or not args.reviewer.strip():
                raise ValueError('Review and reviewer must be nonempty.')
            inputs=[p for p in (args.before,args.after,args.terms,args.dispositions) if p is not None]
            if Path(args.record).resolve() in [Path(p).resolve() for p in inputs]:
                raise ValueError('Record path must not overwrite an input.')
            # Check hard-link identity as well as canonical paths.
            if Path(args.record).exists() and any(Path(args.record).samefile(p) for p in inputs):
                raise ValueError('Record path must not overwrite an input.')
            data=payload(bb,bt,ab,at,args.reviewer,args.review,*options)
            data['record_sha256']=sha(canonical(data))
            Path(args.record).write_bytes(canonical(data)+b'\n')
            findings=bool(data['diagnostics']['before'] or data['diagnostics']['after'] or (comparison and comparison['risks']))
            emit({'record_written':True,'findings':findings,'attestation_only':True,'human_review_required':True})
            return int(findings)
        try:
            data=json.loads(Path(args.record).read_text(encoding='utf-8'))
            if not isinstance(data,dict): raise ValueError('Record must be an object.')
            review=data.get('review');reviewer=data.get('reviewer')
            if not isinstance(review,str) or not review.strip() or not isinstance(reviewer,str) or not reviewer.strip():
                raise ValueError('Missing review attestation.')
            expected=payload(bb,bt,ab,at,reviewer,review,*options)
            expected['record_sha256']=sha(canonical(expected))
            if canonical(data) != canonical(expected): raise ValueError('Record differs from current files, schema, checks, or checksum.')
        except (OSError,UnicodeError,ValueError,TypeError) as exc:
            emit({'valid':False,'reason':str(exc)});return 1
        emit({'valid':True,'attestation_only':True,'human_review_required':True,
              'meaning_certified':False,'warning':'Checksum is not authentication. A rewritten record can be rehashed.'})
        return 0
    except (OSError,UnicodeError,ValueError,RuntimeError) as exc:
        print(json.dumps({'error':str(exc)},ensure_ascii=False),file=sys.stderr)
        return 2

if __name__=='__main__': sys.exit(main())
