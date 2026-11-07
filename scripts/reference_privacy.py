#!/usr/bin/env python3
"""Install or run explicit local-only source guards; never uploads data."""
import argparse
import os
from pathlib import Path
import shlex
import shutil
import subprocess
import sys


class PrivacyError(RuntimeError):
    pass


def git(root, *args, data=None):
    # Hooks may inherit the parent's Git environment when inspecting the child.
    env = {k: v for k, v in os.environ.items() if not k.startswith('GIT_')}
    env['GIT_NO_REPLACE_OBJECTS'] = '1'
    result = subprocess.run(['git', '-C', str(root), *args], input=data,
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env)
    if result.returncode:
        raise PrivacyError('Git inspection failed; refusing operation')
    return result.stdout


ARCHIVES = ('reference', 'writing/.corpus')
PROTECTED = (*ARCHIVES, 'local')


def protected(paths):
    return any(p == a.encode() or p.startswith(a.encode() + b'/')
               for a in PROTECTED
               for p in paths.split(b'\0') if p)


def check_index(root):
    baseline(root, 'labo.referencePrivacyBaseline')
    baseline(root, 'labo.corpusPrivacyBaseline')
    if protected(git(root, 'ls-files', '-z')):
        raise PrivacyError('reference/, writing/.corpus/ and local/ must not be tracked by the parent Git')


def manifest(root, revision, archive):
    # Raw entries include exact path, mode, object type and blob/gitlink OID.
    return git(root, 'ls-tree', '-r', '-z', revision, '--', archive)


def check_tree(root, revision):
    if manifest(root, revision, 'local'):
        raise PrivacyError('push contains local/ in a commit')
    if manifest(root, revision, 'reference'):
        raise PrivacyError('push contains reference/ in a commit; remove it before sending')
    corpus = manifest(root, revision, 'writing/.corpus')
    if corpus:
        raise PrivacyError('push contains new or changed writing/.corpus/ data')


def baseline(root, key):
    value = git(root, 'config', '--local', '--get', key).decode().strip()
    if not value or any(c not in '0123456789abcdef' for c in value):
        raise PrivacyError('invalid verified remote baseline')
    return git(root, 'rev-parse', '--verify', value + '^{commit}').decode().strip()


def check_push(root, lines):
    policy = subprocess.run(['git', '-C', str(root), 'config', '--local', '--get',
                             'labo.pushRole'], capture_output=True, text=True,
                            env={k: v for k, v in os.environ.items() if not k.startswith('GIT_')})
    if policy.returncode not in (0, 1):
        raise PrivacyError('cannot inspect local push policy')
    if policy.stdout.strip() == 'local-only':
        raise PrivacyError('research Git is local-only; all pushes are disabled')
    check_index(root)
    reference_base = baseline(root, 'labo.referencePrivacyBaseline')
    corpus_base = baseline(root, 'labo.corpusPrivacyBaseline')
    # Baseline is explicitly verified remote history, never inferred from HEAD.
    legacy_corpus = manifest(root, corpus_base, 'writing/.corpus')
    for line in lines:
        parts = line.split()
        if len(parts) != 4:
            raise PrivacyError('invalid pre-push input')
        oid = parts[1]
        if set(oid) == {'0'}:
            continue
        tip = git(root, 'rev-parse', '--verify', oid + '^{commit}').decode().strip()
        check_tree(root, tip)
        # local/ has no historical exception or newly trusted baseline.
        for commit in git(root, 'rev-list', tip).decode().splitlines():
            if manifest(root, commit, 'local'):
                raise PrivacyError('push contains local/ in an intermediate commit')
        for commit in git(root, 'rev-list', tip, '^' + reference_base).decode().splitlines():
            if manifest(root, commit, 'reference'):
                raise PrivacyError('push contains reference/ in an intermediate commit')
        for commit in git(root, 'rev-list', tip, '^' + corpus_base).decode().splitlines():
            corpus = manifest(root, commit, 'writing/.corpus')
            if corpus and corpus != legacy_corpus:
                raise PrivacyError('push contains new or changed intermediate corpus data')
    for archive in (*ARCHIVES, "local/materials"):
        child = root / archive
        if (child / '.git').exists() and git(child, 'remote').strip():
            raise PrivacyError('local source Git must have no remotes')


def hook_script(hooks, name):
    mode = 'check-push' if name == 'pre-push' else 'check-index'
    script = ('#!/bin/sh\n# labo-reference-privacy-v1\n'
              + 'root=$(git rev-parse --show-toplevel) || exit 1\n'
              + 'guard=$(git rev-parse --git-path hooks/labo-reference-guard.py) || exit 1\n')
    if mode == 'check-push':
        script += ('input=$(mktemp) || exit 1\ntrap \'rm -f "$input"\' EXIT HUP INT TERM\n'
                   'cat > "$input" || exit 1\n'
                   'python3 "$guard" check-push --workspace "$root" < "$input" || exit 1\n')
    else:
        script += 'python3 "$guard" check-index --workspace "$root" || exit 1\n'
    backup = hooks / (name + '.before-reference-privacy')
    if backup.exists():
        script += shlex.quote(str(backup)) + ' "$@"'
        script += ' < "$input"\n' if mode == 'check-push' else '\n'
    return script


def hooks_directory(root):
    custom = subprocess.run(['git', '-C', str(root), 'config', '--get', 'core.hooksPath'],
                            capture_output=True, text=True)
    if custom.returncode != 1:
        raise PrivacyError('custom core.hooksPath must be reviewed before installation')
    hooks = Path(git(root, 'rev-parse', '--git-path', 'hooks').decode().strip())
    return hooks if hooks.is_absolute() else root / hooks


def require_local_boundary(root):
    """Verify exclusion and the installed parent guard before private placement."""
    root = root.resolve()
    if Path(git(root, 'rev-parse', '--show-toplevel').decode().strip()).resolve() != root:
        raise PrivacyError('select the parent repository root')
    ignore = root / '.gitignore'
    if ignore.is_symlink() or not ignore.is_file() or '/local/' not in ignore.read_text().splitlines():
        raise PrivacyError('parent .gitignore needs the exact /local/ exclusion')
    probes = b'local/\0local/.privacy-probe\0local/materials/.privacy-probe\0local/cache/.privacy-probe\0local/output/.privacy-probe\0'
    if git(root, 'check-ignore', '--no-index', '-z', '--stdin', data=probes) != probes:
        raise PrivacyError('parent ignore rules do not exclude local/')
    check_index(root)
    hooks = hooks_directory(root)
    guard = hooks / 'labo-reference-guard.py'
    if guard.is_symlink() or not guard.is_file() or guard.read_bytes() != Path(__file__).read_bytes():
        raise PrivacyError('parent privacy guard is missing or outdated; refresh it from the policy checkout')
    for name in ('pre-commit', 'pre-push'):
        hook = hooks / name
        if hook.is_symlink() or not hook.is_file() or not os.access(hook, os.X_OK) or hook.read_text() != hook_script(hooks, name):
            raise PrivacyError('parent privacy hooks are missing or modified')


def install(root, verified_baseline=None):
    root = root.resolve()
    if Path(git(root, 'rev-parse', '--show-toplevel').decode().strip()).resolve() != root:
        raise PrivacyError('select the repository root')
    # Refresh is allowed only with both independently established boundaries.
    # Validate everything before replacing hooks; never infer trust from HEAD.
    values = {}
    for key in ('labo.referencePrivacyBaseline', 'labo.corpusPrivacyBaseline'):
        found = subprocess.run(['git', '-C', str(root), 'config', '--local', '--get', key],
                               capture_output=True, text=True)
        if found.returncode == 0:
            values[key] = baseline(root, key)
        elif found.returncode == 1 and verified_baseline:
            values[key] = git(root, 'rev-parse', '--verify', verified_baseline + '^{commit}').decode().strip()
        else:
            raise PrivacyError('installation needs independently verified baselines; refresh cannot create them')
    hooks = hooks_directory(root)
    hooks.mkdir(parents=True, exist_ok=True)
    for name in ('pre-commit', 'pre-push'):
        hook = hooks / name
        backup = hooks / (name + '.before-reference-privacy')
        if hook.is_symlink() or backup.is_symlink():
            raise PrivacyError('privacy hooks must be real files')
        if hook.exists() and '# labo-reference-privacy-v1' not in hook.read_text() and backup.exists():
            raise PrivacyError('hook backup already exists; inspect before replacing')
    for key, value in values.items():
        git(root, 'config', '--local', key, value)
    if (hooks / 'labo-reference-guard.py').is_symlink():
        raise PrivacyError('guard runtime must be a real file')
    shutil.copyfile(__file__, hooks / 'labo-reference-guard.py')
    for name in ('pre-commit', 'pre-push'):
        hook = hooks / name
        backup = hooks / (name + '.before-reference-privacy')
        if hook.exists() and '# labo-reference-privacy-v1' not in hook.read_text():
            hook.rename(backup)
        hook.write_text(hook_script(hooks, name))
        hook.chmod(0o755)


def install_archive(root, archive):
    root = root.resolve()
    child = root / archive
    if not child.is_dir() or child.is_symlink() or any(p.is_symlink() for p in child.parents if p != root):
        raise PrivacyError('archive must be an existing real directory')
    if (child / '.git').exists() and not (child / '.git').is_dir():
        raise PrivacyError('archive must use independent Git, not a submodule/worktree')
    if not (child / '.git').exists():
        git(child, 'init', '-q')
    if Path(git(child, 'rev-parse', '--show-toplevel').decode().strip()).resolve() != child.resolve():
        raise PrivacyError('archive must own its independent Git')
    if git(child, 'remote').strip():
        raise PrivacyError('archive Git must have no remotes')
    hooks = child / '.git' / 'hooks'
    marker = '# labo-local-source-deny-all-v1'
    hook = hooks / 'pre-push'
    if hook.exists() and marker not in hook.read_text():
        raise PrivacyError('existing archive hook requires review')
    hooks.mkdir(exist_ok=True)
    hook.write_text('#!/bin/sh\n' + marker + '\necho "Local source archive: all pushes are prohibited" >&2\nexit 1\n')
    hook.chmod(0o755)
    git(child, 'config', '--local', 'core.hooksPath', str(hooks))
    # Highest-priority attributes force actual local bytes, including PDFs.
    attributes = child / '.git' / 'info' / 'attributes'
    previous = attributes.read_text() if attributes.exists() else ''
    line = '* -filter\n'
    if not previous.endswith(line):
        attributes.write_text(previous + ('\n' if previous and not previous.endswith('\n') else '') + line)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('mode', choices=['install', 'refresh', 'check-local', 'install-archive', 'check-index', 'check-push'])
    parser.add_argument('--workspace', type=Path, required=True)
    parser.add_argument('--baseline', help='explicitly verified remote commit, for install only')
    parser.add_argument('--archive', choices=ARCHIVES)
    args = parser.parse_args()
    try:
        if args.mode == 'install':
            if not args.baseline:
                raise PrivacyError('installation needs an explicitly verified baseline')
            install(args.workspace, args.baseline)
        elif args.mode == 'refresh':
            install(args.workspace)
        elif args.mode == 'check-local':
            require_local_boundary(args.workspace)
        elif args.mode == 'install-archive':
            if not args.archive:
                raise PrivacyError('select --archive explicitly')
            install_archive(args.workspace, args.archive)
        elif args.mode == 'check-index':
            check_index(args.workspace)
        else:
            check_push(args.workspace, sys.stdin.read().splitlines())
    except (PrivacyError, OSError, ValueError) as exc:
        print('Source privacy: ' + str(exc), file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
