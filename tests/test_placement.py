from pathlib import Path
import json
import subprocess
import sys
import tempfile
import unittest

SCRIPTS = Path(__file__).resolve().parents[1] / 'scripts'
sys.path.insert(0, str(SCRIPTS))
import placement  # noqa: E402

POLICY = {'folders': {'kept': 'local-only', 'notes': 'private-ok', 'drafts': 'private-ok'},
          'allow': ['drafts/figures/*.pdf']}


class PlacementTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory(prefix='placement-test-')
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name).resolve() / 'workspace with spaces'
        self.root.mkdir()
        self.git('init', '-q')
        self.git('config', 'user.name', 'Synthetic Reviewer')
        self.git('config', 'user.email', 'fixture@example.invalid')
        self.policy(POLICY)

    def git(self, *args):
        return subprocess.run(['git', '-C', str(self.root), *args], text=True,
                              capture_output=True, check=True)

    def policy(self, data):
        (self.root / placement.POLICY_FILE).write_text(json.dumps(data))

    def commit(self, files):
        for path, content in files.items():
            target = self.root / path
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(content if isinstance(content, bytes) else content.encode())
        self.git('add', '-A')
        self.git('commit', '-qm', 'Synthetic fixture update')

    def run_tool(self, *args):
        return subprocess.run([sys.executable, str(SCRIPTS / 'placement.py'), *args],
                              text=True, capture_output=True)

    def check(self, *extra):
        result = self.run_tool('check', '--repo', str(self.root), *extra)
        return result.returncode, json.loads(result.stdout) if result.stdout else {}

    def kinds(self, report):
        return {(f['kind'], f['path']) for f in report['findings']}

    def write_ignore(self):
        self.run_tool('gitignore', '--repo', str(self.root), '--write')

    def test_clean_workspace_passes(self):
        self.write_ignore()
        self.commit({'notes/a.md': 'text\n', 'drafts/b.tex': 'text\n'})
        code, report = self.check()
        self.assertEqual((code, report['findings'], report['local_only_not_ignored']), (0, [], []))

    def test_local_only_folder_must_be_untracked_and_ignored(self):
        self.commit({'kept/x.txt': 'private\n'})
        code, report = self.check()
        self.assertEqual(code, 1)
        self.assertIn(('tracked-in-local-only', 'kept/x.txt'), self.kinds(report))
        self.assertEqual(report['local_only_not_ignored'], ['kept'])

    def test_downloaded_originals_are_flagged(self):
        self.write_ignore()
        self.commit({'notes/source.pdf': b'%PDF-1.4', 'notes/bundle.zip': b'PK', 'notes/ok.md': 'text\n'})
        code, report = self.check()
        self.assertEqual(code, 1)
        self.assertEqual(self.kinds(report), {('blocked-type', 'notes/source.pdf'),
                                              ('blocked-type', 'notes/bundle.zip')})

    def test_oversize_text_is_flagged(self):
        self.write_ignore()
        self.commit({'drafts/huge.txt': b'x' * 6_000_000})
        code, report = self.check()
        self.assertEqual(code, 1)
        self.assertIn(('oversize', 'drafts/huge.txt'), self.kinds(report))

    def test_allow_glob_admits_own_figures_only(self):
        self.write_ignore()
        self.commit({'drafts/figures/plot.pdf': b'%PDF', 'notes/other.pdf': b'%PDF'})
        _, report = self.check()
        self.assertEqual(self.kinds(report), {('blocked-type', 'notes/other.pdf')})

    def test_range_mode_sees_only_new_commits(self):
        self.write_ignore()
        self.commit({'notes/old.txt': 'ok\n'})
        base = self.git('rev-parse', 'HEAD').stdout.strip()
        self.commit({'notes/new.txt': 'ok\n', 'notes/new_scan.pdf': b'%PDF'})
        code, report = self.check('--range', base + '..HEAD')
        self.assertEqual(code, 1)
        self.assertEqual(self.kinds(report), {('blocked-type', 'notes/new_scan.pdf')})

    def test_unclassified_top_level_is_reported_but_not_fatal(self):
        self.write_ignore()
        self.commit({'stray/a.txt': 'text\n'})
        code, report = self.check()
        self.assertEqual(code, 0)
        self.assertIn(('unclassified', 'stray/a.txt'), self.kinds(report))

    def test_there_is_no_public_kind(self):
        self.policy({'folders': {'notes': 'public'}})
        result = self.run_tool('check', '--repo', str(self.root))
        self.assertEqual(result.returncode, 2)
        self.assertIn('no public kind', result.stderr)

    def test_gitignore_block_is_idempotent_and_keeps_other_lines(self):
        (self.root / '.gitignore').write_text('*.log\n')
        self.write_ignore()
        self.write_ignore()
        text = (self.root / '.gitignore').read_text()
        self.assertEqual(text.count(placement.BEGIN), 1)
        self.assertIn('*.log', text)
        self.assertIn('/kept/', text.splitlines())
        self.assertNotIn('/notes/', text.splitlines())
        self.policy({'folders': {'kept': 'private-ok', 'other': 'local-only'}})
        self.write_ignore()
        text = (self.root / '.gitignore').read_text()
        self.assertNotIn('/kept/', text.splitlines())
        self.assertIn('/other/', text.splitlines())
        self.assertIn('*.log', text)

    def test_only_github_remotes_can_be_verified(self):
        self.assertEqual(placement.parse_github('https://github.com/owner/repo.git'), ('owner', 'repo'))
        self.assertEqual(placement.parse_github('git@github.com:owner/repo'), ('owner', 'repo'))
        result = self.run_tool('remote', '--url', 'https://example.invalid/owner/repo.git')
        self.assertEqual(result.returncode, 2)

    def test_check_never_changes_the_repository(self):
        self.commit({'notes/a.md': 'text\n'})
        before = self.git('status', '--porcelain').stdout, self.git('rev-parse', 'HEAD').stdout
        self.check()
        after = self.git('status', '--porcelain').stdout, self.git('rev-parse', 'HEAD').stdout
        self.assertEqual(before, after)


if __name__ == '__main__':
    unittest.main()
