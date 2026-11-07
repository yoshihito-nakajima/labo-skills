from pathlib import Path
import os
import subprocess
import sys
import tempfile
import unittest

SCRIPTS = Path(__file__).resolve().parents[1] / 'scripts'


class PublicationTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory(prefix='publication-test-')
        self.addCleanup(temp.cleanup)
        self.area = Path(temp.name).resolve()
        self.root = self.area / 'policy with spaces'
        self.root.mkdir()
        self.git('init', '-q')
        self.git('config', 'user.name', 'Synthetic Reviewer')
        self.git('config', 'user.email', 'fixture@example.invalid')
        self.save('README.md', 'Fictional policy fixture\n')
        self.base = self.git('rev-parse', 'HEAD').stdout.strip()
        self.remote = self.area / 'receiver.git'
        subprocess.run(['git', 'init', '--bare', '-q', str(self.remote)], check=True)

    def git(self, *args, ok=True):
        return subprocess.run(['git', '-C', str(self.root), *args], text=True,
                              capture_output=True, check=ok)

    def guard(self, mode, *args, data=None, ok=True, script='publication_guard.py'):
        flag = '--workspace' if script == 'reference_privacy.py' else '--repo'
        return subprocess.run([sys.executable, str(SCRIPTS / script), mode, flag,
                               str(self.root), *args], text=True, input=data,
                              capture_output=True, check=ok)

    def save(self, path, content):
        target = self.root / path
        target.parent.mkdir(parents=True, exist_ok=True)
        if isinstance(content, bytes):
            target.write_bytes(content)
        else:
            target.write_text(content)
        self.git('add', '--', path)
        self.git('commit', '-qm', 'Synthetic fixture update')

    def install(self, role='policy'):
        self.guard('install', '--role', role)

    def review(self):
        self.guard('review', '--base', self.base, '--destination', str(self.remote),
                   '--content-reviewed')

    def push(self):
        return self.git('push', str(self.remote), 'HEAD:refs/heads/topic', ok=False)

    def refs(self):
        return subprocess.check_output(['git', '--git-dir', str(self.remote),
                                        'show-ref'], text=True) if (self.remote / 'refs/heads/topic').exists() else ''

    def test_reviewed_push_succeeds_but_changed_head_and_destination_fail(self):
        self.install()
        self.save('skills/example/references/generic.md', 'Generic fictional guidance\n')
        self.assertNotEqual(self.push().returncode, 0)
        self.review()
        self.assertEqual(self.push().returncode, 0)
        before = self.refs()
        oid = self.git('rev-parse', 'HEAD').stdout.strip()
        data = f'refs/heads/main {oid} refs/heads/topic {self.base}\n'
        self.assertNotEqual(self.guard('check-push', '--destination', '/different', data=data, ok=False).returncode, 0)
        self.save('scripts/example.py', 'print("fictional")\n')
        self.assertNotEqual(self.push().returncode, 0)
        self.assertEqual(before, self.refs())

    def test_parent_local_commits_work_but_all_pushes_fail(self):
        self.install('local-only')
        self.save('research/fictional-progress.md', 'Synthetic local progress\n')
        self.assertNotEqual(self.push().returncode, 0)
        for data in ('', f'refs/heads/gone {"0" * 40} refs/heads/gone {self.base}\n',
                     f'refs/tags/v1 {self.base} refs/tags/v1 {"0" * 40}\n'):
            result = self.guard('check-push', '--destination', str(self.remote), data=data, ok=False)
            self.assertIn('local-only', result.stderr)
            self.assertNotEqual(result.returncode, 0)
        self.assertEqual('', self.refs())

    def test_add_then_remove_is_rejected(self):
        self.save('reference/fictional.txt', 'Synthetic source\n')
        self.git('rm', 'reference/fictional.txt')
        self.git('commit', '-qm', 'Remove synthetic source')
        result = self.guard('check', '--base', self.base, ok=False)
        self.assertIn('non-policy path', result.stderr)

    def test_replacement_objects_cannot_hide_sent_private_history(self):
        self.install()
        self.save('research/fictional-private.txt', 'Synthetic private object\n')
        private = self.git('rev-parse', 'HEAD').stdout.strip()
        tree = self.git('rev-parse', self.base + '^{tree}').stdout.strip()
        clean = self.git('commit-tree', tree, '-p', self.base, '-m', 'Synthetic clean view').stdout.strip()
        self.git('replace', private, clean)
        self.assertNotEqual(self.guard('review', '--base', self.base, '--destination',
                            str(self.remote), '--content-reviewed', ok=False).returncode, 0)
        self.assertNotEqual(self.push().returncode, 0)
        self.assertEqual('', self.refs())

    def test_grafts_and_shallow_history_are_rejected(self):
        self.save('scripts/example.py', 'print("synthetic")\n')
        tip = self.git('rev-parse', 'HEAD').stdout.strip()
        grafts = self.root / '.git/info/grafts'
        grafts.write_text(tip + '\n')
        result = self.guard('check', '--base', self.base, ok=False)
        self.assertIn('grafts', result.stderr)
        grafts.unlink()
        (self.root / '.git/shallow').write_text(self.base + '\n')
        result = self.guard('check', '--base', self.base, ok=False)
        self.assertIn('complete history', result.stderr)

    def test_binary_lfs_and_symlink_are_rejected(self):
        for path, content in [('tests/image.pdf', b'fake'),
                              ('skills/example/data.txt', b'\x00binary'),
                              ('tests/pointer.txt', 'version https://git-lfs.github.com/spec/v1\n')]:
            with self.subTest(path=path):
                base = self.git('rev-parse', 'HEAD').stdout.strip()
                self.save(path, content)
                self.assertNotEqual(self.guard('check', '--base', base, ok=False).returncode, 0)
        base = self.git('rev-parse', 'HEAD').stdout.strip()
        (self.root / 'tests/link').symlink_to('../README.md')
        self.git('add', 'tests/link')
        self.git('commit', '-qm', 'Synthetic link')
        self.assertNotEqual(self.guard('check', '--base', base, ok=False).returncode, 0)

    def test_intermediate_merged_branch_is_inspected(self):
        main = self.git('branch', '--show-current').stdout.strip()
        self.git('checkout', '-qb', 'side')
        self.save('writing/fictional.txt', 'Synthetic private work\n')
        self.git('rm', 'writing/fictional.txt')
        self.git('commit', '-qm', 'Remove fictional work')
        self.git('checkout', main)
        self.save('README.md', 'Fictional main update\n')
        self.git('merge', '--no-ff', 'side', '-m', 'Synthetic merge')
        self.assertNotEqual(self.guard('check', '--base', self.base, ok=False).returncode, 0)

    def test_only_exact_generic_layout_templates_are_allowed(self):
        prefix = 'skills/labo-layout/assets/writing/.corpus/'
        for name in ('README.md', 'index.md'):
            self.save(prefix + name, 'Generic fictional template guidance\n')
        self.assertEqual(self.guard('check', '--base', self.base).returncode, 0)
        for path in (prefix + 'notes.md', prefix + 'source.pdf',
                     'writing/.corpus/README.md',
                     'skills/other/assets/writing/.corpus/index.md'):
            with self.subTest(path=path):
                base = self.git('rev-parse', 'HEAD').stdout.strip()
                self.save(path, 'Fictional private source\n')
                result = self.guard('check', '--base', base, ok=False)
                self.assertNotEqual(result.returncode, 0)
                self.assertIn('non-policy path', result.stderr)

    def test_template_exception_keeps_blob_and_file_type_checks(self):
        prefix = 'skills/labo-layout/assets/writing/.corpus/'
        self.save(prefix + 'README.md', b'\x00fictional binary')
        result = self.guard('check', '--base', self.base, ok=False)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('binary', result.stderr)
        base = self.git('rev-parse', 'HEAD').stdout.strip()
        (self.root / prefix / 'index.md').symlink_to('README.md')
        self.git('add', prefix + 'index.md')
        self.git('commit', '-qm', 'Synthetic template symlink')
        result = self.guard('check', '--base', base, ok=False)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('non-regular', result.stderr)

    @unittest.skipIf(sys.platform == "win32", "executes POSIX sh hook directly")
    def test_preserves_existing_hook_stdin_args_and_exit_code(self):
        hook = self.root / '.git/hooks/pre-push'
        hook.write_text('#!/bin/sh\ncat > received-input\nprintf "%s\\n" "$@" > received-args\nexit 17\n')
        hook.chmod(0o755)
        self.install()
        self.install()
        self.review()
        data = f'refs/heads/main {self.base} refs/heads/topic {"0" * 40}\n'
        result = subprocess.run([str(hook), 'origin', str(self.remote)], cwd=self.root,
                                input=data, text=True, capture_output=True)
        self.assertEqual(result.returncode, 17)
        self.assertEqual((self.root / 'received-input').read_text(), data)
        self.assertEqual((self.root / 'received-args').read_text(), f'origin\n{self.remote}\n')

    def test_backup_collision_and_symlink_preserve_hook(self):
        hook = self.root / '.git/hooks/pre-push'
        original = '#!/bin/sh\nexit 0\n'
        hook.write_text(original)
        hook.chmod(0o755)
        backup = hook.with_name('pre-push.before-publication-guard')
        backup.write_text('prior backup')
        self.assertNotEqual(self.guard('install', '--role', 'policy', ok=False).returncode, 0)
        self.assertEqual(hook.read_text(), original)
        backup.unlink()
        backup.symlink_to(self.root / 'README.md')
        self.assertNotEqual(self.guard('install', '--role', 'policy', ok=False).returncode, 0)
        self.assertEqual(hook.read_text(), original)

    def test_empty_custom_hooks_path_cannot_disable_an_installed_guard_silently(self):
        self.git('config', 'core.hooksPath', '')
        result = self.guard('install', '--role', 'local-only', ok=False)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('custom core.hooksPath', result.stderr)
        self.assertFalse((self.root / '.git/hooks/pre-push').exists())
        import json
        status = json.loads(self.guard('status').stdout)
        self.assertTrue(status['custom_hooks_path_configured'])
        self.assertEqual(status['hooksPath'], '')

    def test_reference_compatibility_in_both_install_orders(self):
        self.save('.gitignore', '/local/\n/reference/\n/writing/.corpus/\n')
        self.guard('install', '--baseline', self.base, script='reference_privacy.py')
        self.install('local-only')
        self.guard('check-local', script='reference_privacy.py')
        self.assertNotEqual(self.push().returncode, 0)
        # Refresh must retain the local-only role and exact reference hooks.
        self.guard('refresh', script='reference_privacy.py')
        self.guard('check-local', script='reference_privacy.py')
        self.assertNotEqual(self.push().returncode, 0)

    def test_reference_installed_after_local_guard(self):
        self.install('local-only')
        self.save('.gitignore', '/local/\n/reference/\n/writing/.corpus/\n')
        self.guard('install', '--baseline', self.base, script='reference_privacy.py')
        self.guard('check-local', script='reference_privacy.py')
        self.assertNotEqual(self.push().returncode, 0)

    def test_worktree_review_and_alias_from_outside_repository(self):
        self.install()
        other = self.area / 'contribution'
        self.git('worktree', 'add', '-qb', 'contribution', str(other), self.base)
        self.root = other
        self.save('skills/example/SKILL.md', 'Synthetic skill\n')
        alias = self.area / '.claude'
        alias.symlink_to(SCRIPTS.parent, target_is_directory=True)
        subprocess.run([sys.executable, str(alias / 'scripts/publication_guard.py'),
                        'review', '--repo', str(other), '--base', self.base,
                        '--destination', str(self.remote), '--content-reviewed'],
                       cwd=self.area, check=True, capture_output=True)
        self.assertEqual(self.push().returncode, 0)


if __name__ == '__main__':
    unittest.main()
