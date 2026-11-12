# Poetry fixtures below are original synthetic test lines, not corpus quotations.
import importlib.util
import json
from pathlib import Path
import subprocess
import tempfile
import os
import sys
import unittest
import unicodedata

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE.parent / 'scripts'))
SPEC = importlib.util.find_spec('luc_bat')
if SPEC:
    from luc_bat import analyze, tone_class


class DiagnosticsTests(unittest.TestCase):
    def setUp(self):
        self.assertIsNotNone(SPEC, 'Diagnostic module must exist before behavior can pass')

    def test_punctuation_counts_and_original(self):
        text = '“Sớm mai, bà vá lưới thưa!”\r\nKim tre kéo sợi nắng vừa qua tay.\r\n'
        report = analyze(text)
        self.assertEqual(report['original_text'], text)
        self.assertEqual([x['candidate_count'] for x in report['lines']], [6, 8])
        self.assertEqual(report['lines'][0]['tokens'][0]['text'], 'Sớm')

    def test_decomposed_unicode_normalizes_only_analysis(self):
        text = unicodedata.normalize('NFD', 'Sớm mai bà vá lưới thưa')
        report = analyze(text)
        self.assertEqual(report['original_text'], text)
        self.assertEqual(report['analysis_text'], 'Sớm mai bà vá lưới thưa')
        self.assertEqual(report['lines'][0]['candidate_count'], 6)

    def test_all_tones(self):
        for token, want in [('ma','B'), ('mà','B'), ('má','T'), ('mả','T'), ('mã','T'), ('mạ','T'), ('ĐỜI','B')]:
            with self.subTest(token=token):
                self.assertEqual(tone_class(token), want)

    def test_d_and_d_stroke_preserved(self):
        tokens = analyze('da đa dì đi')['lines'][0]['tokens']
        self.assertEqual([x['text'] for x in tokens], ['da','đa','dì','đi'])

    def test_empty_and_punctuation_rejected(self):
        for value in ['', ' \n\t', '... — !!!']:
            with self.subTest(value=value), self.assertRaises(ValueError):
                analyze(value)

    def test_control_character_rejected(self):
        with self.assertRaises(ValueError):
            analyze('xin\x00 chào')

    def test_line_length_variation_not_rewritten(self):
        report = analyze('này là ba\nnày là bốn tiếng')
        self.assertEqual([x['expected_count'] for x in report['lines']], [6,8])
        self.assertEqual([x['length_status'] for x in report['lines']], ['variation','variation'])
        self.assertEqual(report['rhyme_candidates'], [])

    def test_traditional_even_positions_and_mismatch(self):
        lines = analyze('Sớm mai bà vá lưới thưa\nKim tre kéo sợi nắng vừa qua tay')['lines']
        self.assertEqual([(x['position'],x['expected']) for x in lines[0]['tone_checks']], [(2,'B'),(4,'T'),(6,'B')])
        self.assertEqual([x['status'] for x in lines[1]['tone_checks']], ['matches_orthography']*4)
        bad = analyze('Sớm nắng bà vá lưới thưa')['lines'][0]
        self.assertEqual(bad['tone_checks'][0]['status'], 'differs_orthography')

    def test_rhyme_positions_never_certified(self):
        report = analyze('Sớm mai bà vá lưới thưa\nKim tre kéo sợi nắng vừa qua tay\nMắt thưa khép dưới bàn tay')
        links = report['rhyme_candidates']
        self.assertEqual([(x['from']['line'],x['from']['position'],x['to']['line'],x['to']['position']) for x in links], [(1,6,2,6),(2,8,3,6)])
        self.assertTrue(all(x['status']=='needs_human_review' for x in links))

    def test_numbers_multilingual_and_ascii_are_uncertain(self):
        tokens = analyze('hello 2026 世界 café năm')['lines'][0]['tokens']
        for token in tokens[:4]:
            self.assertTrue(token['uncertainties'])
        self.assertIsNone(tokens[1]['tone_class'])
        self.assertIsNone(tokens[2]['tone_class'])
        self.assertEqual(tokens[4]['tone_class'], 'B')
        self.assertFalse(analyze('hello')['lines'][0]['count_is_verified'])

    def test_regional_vocabulary_retained(self):
        text = 'Răng mô rứa hỉ ni tê'
        self.assertEqual(analyze(text)['original_text'], text)
        self.assertEqual([x['text'] for x in analyze(text)['lines'][0]['tokens']], text.split())

    def test_cli_json_stdin_and_empty_failure(self):
        run = subprocess.run([sys.executable, str(HERE.parent/'scripts'/'luc_bat.py'), '--json'], input='Sớm mai bà vá lưới thưa\r\n', text=True, capture_output=True)
        self.assertEqual(run.returncode, 0, run.stderr)
        self.assertEqual(json.loads(run.stdout)['original_text'], 'Sớm mai bà vá lưới thưa\r\n')
        bad = subprocess.run([sys.executable, str(HERE.parent/'scripts'/'luc_bat.py'), '--json'], input='', text=True, capture_output=True)
        self.assertNotEqual(bad.returncode,0)


class CliPathBoundaryTests(unittest.TestCase):
    def run_cli(self, root, path):
        return subprocess.run(
            [sys.executable, str((HERE.parent/'scripts'/'luc_bat.py').resolve()), str(path), '--json'],
            cwd=root, text=True, capture_output=True, timeout=2)

    def test_rejects_outside_hidden_traversal_and_symlink(self):
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            root = base/'workspace'
            root.mkdir()
            outside = base/'outside.txt'
            outside.write_text('Sớm mai bà vá lưới thưa', encoding='utf-8')
            (root/'poem.txt').write_bytes(outside.read_bytes())
            (root/'.hidden').mkdir()
            (root/'.hidden'/'poem.txt').write_bytes(outside.read_bytes())
            (root/'escape.txt').symlink_to(outside)
            (root/'hidden-link.txt').symlink_to(root/'.hidden'/'poem.txt')
            for target in [outside, '.hidden/poem.txt', '../outside.txt',
                           'sub/../poem.txt', 'escape.txt', 'hidden-link.txt']:
                with self.subTest(target=str(target)):
                    run = self.run_cli(root, target)
                    self.assertEqual(run.returncode, 2, run.stdout)
                    self.assertEqual(run.stdout, '')
                    self.assertNotIn('Traceback', run.stderr)
                    self.assertTrue(any(message in run.stderr for message in
                        ['current working directory', 'traversal', 'Dot-prefixed', 'dot-prefixed']), run.stderr)

    def test_rejects_non_regular_inputs_before_read(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root/'directory').mkdir()
            targets = ['directory']
            if hasattr(os, 'mkfifo'):
                os.mkfifo(root/'pipe')
                targets.append('pipe')
            if Path('/dev/null').exists():
                (root/'device').symlink_to('/dev/null')
                targets.append('device')
            for target in targets:
                with self.subTest(target=target):
                    try:
                        run = self.run_cli(root, target)
                    except subprocess.TimeoutExpired:
                        self.fail('Non-regular input was read instead of rejected: ' + target)
                    self.assertEqual(run.returncode, 2)
                    self.assertEqual(run.stdout, '')
                    self.assertTrue('regular file' in run.stderr or 'escapes' in run.stderr, run.stderr)

    def test_rejects_symlink_loop_without_traceback(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root/'loop.txt').symlink_to('loop.txt')
            run = self.run_cli(root, 'loop.txt')
            self.assertEqual(run.returncode, 2, run.stderr)
            self.assertEqual(run.stdout, '')
            self.assertNotIn('Traceback', run.stderr)

    def test_accepts_relative_absolute_and_in_scope_symlink(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            poem = 'Sớm mai bà vá lưới thưa\r\n'
            (root/'poem.txt').write_bytes(poem.encode('utf-8'))
            (root/'link.txt').symlink_to(root/'poem.txt')
            for target in ['poem.txt', root/'poem.txt', 'link.txt']:
                with self.subTest(target=str(target)):
                    run = self.run_cli(root, target)
                    self.assertEqual(run.returncode, 0, run.stderr)
                    self.assertEqual(json.loads(run.stdout)['original_text'], poem)

if __name__ == '__main__':
    unittest.main()
