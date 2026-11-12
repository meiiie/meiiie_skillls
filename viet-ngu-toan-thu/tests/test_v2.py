import test_viet_guard
import unittest
import json

class V2Tests(unittest.TestCase):
    setUp = test_viet_guard.GuardTests.setUp
    run_cli = test_viet_guard.GuardTests.run_cli
    lint = test_viet_guard.GuardTests.lint
    diff = test_viet_guard.GuardTests.diff
    codes = test_viet_guard.GuardTests.codes
    check = test_viet_guard.GuardTests.check
    verify = test_viet_guard.GuardTests.verify
    def config(self, data, name='terms.json'):
        p=self.root/name;p.write_text(json.dumps(data,ensure_ascii=False),encoding='utf-8');return p
    def test_frontmatter_protected(self):
        self.assertEqual(self.lint('---\nkey: a  , b\n---\nĐúng.'),[])
    def test_html_attributes_protected(self):
        self.assertEqual(self.lint('<span title="a  , b">Đúng.</span>'),[])
    def test_html_visible_text_checked(self):
        self.assertIn('repeated_spaces',self.codes(self.lint('<span>Sai  rồi.</span>')))
    def test_relative_link_destination_protected(self):
        self.assertEqual(self.lint('[Tên](../a%20b "a  , b")'),[])
    def test_relative_link_changes_flagged(self):
        self.assertIn('protected_changed',self.codes(self.diff('[Tên](a.md)','[Tên](b.md)')['risks']))
    def test_condition_change(self):
        self.assertIn('condition_changed',self.codes(self.diff('Chỉ khi mưa, tôi nghỉ.','Khi mưa, tôi nghỉ.')['risks']))
    def test_exception_change(self):
        self.assertIn('exception_changed',self.codes(self.diff('Áp dụng trừ khi hết hạn.','Áp dụng khi hết hạn.')['risks']))
    def test_quantifier_change(self):
        self.assertIn('quantifier_changed',self.codes(self.diff('Một số người đến.','Mọi người đến.')['risks']))
    def test_time_change(self):
        self.assertIn('time_changed',self.codes(self.diff('Đã gửi.','Sẽ gửi.')['risks']))
    def test_comparison_change(self):
        self.assertIn('comparison_changed',self.codes(self.diff('A hơn B.','A kém B.')['risks']))
    def test_terms_flag_and_allow(self):
        p=self.config({'allow':['đột phá'],'flag':['đột phá','tối ưu'],'protect':['Neko Core']})
        self.before.write_text('Đột phá và tối ưu.');r=self.run_cli('lint',self.before,'--terms',p)
        self.assertEqual(r.returncode,1,r.stderr);d=json.loads(r.stdout)['diagnostics'];self.assertEqual([x['term'] for x in d],['tối ưu'])
    def test_terms_no_substring(self):
        p=self.config({'flag':['ưu']});self.before.write_text('lưu lại.');self.assertEqual(self.run_cli('lint',self.before,'--terms',p).returncode,0)
    def test_protect_terms_changed(self):
        p=self.config({'protect':['Neko Core']});self.before.write_text('Dùng Neko Core.');self.after.write_text('Dùng Neko.')
        r=self.run_cli('diff',self.before,self.after,'--terms',p);self.assertEqual(r.returncode,1,r.stderr);self.assertIn('project_protected_changed',self.codes(json.loads(r.stdout)['risks']))
    def test_bad_terms_rejected(self):
        p=self.config({'flag':'not list'});self.assertEqual(self.run_cli('lint',self.before,'--terms',p).returncode,2)
    def test_terms_hidden_rejected(self):
        p=self.config({'flag':[]},'.terms.json');self.assertEqual(self.run_cli('lint',self.before,'--terms',p).returncode,2)
    def test_compose_mode_record(self):
        self.before.write_text('Viết cảnh bình minh.');self.after.write_text('Mặt trời mọc trên biển.')
        r=self.check('--mode','compose');self.assertEqual(r.returncode,0,r.stderr)
        d=json.loads(self.record.read_text());self.assertEqual(d['mode'],'compose');self.assertIsNone(d['comparison']);self.assertIn('material_sha256',d)
        self.assertEqual(self.run_cli('verify',self.before,self.after,'--record',self.record,'--mode','compose').returncode,0)
        self.assertEqual(self.verify().returncode,1)
    def test_compose_stale_material(self):
        self.check('--mode','compose');self.before.write_text('Changed request.')
        self.assertEqual(self.run_cli('verify',self.before,self.after,'--record',self.record,'--mode','compose').returncode,1)
    def test_config_bound(self):
        p=self.config({'flag':[]});self.assertEqual(self.check('--terms',p).returncode,0)
        p.write_text('{"flag": [], "allow": []}')
        self.assertEqual(self.run_cli('verify',self.before,self.after,'--record',self.record,'--terms',p).returncode,1)
    def test_strict_dispositions_missing(self):
        self.before.write_text('Sai  rồi.');self.assertEqual(self.check('--require-dispositions').returncode,2);self.assertFalse(self.record.exists())
    def test_dispositions_bound_to_finding(self):
        self.before.write_text('Sai  rồi.');self.check();d=json.loads(self.record.read_text());ids=[x['id'] for x in d['review_items']]
        p=self.config({i:{'decision':'kept','reason':'Spacing is source evidence.'} for i in ids},'reviews.json')
        r=self.check('--dispositions',p,'--require-dispositions');self.assertEqual(r.returncode,1,r.stderr)
        self.assertTrue(json.loads(self.record.read_text())['review_complete'])
        self.assertEqual(self.run_cli('verify',self.before,self.after,'--record',self.record,'--dispositions',p,'--require-dispositions').returncode,0)
        self.before.write_text('Sai  khác.');self.assertEqual(self.check('--dispositions',p,'--require-dispositions').returncode,2)
    def test_invalid_disposition(self):
        p=self.config({'unknown':{'decision':'approved','reason':'yes'}},'reviews.json');self.assertEqual(self.check('--dispositions',p).returncode,2)

    def test_record_cannot_overwrite_terms(self):
        p=self.config({'flag':[]});original=p.read_bytes()
        self.assertEqual(self.check('--terms',p,'--record',p).returncode,2)
        self.assertEqual(p.read_bytes(),original)
    def test_record_cannot_overwrite_dispositions(self):
        p=self.config({},'reviews.json');original=p.read_bytes()
        self.assertEqual(self.check('--dispositions',p,'--record',p).returncode,2)
        self.assertEqual(p.read_bytes(),original)
    def test_record_cannot_overwrite_terms_hardlink(self):
        import os
        p=self.config({'flag':[]});original=p.read_bytes();alias=self.root/'alias.json';os.link(p,alias)
        self.assertEqual(self.check('--terms',p,'--record',alias).returncode,2)
        self.assertEqual(p.read_bytes(),original)

    def test_literal_terms_do_not_execute_regex(self):
        p=self.config({'flag':['a.*b']});self.before.write_text('axxxb');self.assertEqual(self.run_cli('lint',self.before,'--terms',p).returncode,0)
    def test_allow_does_not_suppress_technical_lint(self):
        p=self.config({'allow':['Sai  rồi']});self.before.write_text('Sai  rồi');r=self.run_cli('lint',self.before,'--terms',p)
        self.assertEqual(r.returncode,1);self.assertIn('repeated_spaces',self.codes(json.loads(r.stdout)['diagnostics']))
    def test_flag_inside_code_not_reported(self):
        p=self.config({'flag':['tối ưu']});self.before.write_text('`tối ưu`');self.assertEqual(self.run_cli('lint',self.before,'--terms',p).returncode,0)
    def test_needs_author_is_not_completed(self):
        self.before.write_text('Sai  rồi.');self.check();d=json.loads(self.record.read_text())
        p=self.config({x['id']:{'decision':'needs_author','reason':'Confirm intended spacing.'} for x in d['review_items']},'reviews.json')
        self.assertEqual(self.check('--dispositions',p,'--require-dispositions').returncode,2)
    def test_terms_symlink_escape_rejected(self):
        import tempfile
        with tempfile.TemporaryDirectory() as other:
            p=__import__('pathlib').Path(other)/'terms.json';p.write_text('{}');link=self.root/'link.json';link.symlink_to(p)
            self.assertEqual(self.run_cli('lint',self.before,'--terms',link).returncode,2)
    def test_fifo_input_refused_without_blocking(self):
        import os, subprocess, sys
        p=self.root/'pipe';os.mkfifo(p)
        r=subprocess.run([sys.executable,str(test_viet_guard.SCRIPT),'lint',str(p)],cwd=self.root,capture_output=True,timeout=2)
        self.assertEqual(r.returncode,2)
    def test_fifo_record_refused_without_blocking(self):
        import os, subprocess, sys
        p=self.root/'pipe';os.mkfifo(p)
        r=subprocess.run([sys.executable,str(test_viet_guard.SCRIPT),'check',str(self.before),str(self.after),'--record',str(p),'--review','checked','--reviewer','AI'],cwd=self.root,capture_output=True,timeout=2)
        self.assertEqual(r.returncode,2)
    def test_quotes_protected(self):
        self.assertIn('protected_changed',self.codes(self.diff('Lan nói “đồng ý”.','Lan nói “từ chối”.')['risks']))
    def test_negation_moves_between_sentences(self):
        self.assertIn('sentence_scope_changed',self.codes(self.diff('Lan không đi. Minh đi.','Lan đi. Minh không đi.')['risks']))
    def test_url_sentence_punctuation_not_protected(self):
        self.assertNotIn('protected_changed',self.codes(self.diff('Xem https://example.org.','Xem https://example.org!')['risks']))
