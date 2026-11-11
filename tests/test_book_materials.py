"""Synthetic checks for the workspace-internal and external local-only book-materials workflow."""

from pathlib import Path
import subprocess
import os
import sys
import tempfile
import unittest


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "book_materials.py"


class BookMaterialsTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.base = Path(temp.name)
        self.workspace = self.base / "workspace"
        self.workspace.mkdir()
        self.root = self.base / "books"

    def call(self, mode, *extra, script=SCRIPT):
        return subprocess.run(
            [sys.executable, str(script), mode, "--root", str(self.root),
             "--workspace", str(self.workspace), *extra],
            cwd=self.base, text=True, capture_output=True,
        )

    def test_materials_only_git_and_url_push_denied(self):
        self.assertEqual(self.call("install").returncode, 0)
        self.assertFalse((self.root / ".git").exists())
        gitroot = self.root / "materials"
        self.assertTrue((gitroot / ".git").is_dir())
        self.assertEqual(self.call("check").returncode, 0)
        self.assertFalse(subprocess.check_output(["git", "-C", str(gitroot), "remote"]).strip())
        self.assertEqual((gitroot / ".git/info/attributes").read_text(), "* -filter\n")
        original = self.root / "originals" / "fictional.pdf"
        original.parent.mkdir()
        original.write_bytes(b"synthetic source bytes")
        outside_add = subprocess.run(["git", "-C", str(gitroot), "add", "../originals/fictional.pdf"], capture_output=True)
        self.assertNotEqual(outside_add.returncode, 0)
        (gitroot / "fixture.txt").write_text("fictional mathematics")
        for key, value in (("user.name", "Synthetic"), ("user.email", "test@example.invalid")):
            subprocess.run(["git", "-C", str(gitroot), "config", key, value], check=True)
        subprocess.run(["git", "-C", str(gitroot), "add", "fixture.txt"], check=True)
        subprocess.run(["git", "-C", str(gitroot), "commit", "-qm", "fixture"], check=True)
        receiver = self.base / "receiver.git"
        subprocess.run(["git", "init", "--bare", "-q", str(receiver)], check=True)
        pushed = subprocess.run(["git", "-C", str(gitroot), "push", str(receiver), "HEAD:refs/heads/main"], capture_output=True)
        self.assertNotEqual(pushed.returncode, 0)
        self.assertIn(b"all pushes are prohibited", pushed.stderr)
        self.assertEqual(subprocess.run(["git", "--git-dir", str(receiver), "show-ref"], capture_output=True).returncode, 1)

    def test_reject_parent_git_and_symlink_escape(self):
        parent = self.base / "sendable"
        parent.mkdir()
        subprocess.run(["git", "init", "-q", str(parent)], check=True)
        self.root = parent / "books"
        self.assertNotEqual(self.call("install").returncode, 0)
        self.assertFalse(self.root.exists())
        self.root = self.base / "books"
        self.assertEqual(self.call("install").returncode, 0)
        (self.root / "materials/courses").symlink_to(self.base, target_is_directory=True)
        self.assertNotEqual(self.call("check").returncode, 0)

    def test_reject_symlinked_output_and_preserve_external_target(self):
        self.assertEqual(self.call("install").returncode, 0)
        folder = self.root / "materials/courses/sample"
        folder.mkdir(parents=True)
        (folder / "main.tex").write_text("\\documentclass{article}\n\\begin{document}X\\end{document}\n")
        output = self.root / "output"
        output.mkdir(exist_ok=True)
        outside = self.base / "outside.pdf"
        outside.write_bytes(b"untouched")
        (output / "sample.pdf").symlink_to(outside)
        self.assertNotEqual(self.call("build", "--course", "sample").returncode, 0)
        self.assertEqual(outside.read_bytes(), b"untouched")

    @unittest.skipIf(sys.platform == "win32", "POSIX permission bits / shebang launcher")
    def test_check_rejects_disabled_hook_and_filter_override(self):
        self.assertEqual(self.call("install").returncode, 0)
        hook = self.root / "materials/.git/hooks/pre-push"
        original = hook.read_text()
        hook.chmod(0o644)
        self.assertNotEqual(self.call("check").returncode, 0)
        hook.chmod(0o755)
        hook.write_text(original.replace("exit 1", "exit 0"))
        self.assertNotEqual(self.call("check").returncode, 0)
        hook.write_text(original)
        attrs = self.root / "materials/.git/info/attributes"
        attrs.write_text("* -filter\n* filter=external\n")
        self.assertNotEqual(self.call("check").returncode, 0)

    def test_equivalent_root_alias_is_accepted(self):
        self.assertEqual(self.call("install").returncode, 0)
        self.root = self.root / ".." / "books"
        self.assertEqual(self.call("check").returncode, 0)

    def test_outside_cwd_and_both_mounted_launcher_names(self):
        host = self.base / "host"
        host.mkdir()
        policy = SCRIPT.parents[1]
        (host / ".agents").symlink_to(policy, target_is_directory=True)
        (host / ".claude").symlink_to(policy, target_is_directory=True)
        self.assertEqual(self.call("install", script=host / ".agents/scripts/book_materials.py").returncode, 0)
        self.assertEqual(self.call("check", script=host / ".claude/scripts/book_materials.py").returncode, 0)

    def parent_git(self, *args, check=True):
        return subprocess.run(["git", "-C", str(self.workspace), *args],
                              capture_output=True, text=True, check=check)

    def guarded_parent(self):
        self.parent_git("init", "-q")
        self.parent_git("config", "user.name", "Synthetic")
        self.parent_git("config", "user.email", "test@example.invalid")
        (self.workspace / ".gitignore").write_text("/local/\n")
        self.parent_git("add", ".gitignore")
        self.parent_git("commit", "-qm", "fictional baseline")
        baseline = self.parent_git("rev-parse", "HEAD").stdout.strip()
        guard = SCRIPT.with_name("reference_privacy.py")
        result = subprocess.run([sys.executable, str(guard), "install", "--workspace",
                                 str(self.workspace), "--baseline", baseline], capture_output=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        return baseline

    def test_internal_default_needs_effective_parent_protection(self):
        self.root = self.workspace / "local"
        self.assertNotEqual(self.call("install").returncode, 0)
        self.assertFalse(self.root.exists())
        self.guarded_parent()
        # Default location works even from an unrelated cwd, under both mounts.
        host = self.base / "mounted"
        host.mkdir()
        for mount in (".agents", ".claude"):
            (host / mount).symlink_to(SCRIPT.parents[1], target_is_directory=True)
        installed = subprocess.run([sys.executable, str(host / ".agents/scripts/book_materials.py"),
                                    "install", "--workspace", str(self.workspace)], cwd=self.base, capture_output=True)
        self.assertEqual(installed.returncode, 0, installed.stderr)
        self.assertEqual(self.call("check", script=host / ".claude/scripts/book_materials.py").returncode, 0)
        self.assertTrue((self.root / "materials/.git").is_dir())
        self.assertFalse((self.root / ".git").exists())
        (self.root / "materials/fictional-source.txt").write_text("fictional local source")
        self.parent_git("add", ".")
        self.assertEqual(self.parent_git("diff", "--cached", "--name-only").stdout, "")
        (self.workspace / ".git/hooks/labo-reference-guard.py").write_text("# stale runtime")
        self.assertNotEqual(self.call("check").returncode, 0)

    def test_git_free_projects_preserve_existing_courses_and_ignore_originals(self):
        self.guarded_parent()
        self.root = self.workspace / "local"
        self.assertEqual(self.call("install").returncode, 0)
        legacy_config = (self.root / "materials/.git/config").read_bytes()
        for kind in ("books", "topics"):
            installed = self.call("install", "--kind", kind, "--course", "sample")
            self.assertEqual(installed.returncode, 0, installed.stderr)
            project = self.root / kind / "sample"
            self.assertTrue((project / "START_HERE.md").is_file())
            self.assertFalse((project / ".git").exists())
            (project / "main.tex").write_text("\\documentclass{book}\n\\begin{document}Fictional.\\end{document}\n")
            self.assertEqual(self.call("check", "--kind", kind, "--course", "sample").returncode, 0)
            dry = self.call("build", "--kind", kind, "--course", "sample", "--dry-run")
            self.assertEqual(dry.returncode, 0, dry.stderr)
            self.assertIn(f"cache/{kind}-sample", dry.stdout)
        original = self.root / "original/fictional.pdf"
        original.write_bytes(b"synthetic original")
        self.assertEqual(self.parent_git("check-ignore", str(original)).returncode, 0)
        self.parent_git("add", ".")
        self.assertEqual(self.parent_git("diff", "--cached", "--name-only").stdout, "")
        self.assertIn("/original/", (self.root / ".gitignore").read_text())
        self.assertEqual((self.root / "materials/.git/config").read_bytes(), legacy_config)
        # No source overwrite or accidental opt-in to history on repeated init.
        self.assertNotEqual(self.call("install", "--kind", "books", "--course", "sample").returncode, 0)

    def test_git_free_project_rejects_git_in_originals_and_mode_parent(self):
        self.assertEqual(self.call("install", "--kind", "topics", "--course", "sample").returncode, 0)
        original_git = self.root / "original/nested/.git"
        original_git.mkdir(parents=True)
        rejected = self.call("check", "--kind", "topics", "--course", "sample")
        self.assertNotEqual(rejected.returncode, 0)
        self.assertIn("must not own Git", rejected.stderr)
        original_git.rmdir()
        (self.root / "topics/.git").mkdir()
        self.assertNotEqual(self.call("check", "--kind", "topics", "--course", "sample").returncode, 0)

    def test_git_free_project_rejects_symlink_escape_and_slug_escape(self):
        self.root.mkdir()
        outside = self.base / "untouched"
        outside.mkdir()
        (self.root / "books").symlink_to(outside, target_is_directory=True)
        self.assertNotEqual(self.call("install", "--kind", "books", "--course", "sample").returncode, 0)
        self.assertEqual(list(outside.iterdir()), [])
        self.assertNotEqual(self.call("install", "--kind", "topics", "--course", "../escape").returncode, 0)

    def test_internal_root_refuses_alias_escape_and_arbitrary_nested_git(self):
        self.guarded_parent()
        self.root = self.workspace / "other"
        self.assertNotEqual(self.call("install").returncode, 0)
        outside = self.base / "escaped"
        outside.mkdir()
        self.root = self.workspace / "local"
        self.root.symlink_to(outside, target_is_directory=True)
        self.assertNotEqual(self.call("install").returncode, 0)
        self.assertFalse((outside / "materials").exists())

    def test_parent_forced_local_files_and_gitlink_commit_are_blocked(self):
        self.guarded_parent()
        self.root = self.workspace / "local"
        self.assertEqual(self.call("install").returncode, 0)
        (self.root / "private-instructions.md").write_text("fictional source instructions")
        self.parent_git("add", "-f", "local/private-instructions.md")
        rejected = self.parent_git("commit", "-qm", "must fail", check=False)
        self.assertNotEqual(rejected.returncode, 0)
        self.assertIn("local/", rejected.stderr)
        self.parent_git("reset", "-q")
        oid = self.parent_git("rev-parse", "HEAD").stdout.strip()
        self.parent_git("update-index", "--add", "--cacheinfo", "160000", oid, "local/materials")
        self.assertNotEqual(self.parent_git("commit", "-qm", "gitlink must fail", check=False).returncode, 0)

    def test_real_parent_push_rejects_local_intermediate_branch_and_tags(self):
        baseline = self.guarded_parent()
        receiver = self.base / "parent-receiver.git"
        subprocess.run(["git", "init", "--bare", "-q", str(receiver)], check=True)
        self.parent_git("push", str(receiver), "HEAD:refs/heads/main")
        self.parent_git("config", "core.hooksPath", "/dev/null")
        secret = self.workspace / "local/cache/fictional.txt"
        secret.parent.mkdir(parents=True)
        secret.write_text("entirely fictional source")
        self.parent_git("add", "-f", "local/cache/fictional.txt")
        self.parent_git("commit", "-qm", "fictional leak")
        self.parent_git("tag", "-am", "fictional", "leak-tag")
        self.parent_git("rm", "-r", "local")
        self.parent_git("commit", "-qm", "delete fictional leak")
        self.parent_git("tag", "-am", "clean tip with leaking history", "clean-tip-tag")
        self.parent_git("config", "--unset", "core.hooksPath")
        for ref in ("HEAD:refs/heads/main", "refs/tags/leak-tag", "refs/tags/clean-tip-tag"):
            result = self.parent_git("push", str(receiver), ref, check=False)
            self.assertNotEqual(result.returncode, 0, result.stderr)
            self.assertIn("local/", result.stderr)
        received = subprocess.check_output(["git", "--git-dir", str(receiver), "show-ref"], text=True)
        self.assertEqual(received.strip(), baseline + " refs/heads/main")
        # Refresh must not turn the new local HEAD into a trusted exception.
        guard = SCRIPT.with_name("reference_privacy.py")
        refreshed = subprocess.run([sys.executable, str(guard), "refresh", "--workspace", str(self.workspace)], capture_output=True)
        self.assertEqual(refreshed.returncode, 0, refreshed.stderr)
        for key in ("labo.referencePrivacyBaseline", "labo.corpusPrivacyBaseline"):
            self.assertEqual(self.parent_git("config", "--get", key).stdout.strip(), baseline)
        self.assertNotEqual(self.parent_git("push", str(receiver), "HEAD:refs/heads/main", check=False).returncode, 0)

    @unittest.skipIf(sys.platform == "win32", "POSIX permission bits / shebang launcher")
    def test_internal_build_keeps_outputs_and_cache_outside_child_git(self):
        self.guarded_parent()
        self.root = self.workspace / "local"
        self.assertEqual(self.call("install").returncode, 0)
        folder = self.root / "materials/courses/fictional"
        folder.mkdir(parents=True)
        (folder / "main.tex").write_text("\\documentclass{article}\n\\begin{document}Fiction\\end{document}\n")
        binary = self.base / "bin"
        binary.mkdir()
        latexmk = binary / "latexmk"
        latexmk.write_text("#!/usr/bin/env python3\nimport pathlib, sys\np = pathlib.Path(next(a.split('=', 1)[1] for a in sys.argv if a.startswith('-outdir=')))\np.mkdir(parents=True, exist_ok=True)\n(p/'main.pdf').write_bytes(b'fictional PDF')\n(p/'main.synctex.gz').write_bytes(b'fictional sync')\n")
        latexmk.chmod(0o755)
        result = subprocess.run([sys.executable, str(SCRIPT), "build", "--workspace", str(self.workspace),
                                 "--course", "fictional"], cwd=self.base,
                                env={**os.environ, "PATH": str(binary) + os.pathsep + os.environ["PATH"]}, capture_output=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual((self.root / "output/fictional.pdf").read_bytes(), b"fictional PDF")
        self.assertTrue((self.root / "output/fictional.synctex.gz").is_file())
        self.assertTrue((self.root / "cache/fictional/main.pdf").is_file())
        self.assertFalse(list((self.root / "materials").rglob("*.pdf")))
        self.parent_git("add", ".")
        self.assertEqual(self.parent_git("diff", "--cached", "--name-only").stdout, "")

    def test_stopped_migration_preserves_history_dirty_files_and_rebinds_hook(self):
        self.guarded_parent()
        self.assertEqual(self.call("install").returncode, 0)
        old_root = self.root
        child = old_root / "materials"
        def cg(*args):
            return subprocess.run(["git", "-C", str(child), *args], capture_output=True, text=True, check=True)
        cg("config", "user.name", "Synthetic")
        cg("config", "user.email", "test@example.invalid")
        source = child / "fiction.txt"
        source.write_text("fictional initial content")
        cg("add", ".")
        cg("commit", "-qm", "local fictional history")
        head = cg("rev-parse", "HEAD").stdout
        source.write_text("fictional uncommitted content")
        (child / "new.txt").write_text("fictional new untracked content")
        status = cg("status", "--porcelain=v1").stdout
        self.root = self.workspace / "local"
        self.assertNotEqual(self.call("migrate", "--from-root", str(old_root)).returncode, 0)
        self.assertTrue(old_root.exists())
        result = self.call("migrate", "--from-root", str(old_root), "--writers-stopped")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertFalse(old_root.exists())
        child = self.root / "materials"
        self.assertEqual(cg("rev-parse", "HEAD").stdout, head)
        self.assertEqual(cg("status", "--porcelain=v1").stdout, status)
        self.assertEqual((child / "fiction.txt").read_text(), "fictional uncommitted content")
        self.assertEqual((child / "new.txt").read_text(), "fictional new untracked content")
        self.assertEqual(cg("config", "--get", "core.hooksPath").stdout.strip(), str((child / ".git/hooks").resolve()))
        self.assertEqual(self.call("check").returncode, 0)


if __name__ == "__main__":
    unittest.main()
