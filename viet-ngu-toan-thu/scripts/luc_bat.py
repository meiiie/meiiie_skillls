#!/usr/bin/env python3
"""Conservative orthographic lục bát diagnostics; Python standard library only.

Run: python luc_bat.py poem.txt --json   (omit path or use - for UTF-8 stdin).
Counts are tiếng candidates, not linguistic words or certified spoken syllables.
No rhyme decision, dictionary, rewriting, language identification, or dialect repair.
File inputs must be regular, non-hidden files under cwd; traversal and escaped
symlinks are rejected. This scope guard assumes no concurrent symlink changes.
"""
import argparse
import json
from viet_guard import safe_path
import sys
import unicodedata as ud

TONES = {'\u0300': 'B', '\u0301': 'T', '\u0309': 'T', '\u0303': 'T', '\u0323': 'T'}
SHAPES = {'\u0302', '\u0306', '\u031b'}
BASE = set('abcdeghiklmnopqrstuvxyđ')
VOWELS = set('aeiouy')
LIMITATIONS = [
    'Counts are punctuation/whitespace-delimited tiếng candidates, not linguistic words or verified spoken syllables.',
    'Tone classes describe spelling only, conditional on a token being one Vietnamese tiếng. Language, spelling validity, and pronunciation are not certified.',
    'Rhyme links only identify traditional positions. Dialect, vowel quality, medials, and codas require human phonological review; no rhyme is certified.',
    'The first nonempty content line is assumed to be a six-tiếng line; subsequent content lines alternate six/eight. Blank and punctuation-only lines do not reset parity.',
    'Traditional even-position patterns are a reference, not a verdict on quality or permissible lục bát variants. Opposing ngang/huyền at positions 6 and 8 of the eight-tiếng line is not checked.',
    'Regional vocabulary is retained. No automatic rewriting or normalization of the original text occurs.',
]


def tone_class(token):
    """Return orthographic B/T, or None if unsupported or clearly ambiguous."""
    decomposed = ud.normalize('NFD', token.lower())
    letters = [c for c in decomposed if ud.category(c).startswith('L')]
    marks = [c for c in decomposed if ud.category(c).startswith('M')]
    if (not letters or not any(c in VOWELS for c in letters)
            or any(c not in BASE for c in letters)
            or any(c not in TONES and c not in SHAPES for c in marks)
            or any(not ud.category(c).startswith(('L','M')) for c in decomposed)):
        return None
    tones = [TONES[c] for c in marks if c in TONES]
    if len(tones) > 1:
        return None
    return tones[0] if tones else 'B'


def _tokens(line):
    # Punctuation separates candidates. Symbols/numbers remain visible, uncertain.
    separated = ''.join(' ' if ud.category(c).startswith('P') else c for c in line)
    result = []
    for token in separated.split():
        tone = tone_class(token)
        uncertainties = ['language_and_single_tieng_unverified']
        if tone is None:
            uncertainties.append('unsupported_or_ambiguous_token')
        if token.isascii():
            uncertainties.append('unaccented_latin_or_number_ambiguous')
        result.append({'text': token, 'tone_class': tone, 'uncertainties': uncertainties})
    return result


def analyze(text):
    """Analyze a str without changing it. Raise ValueError for empty/control input."""
    if not isinstance(text, str):
        raise ValueError('Input must be Unicode text decoded from UTF-8.')
    if any(ud.category(c).startswith('C') and c not in '\n\r\t' for c in text):
        raise ValueError('Unsupported control or format character in input.')
    normalized = ud.normalize('NFC', text)
    lines = []
    for source_number, raw in enumerate(normalized.splitlines(), 1):
        tokens = _tokens(raw)
        if not tokens:
            continue
        expected = 6 if len(lines) % 2 == 0 else 8
        checks = []
        for position in range(2, expected + 1, 2):
            target = 'T' if position == 4 else 'B'
            actual = tokens[position-1]['tone_class'] if position <= len(tokens) else None
            checks.append({'position': position, 'expected': target, 'observed': actual,
                           'status': 'unknown' if actual is None else
                           ('matches_orthography' if actual == target else 'differs_orthography')})
        lines.append({'line': source_number, 'analysis_line': raw, 'tokens': tokens,
                      'candidate_count': len(tokens), 'count_is_verified': False,
                      'expected_count': expected,
                      'length_status': 'matches_candidate_count' if len(tokens) == expected else 'variation',
                      'tone_checks': checks})
    if not lines:
        raise ValueError('Input contains no tiếng candidates.')
    links = []
    for left, right in zip(lines, lines[1:]):
        p, q = (6,6) if left['expected_count'] == 6 else (8,6)
        if len(left['tokens']) >= p and len(right['tokens']) >= q:
            def endpoint(line, pos):
                return {'line': line['line'], 'position': pos, 'text': line['tokens'][pos-1]['text']}
            links.append({'from': endpoint(left,p), 'to': endpoint(right,q),
                          'status': 'needs_human_review'})
    return {'original_text': text, 'analysis_text': normalized, 'lines': lines,
            'rhyme_candidates': links, 'limitations': list(LIMITATIONS)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('path', nargs='?', default='-', help='UTF-8 poem file, or - for stdin')
    parser.add_argument('--json', action='store_true', help='emit structured diagnostics including exact original text')
    args = parser.parse_args()
    try:
        raw = sys.stdin.buffer.read() if args.path == '-' else safe_path(args.path).read_bytes()
        report = analyze(raw.decode('utf-8'))
    except (OSError, UnicodeError, ValueError, RuntimeError) as error:
        print('Error: ' + str(error), file=sys.stderr)
        return 2
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        for line in report['lines']:
            checks = ', '.join(f"{c['position']}:{c['observed'] or '?'} (expected {c['expected']})" for c in line['tone_checks'])
            print(f"Line {line['line']}: {line['candidate_count']} tiếng candidates; expected {line['expected_count']}; {checks}")
        print('\nRhyme candidates, all needing human review:')
        for link in report['rhyme_candidates']:
            print(f"  {link['from']} -> {link['to']}")
        print('\nLimitations:\n' + '\n'.join('- '+x for x in report['limitations']))
        print('\nExact original text is retained in --json output.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
