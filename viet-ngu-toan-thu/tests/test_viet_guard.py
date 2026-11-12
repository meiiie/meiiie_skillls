import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
import unicodedata

SCRIPT = Path(__file__).resolve().parents[1] / 'scripts' / 'viet_guard.py'

class GuardTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.before = self.root / 'before.txt'
        self.after = self.root / 'after.txt'
        self.record = self.root / 'record.json'
        self.before.write_text('Tôi thích tiếng Việt.\n', encoding='utf-8')
        self.after.write_bytes(self.before.read_bytes())
    def run_cli(self, *args):
        return subprocess.run([sys.executable, str(SCRIPT), *map(str,args)], capture_output=True, text=True, encoding='utf-8', cwd=self.root)
    def lint(self, text):
        self.before.write_text(text, encoding='utf-8')
        p=self.run_cli('lint',self.before,'--json')
        self.assertIn(p.returncode,(0,1),p.stderr)
        return json.loads(p.stdout)['diagnostics']
    def diff(self, a,b):
        self.before.write_text(a,encoding='utf-8');self.after.write_text(b,encoding='utf-8')
        p=self.run_cli('diff',self.before,self.after,'--json')
        self.assertIn(p.returncode,(0,1),p.stderr)
        return json.loads(p.stdout)
    def codes(self, items): return {x['code'] for x in items}
    def check(self,*extra):
        return self.run_cli('check',self.before,self.after,'--record',self.record,'--reviewer','Mai','--review','Đã so sánh từng câu; giữ nguyên ý.',*extra)
    def verify(self): return self.run_cli('verify',self.before,self.after,'--record',self.record)
    def test_traversal_rejected(self):
        self.assertEqual(self.run_cli('lint','../'+self.root.name+'/before.txt').returncode,2)
    def test_absolute_outside_rejected(self):
        with tempfile.TemporaryDirectory() as other:
            p=Path(other)/'public.txt';p.write_text('Đúng.');self.assertEqual(self.run_cli('lint',p).returncode,2)
    def test_symlink_escape_rejected(self):
        with tempfile.TemporaryDirectory() as other:
            p=Path(other)/'public.txt';p.write_text('Đúng.');link=self.root/'link.txt';link.symlink_to(p);self.assertEqual(self.run_cli('lint',link).returncode,2)
    def test_dotfile_rejected(self):
        p=self.root/'.hidden';p.write_text('Đúng.');self.assertEqual(self.run_cli('lint',p).returncode,2)
    def test_dotdir_rejected(self):
        p=self.root/'.private';p.mkdir();(p/'text').write_text('Đúng.');self.assertEqual(self.run_cli('lint',p/'text').returncode,2)
    def test_valid_nested(self):
        p=self.root/'nested';p.mkdir();(p/'text').write_text('Đúng.');self.assertEqual(self.run_cli('lint','nested/text').returncode,0)
    def test_absolute_within_root(self): self.assertEqual(self.run_cli('lint',self.before).returncode,0)
    def test_record_outside_rejected(self):
        with tempfile.TemporaryDirectory() as other:
            p=Path(other)/'record.json';self.assertEqual(self.check('--record',p).returncode,2);self.assertFalse(p.exists())
    def test_record_symlink_escape_rejected(self):
        with tempfile.TemporaryDirectory() as other:
            p=Path(other)/'record.json';link=self.root/'link.json';link.symlink_to(p);self.assertEqual(self.check('--record',link).returncode,2);self.assertFalse(p.exists())
    def test_record_symlink_parent_escape_rejected(self):
        with tempfile.TemporaryDirectory() as other:
            link=self.root/'linked';link.symlink_to(other,target_is_directory=True);self.assertEqual(self.check('--record',link/'record.json').returncode,2)
    def test_record_dotfile_rejected(self): self.assertEqual(self.check('--record',self.root/'.record').returncode,2)
    def test_directory_rejected(self): self.assertEqual(self.run_cli('lint',self.root).returncode,2)
    def test_symlink_hidden_target_rejected(self):
        p=self.root/'.hidden';p.write_text('Đúng.');link=self.root/'visible';link.symlink_to(p);self.assertEqual(self.run_cli('lint',link).returncode,2)
    def test_canonical_semantic_tokens(self):
        a='Tôi không có thể trả 12 đồng.';b=unicodedata.normalize('NFD',a)
        d=self.diff(a,b);self.assertTrue(d['changed']);self.assertEqual(d['risks'],[])
    def test_textual_diff_changed_names(self):
        d=self.diff('Lan trả 12 đồng.','Mai trả 12 đồng.')
        self.assertEqual(d['risks'],[]);self.assertIn('-Lan trả 12 đồng.',d['unified_diff']);self.assertIn('+Mai trả 12 đồng.',d['unified_diff'])
    def test_textual_diff_identical(self): self.assertEqual(self.diff('Đúng.','Đúng.')['unified_diff'],'')
    def test_nfc_location(self):
        d=self.lint('Đúng rồi.\nSai: a\u0301.')[0];self.assertEqual((d['line'],d['column']),(2,6))
    def test_codepoint_column(self):
        d=self.lint('😀 é  x')[0];self.assertEqual((d['line'],d['column']),(1,4))
    def test_diff_unicode_separator_is_not_lf(self):
        d=self.diff('A\u2028B\n','A\u2028C\n')['unified_diff']
        self.assertIn('@@ -1 +1 @@',d);self.assertNotIn('No newline',d)
    def test_diff_crlf_preserved(self):
        d=self.diff('A\r\n','B\r\n')['unified_diff']
        self.assertIn('-A\r\n',d);self.assertIn('+B\r\n',d);self.assertNotIn('No newline',d)
    def test_diff_no_final_newline(self):
        d=self.diff('A','B')['unified_diff'];self.assertEqual(d.count('No newline at end of file'),2)
    def test_clean(self): self.assertEqual(self.lint('Tiếng Việt rất đẹp.\n'),[])
    def test_nfc(self): self.assertIn('unicode_nfc',self.codes(self.lint('Tiếng Việt')))
    def test_zero_width(self): self.assertIn('zero_width',self.codes(self.lint('Vi\u200bệt')))
    def test_spaces(self): self.assertIn('repeated_spaces',self.codes(self.lint('Tôi  đọc.')))
    def test_punctuation(self): self.assertIn('space_before_punctuation',self.codes(self.lint('Xin chào , bạn.')))
    def test_inline_code(self): self.assertEqual(self.lint('Mã `a  , b\u200b`.'),[])
    def test_fenced_code(self): self.assertEqual(self.lint('```python\na  , b\u200b\n```\n'),[])
    def test_tilde_code(self): self.assertEqual(self.lint('~~~\na  , b\u200b\n~~~'),[])
    def test_url(self): self.assertEqual(self.lint('Xem https://example.org/a?x=1,2.'),[])
    def test_decimal(self): self.assertEqual(self.lint('Giá 1.234,50 đồng; tỷ lệ 3,14.'),[])
    def test_date(self): self.assertEqual(self.lint('Ngày 11/11/2026.'),[])
    def test_abbreviation(self): self.assertEqual(self.lint('TS. Lan ở TP.HCM.'),[])
    def test_indent(self): self.assertEqual(self.lint('  Một đoạn văn.\n'),[])
    def test_location(self):
        d=self.lint('Đúng.\nSai  rồi.')[0]; self.assertEqual((d['line'],d['column']),(2,4))
    def test_number_risk(self): self.assertIn('numbers_changed',self.codes(self.diff('Có 12 người.','Có 13 người.')['risks']))
    def test_negation_risk(self): self.assertIn('negation_changed',self.codes(self.diff('Tôi đồng ý.','Tôi không đồng ý.')['risks']))
    def test_modality_risk(self): self.assertIn('modality_changed',self.codes(self.diff('Bạn có thể đi.','Bạn phải đi.')['risks']))
    def test_causality_risk(self): self.assertIn('causality_changed',self.codes(self.diff('A và B.','A vì B.')['risks']))
    def test_attribution_risk(self): self.assertIn('attribution_changed',self.codes(self.diff('Theo Lan, trời đẹp.','Trời đẹp.')['risks']))
    def test_code_risk(self): self.assertIn('protected_changed',self.codes(self.diff('Dùng `a`','Dùng `b`')['risks']))
    def test_url_risk(self): self.assertIn('protected_changed',self.codes(self.diff('https://a.test','https://b.test')['risks']))
    def test_no_substring_negation(self): self.assertNotIn('negation_changed',self.codes(self.diff('Không khí tốt.','Không khí trong lành.')['risks']))
    def test_human_review(self): self.assertTrue(self.diff('Tôi thích trà.','Tôi thích cà phê.')['human_review_required'])
    def test_unchanged(self): self.assertEqual(self.diff('Không có 12 người.','Không có 12 người.')['risks'],[])
    def test_no_mutation(self):
        data=b'a  , b\r\n'; self.before.write_bytes(data); self.run_cli('lint',self.before); self.assertEqual(self.before.read_bytes(),data)
    def test_record_valid(self): self.assertEqual(self.check().returncode,0);self.assertEqual(self.verify().returncode,0)
    def test_review_required(self): self.assertEqual(self.run_cli('check',self.before,self.after,'--record',self.record).returncode,2)
    def test_review_nonempty(self): self.assertEqual(self.check('--review','  ').returncode,2)
    def test_reviewer_nonempty(self): self.assertEqual(self.check('--reviewer','  ').returncode,2)
    def test_stale(self): self.check();self.after.write_text('Thay đổi',encoding='utf-8');self.assertEqual(self.verify().returncode,1)
    def test_newlines(self): self.check();self.after.write_bytes(self.after.read_bytes().replace(b'\n',b'\r\n'));self.assertEqual(self.verify().returncode,1)
    def test_swapped(self):
        self.after.write_text('Khác.',encoding='utf-8');self.check();self.assertEqual(self.run_cli('verify',self.after,self.before,'--record',self.record).returncode,1)
    def test_tamper_review(self):
        self.check();d=json.loads(self.record.read_text());d['review']='changed';self.record.write_text(json.dumps(d));self.assertEqual(self.verify().returncode,1)
    def test_tamper_diagnostics(self):
        self.check();d=json.loads(self.record.read_text());d['diagnostics']=['fake'];self.record.write_text(json.dumps(d));self.assertEqual(self.verify().returncode,1)
    def test_schema(self):
        self.check();d=json.loads(self.record.read_text());d['schema_version']=999;self.record.write_text(json.dumps(d));self.assertEqual(self.verify().returncode,1)
    def test_schema_boolean(self):
        self.check();d=json.loads(self.record.read_text());d['schema_version']=True;self.record.write_text(json.dumps(d));self.assertEqual(self.verify().returncode,1)
    def test_unclosed_fence(self): self.assertEqual(self.lint('```python\na  , b\u200b'),[])
    def test_multibacktick_inline(self): self.assertEqual(self.lint('Dùng ``a `  , b``.'),[])
    def test_empty_file(self): self.assertEqual(self.lint(''),[])
    def test_unicode_bom(self): self.assertIn('zero_width',self.codes(self.lint('\ufeffTiếng Việt.')))
    def test_number_preserved(self): self.assertNotIn('numbers_changed',self.codes(self.diff('Có 1.234,50 đồng.','Số tiền là 1.234,50 đồng.')['risks']))
    def test_protected_numbers(self): self.assertNotIn('numbers_changed',self.codes(self.diff('`v1`','`v2`')['risks']))
    def test_invalid_utf8(self): self.before.write_bytes(b'\xff');self.assertEqual(self.run_cli('lint',self.before).returncode,2)
    def test_missing(self): self.assertEqual(self.run_cli('lint',self.root/'missing').returncode,2)
    def test_invalid_record(self): self.record.write_text('{');self.assertEqual(self.verify().returncode,1)
    def test_same_input_record_refused(self): self.assertEqual(self.run_cli('check',self.before,self.after,'--record',self.before,'--review','checked','--reviewer','Mai').returncode,2)
    def test_deterministic(self): self.check();first=self.record.read_bytes();self.check();self.assertEqual(first,self.record.read_bytes())
    def test_changed_clean_requires_review(self): self.assertEqual(self.diff('Trà.','Cà phê.')['changed'],True)

if __name__ == '__main__': unittest.main()
