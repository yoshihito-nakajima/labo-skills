from pathlib import Path
import os
import subprocess
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / 'scripts' / 'reference_privacy.py'


class ReferencePrivacyTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / 'workspace'
        self.root.mkdir()
        self.git('init', '-q')
        self.git('config', 'user.name', 'Synthetic Test')
        self.git('config', 'user.email', 'test@example.invalid')
        (self.root / 'safe.txt').write_text('safe')
        self.git('add', '.')
        self.git('commit', '-qm', 'baseline')
        self.base = self.git('rev-parse', 'HEAD').stdout.strip()

    def git(self, *args, check=True, data=None):
        return subprocess.run(['git', '-C', str(self.root), *args], input=data,
                              capture_output=True, text=True, check=check)

    def guard(self, mode, data=None, check=False, env=None):
        return subprocess.run([sys.executable, str(SCRIPT), mode, '--workspace',
                               str(self.root)], input=data, capture_output=True,
                              text=True, check=check, env=env)

    def install(self):
        subprocess.run([sys.executable, str(SCRIPT), 'install', '--workspace',
                        str(self.root), '--baseline', self.base], check=True,
                       capture_output=True)

    def push_input(self, oid=None):
        oid = oid or self.git('rev-parse', 'HEAD').stdout.strip()
        return f'refs/heads/main {oid} refs/heads/main {self.base}\n'

    def test_force_added_reference_is_rejected_by_real_commit(self):
        self.install()
        (self.root / '.gitignore').write_text('/reference/\n')
        (self.root / 'reference').mkdir()
        (self.root / 'reference' / 'secret.pdf').write_bytes(b'synthetic')
        self.git('add', '-f', 'reference/secret.pdf')
        self.assertNotEqual(self.git('commit', '-qm', 'must fail', check=False).returncode, 0)

    def test_intermediate_leak_rejected_even_after_tip_deletion(self):
        self.install()
        self.git('config', 'core.hooksPath', '/dev/null')  # Simulate bypass.
        (self.root / 'reference').mkdir()
        (self.root / 'reference' / 'secret').write_text('fictional')
        self.git('add', '.')
        self.git('commit', '-qm', 'leak')
        self.git('rm', '-r', 'reference')
        self.git('commit', '-qm', 'delete leak')
        self.assertNotEqual(self.guard('check-push', self.push_input()).returncode, 0)

    def test_legacy_reference_history_allowed_only_with_clean_tip(self):
        (self.root / 'reference').mkdir()
        (self.root / 'reference' / 'old').write_text('public synthetic baseline')
        self.git('add', '.')
        self.git('commit', '-qm', 'legacy public sources')
        self.base = self.git('rev-parse', 'HEAD').stdout.strip()
        self.git('rm', '-r', 'reference')
        self.git('commit', '-qm', 'separate references')
        self.install()
        self.assertEqual(self.guard('check-push', self.push_input()).returncode, 0)
        self.assertNotEqual(self.guard('check-push', self.push_input(self.base)).returncode, 0)

    def test_annotated_tag_cannot_hide_reference(self):
        self.install()
        self.git('config', 'core.hooksPath', '/dev/null')
        (self.root / 'reference').mkdir()
        (self.root / 'reference' / 'secret').write_text('fictional')
        self.git('add', '.')
        self.git('commit', '-qm', 'leak')
        self.git('tag', '-am', 'synthetic', 'leak-tag')
        tag = self.git('rev-parse', 'leak-tag').stdout.strip()
        self.assertNotEqual(self.guard('check-push', self.push_input(tag)).returncode, 0)

    @unittest.skipIf(sys.platform == "win32", "POSIX hook execution / executable bit")
    def test_existing_hook_is_chained_and_reinstall_preserves_baseline(self):
        hook = self.root / '.git' / 'hooks' / 'pre-push'
        hook.write_text('#!/bin/sh\ncat > chained-input\nexit 17\n')
        hook.chmod(0o755)
        self.install()
        self.install()
        result = subprocess.run([str(hook), 'test', '/unused'], cwd=self.root,
                                input=self.push_input(), capture_output=True, text=True)
        self.assertEqual(result.returncode, 17)
        self.assertEqual((self.root / 'chained-input').read_text(), self.push_input())

    def test_child_remote_rejected_despite_parent_hook_environment(self):
        self.install()
        child = self.root / 'reference'
        child.mkdir()
        subprocess.run(['git', '-C', str(child), 'init', '-q'], check=True)
        subprocess.run(['git', '-C', str(child), 'remote', 'add', 'forbidden',
                        'https://example.invalid/no-upload'], check=True)
        self.assertNotEqual(self.guard('check-push', self.push_input(),
            env={**os.environ, 'GIT_DIR': str(self.root / '.git')}).returncode, 0)

    def test_actual_safe_push_and_blocked_leaking_push(self):
        self.install()
        remote = Path(self.temp.name) / 'remote.git'
        subprocess.run(['git', 'init', '--bare', '-q', str(remote)], check=True)
        self.assertEqual(self.git('push', str(remote), 'HEAD:refs/heads/main', check=False).returncode, 0)
        self.git('config', 'core.hooksPath', '/dev/null')
        (self.root / 'reference').mkdir()
        (self.root / 'reference' / 'secret').write_text('fictional')
        self.git('add', '.')
        self.git('commit', '-qm', 'leak')
        self.git('config', '--unset', 'core.hooksPath')
        self.assertNotEqual(self.git('push', str(remote), 'HEAD:refs/heads/main', check=False).returncode, 0)


class CorpusPrivacyTests(ReferencePrivacyTests):
    def corpus(self, name='index.md', content='fictional private registration'):
        child = self.root / 'writing/.corpus'
        child.mkdir(parents=True, exist_ok=True)
        (child / name).write_text(content)
        return child

    def leak_then_remove(self):
        self.git('config', 'core.hooksPath', '/dev/null')
        self.corpus()
        self.git('add', '.')
        self.git('commit', '-qm', 'fictional corpus leak')
        leak = self.git('rev-parse', 'HEAD').stdout.strip()
        self.git('rm', '-r', 'writing/.corpus')
        self.git('commit', '-qm', 'remove fictional leak')
        self.git('config', '--unset', 'core.hooksPath')
        return leak

    def test_actual_parent_push_rejects_intermediate_corpus_leak(self):
        self.install()
        remote = Path(self.temp.name) / 'parent-corpus-receiver.git'
        subprocess.run(['git', 'init', '--bare', '-q', str(remote)], check=True)
        self.assertEqual(self.git('push', str(remote), 'HEAD:refs/heads/main', check=False).returncode, 0)
        self.leak_then_remove()
        result = self.git('push', str(remote), 'HEAD:refs/heads/main', check=False)
        self.assertNotEqual(result.returncode, 0)
        received = subprocess.check_output(['git', '--git-dir', str(remote), 'rev-parse', 'refs/heads/main'], text=True).strip()
        self.assertEqual(received, self.base)

    def test_force_added_corpus_commit_is_blocked(self):
        self.install()
        self.corpus()
        self.git('add', '-f', 'writing/.corpus/index.md')
        result = self.git('commit', '-qm', 'must fail', check=False)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('writing/.corpus/', result.stderr)

    def test_intermediate_corpus_leak_is_blocked(self):
        self.install()
        self.leak_then_remove()
        self.assertNotEqual(self.guard('check-push', self.push_input()).returncode, 0)

    def test_corpus_tag_and_multiple_refs_are_blocked(self):
        self.install()
        leak = self.leak_then_remove()
        self.git('tag', '-am', 'synthetic tag', 'corpus-tag', leak)
        tag = self.git('rev-parse', 'corpus-tag').stdout.strip()
        self.assertNotEqual(self.guard('check-push', self.push_input(tag)).returncode, 0)
        # A safe deletion ref cannot conceal a later leaking ref.
        data = f'refs/heads/gone {"0" * 40} refs/heads/gone {self.base}\n' + self.push_input(tag)
        self.assertNotEqual(self.guard('check-push', data).returncode, 0)

    def legacy_corpus(self):
        self.corpus(content='fictional old already remote registration')
        self.git('add', '.')
        self.git('commit', '-qm', 'verified remote corpus')
        self.base = self.git('rev-parse', 'HEAD').stdout.strip()
        (self.root / 'safe.txt').write_text('legitimate unpushed edit')
        self.git('add', 'safe.txt')
        self.git('commit', '-qm', 'inherits unchanged remote corpus')

    def test_unchanged_remote_manifest_allowed_only_with_clean_tip(self):
        self.legacy_corpus()
        inherited = self.git('rev-parse', 'HEAD').stdout.strip()
        self.git('rm', '-r', 'writing/.corpus')
        self.git('commit', '-qm', 'separate corpus')
        self.install()
        self.assertEqual(self.guard('check-push', self.push_input()).returncode, 0)
        self.assertNotEqual(self.guard('check-push', self.push_input(inherited)).returncode, 0)
        self.assertNotEqual(self.guard('check-push', self.push_input(self.base)).returncode, 0)

    def test_changed_intermediate_legacy_corpus_is_rejected(self):
        self.legacy_corpus()
        self.corpus(content='fictional new confidential data')
        self.git('add', '.')
        self.git('commit', '-qm', 'changes remote corpus')
        self.git('rm', '-r', 'writing/.corpus')
        self.git('commit', '-qm', 'clean final tree')
        self.install()
        self.assertNotEqual(self.guard('check-push', self.push_input()).returncode, 0)

    def test_additional_intermediate_legacy_file_is_rejected(self):
        self.legacy_corpus()
        self.corpus('new.pdf', 'fictional added original')
        self.git('add', '.')
        self.git('commit', '-qm', 'adds source')
        self.git('rm', '-r', 'writing/.corpus')
        self.git('commit', '-qm', 'clean final tree')
        self.install()
        self.assertNotEqual(self.guard('check-push', self.push_input()).returncode, 0)

    @unittest.skipIf(sys.platform == "win32", "POSIX hook execution / executable bit")
    def test_changed_intermediate_file_mode_is_rejected(self):
        self.legacy_corpus()
        (self.root / 'writing/.corpus/index.md').chmod(0o755)
        self.git('add', 'writing/.corpus/index.md')
        self.git('commit', '-qm', 'changes source mode')
        self.git('rm', '-r', 'writing/.corpus')
        self.git('commit', '-qm', 'clean final tree')
        self.install()
        self.assertNotEqual(self.guard('check-push', self.push_input()).returncode, 0)

    def test_missing_baseline_and_missing_runtime_fail_closed(self):
        self.install()
        self.git('config', '--unset', 'labo.corpusPrivacyBaseline')
        self.assertNotEqual(self.guard('check-push', self.push_input()).returncode, 0)
        self.assertNotEqual(self.git('commit', '--allow-empty', '-qm', 'must fail', check=False).returncode, 0)
        self.install()
        (self.root / '.git/hooks/labo-reference-guard.py').unlink()
        self.assertNotEqual(self.git('commit', '--allow-empty', '-qm', 'must fail', check=False).returncode, 0)

    def test_reference_baseline_is_not_broadened_on_reinstall(self):
        self.install()
        self.git('commit', '--allow-empty', '-qm', 'later safe commit')
        latest = self.git('rev-parse', 'HEAD').stdout.strip()
        subprocess.run([sys.executable, str(SCRIPT), 'install', '--workspace',
                        str(self.root), '--baseline', latest], check=True, capture_output=True)
        self.assertEqual(self.git('config', '--get', 'labo.referencePrivacyBaseline').stdout.strip(), self.base)
        self.assertEqual(self.git('config', '--get', 'labo.corpusPrivacyBaseline').stdout.strip(), self.base)

    def test_child_url_push_denied_and_pdf_is_actual_bytes(self):
        child = self.corpus('source.pdf', 'fictional PDF original bytes')
        (child / '.gitattributes').write_text('*.pdf filter=lfs\n')
        subprocess.run([sys.executable, str(SCRIPT), 'install-archive', '--workspace',
                        str(self.root), '--archive', 'writing/.corpus'], check=True, capture_output=True)
        def cg(*args):
            return subprocess.run(['git', '-C', str(child), *args], capture_output=True, text=True)
        cg('config', 'user.name', 'Synthetic Test')
        cg('config', 'user.email', 'test@example.invalid')
        self.assertEqual(cg('add', '.').returncode, 0)
        self.assertEqual(cg('commit', '-qm', 'local snapshot').returncode, 0)
        self.assertEqual(cg('show', 'HEAD:source.pdf').stdout, (child / 'source.pdf').read_text())
        self.assertEqual(cg('remote').stdout, '')
        remote = Path(self.temp.name) / 'corpus-receiver.git'
        subprocess.run(['git', 'init', '--bare', '-q', str(remote)], check=True)
        self.assertNotEqual(cg('push', str(remote), 'HEAD:refs/heads/main').returncode, 0)
        result = subprocess.run(['git', '--git-dir', str(remote), 'show-ref'], capture_output=True)
        self.assertEqual(result.returncode, 1)
        self.install()
        cg('remote', 'add', 'forbidden', str(remote))
        self.assertNotEqual(self.guard('check-push', self.push_input(),
            env={**os.environ, 'GIT_DIR': str(self.root / '.git')}).returncode, 0)


if __name__ == '__main__':
    unittest.main()
