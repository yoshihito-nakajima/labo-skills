#!/usr/bin/env python3
"""Local-only research and reviewed policy pushes. No network operations."""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import shlex
import subprocess
import sys


class GuardError(RuntimeError):
    pass


def git(root, *args, optional=False):
    env = {k: v for k, v in os.environ.items() if not k.startswith('GIT_')}
    # Push transmits original objects, not the local refs/replace view.
    env['GIT_NO_REPLACE_OBJECTS'] = '1'
    result = subprocess.run(['git', '-C', str(root), *args], capture_output=True, env=env)
    if result.returncode and not (optional and result.returncode == 1):
        raise GuardError('Git inspection failed: ' + ' '.join(args[:2]))
    return result.stdout


def gitpath(root, name):
    path = Path(os.fsdecode(git(root, 'rev-parse', '--git-path', name)).strip())
    return path if path.is_absolute() else root / path


def commit(root, ref):
    if ref.startswith('-'):
        raise GuardError('invalid revision')
    return git(root, 'rev-parse', '--verify', ref + '^{commit}').decode().strip()


ROOT_FILES = {'.gitignore', 'README.md', 'README.ja.md', 'LICENSE', 'LICENSE.md',
              'pyproject.toml', 'plugin.json', 'settings.json'}
ROOT_DIRS = {'.github', 'agents', 'scripts', 'skills', 'src', 'tests'}
PRIVATE_PARTS = {'reference', 'research', 'writing', 'reading', 'inbox', 'output',
                 'profile', 'local', '.corpus', '.temp', '.env', '.aws', '.ssh'}
BLOCKED_SUFFIXES = {'.pdf', '.zip', '.gz', '.tar', '.png', '.jpg', '.jpeg', '.docx',
                    '.pptx', '.sqlite', '.db', '.synctex', '.pem', '.key'}
# Only these reviewed generic templates may use private-layout path components.
# Blob/type checks and human content review still apply to them.
LAYOUT_TEMPLATES = {'skills/labo-layout/assets/writing/.corpus/README.md',
                    'skills/labo-layout/assets/writing/.corpus/index.md'}


def check_path(path):
    parts = Path(path).parts
    if (not parts or not (path in ROOT_FILES or (len(parts) > 1 and parts[0] in ROOT_DIRS))
            or (path not in LAYOUT_TEMPLATES and any(p.lower() in PRIVATE_PARTS for p in parts))
            or Path(path).suffix.lower() in BLOCKED_SUFFIXES):
        raise GuardError('non-policy path in history: ' + path)


def check_entry(root, revision, path, seen):
    data = git(root, 'ls-tree', '-z', revision, '--', ':(literal)' + path)
    for entry in data.split(b'\0'):
        if not entry:
            continue
        meta, rawpath = entry.split(b'\t', 1)
        mode, kind, oid = meta.split()
        check_path(os.fsdecode(rawpath))
        if mode not in (b'100644', b'100755') or kind != b'blob':
            raise GuardError('non-regular policy entry: ' + path)
        if oid in seen:
            continue
        seen.add(oid)
        if int(git(root, 'cat-file', '-s', oid.decode())) > 1024 * 1024:
            raise GuardError('oversized policy blob: ' + path)
        blob = git(root, 'cat-file', 'blob', oid.decode())
        try:
            blob.decode('utf-8')
        except UnicodeDecodeError:
            raise GuardError('non-text policy blob: ' + path)
        if b'\0' in blob or blob.startswith(b'version https://git-lfs.github.com/spec/'):
            raise GuardError('binary or external-object policy blob: ' + path)


def check(root, base, head):
    if git(root, 'rev-parse', '--is-shallow-repository').strip() != b'false':
        raise GuardError('fetch complete history before reviewing a contribution')
    grafts = gitpath(root, 'info/grafts')
    if grafts.exists() and grafts.stat().st_size:
        raise GuardError('legacy grafts obscure history; review an ungrafted checkout')
    base, head = commit(root, base), commit(root, head)
    if git(root, 'merge-base', base, head).decode().strip() != base:
        raise GuardError('public base must be an ancestor of the contribution')
    revisions = git(root, 'rev-list', '--reverse', head, '^' + base).decode().splitlines()
    seen, paths = set(), set()
    for rev in revisions:
        parents = git(root, 'show', '-s', '--format=%P', rev).decode().split()
        if not parents:
            raise GuardError('unrelated root commit in contribution')
        for parent in parents:
            changed = git(root, 'diff-tree', '--no-commit-id', '--no-renames',
                          '--name-only', '-r', '-z', parent, rev).split(b'\0')
            for raw in filter(None, changed):
                path = os.fsdecode(raw)
                check_path(path)
                paths.add(path)
                for version in (parent, rev):
                    check_entry(root, version, path, seen)
    return {'base': base, 'head': head, 'commits': revisions, 'paths': sorted(paths)}


def role(root):
    return git(root, 'config', '--local', '--get', 'labo.pushRole', optional=True).decode().strip()


def check_push(root, destination, lines):
    if role(root) == 'local-only':
        raise GuardError('research Git is local-only; all pushes are disabled')
    if role(root) != 'policy':
        raise GuardError('missing or invalid push role')
    receipt_path = gitpath(root, 'labo-publication-review.json')
    if receipt_path.is_symlink():
        raise GuardError('review record must be a real file')
    receipt = json.loads(receipt_path.read_text())
    if receipt.get('destination') != destination or not receipt.get('content_reviewed'):
        raise GuardError('destination or content review does not match')
    for line in lines:
        fields = line.split()
        if len(fields) != 4:
            raise GuardError('invalid pre-push input')
        _, oid, remote_ref, _ = fields
        if not remote_ref.startswith('refs/heads/') or set(oid) == {'0'}:
            raise GuardError('only reviewed branch updates are supported')
        if oid != receipt.get('head'):
            raise GuardError('head changed; review the new commits first')
        check(root, receipt['base'], oid)


MARKER = '# labo-publication-guard-v1'


def hook_text(script, backup):
    text = ('#!/bin/sh\n' + MARKER + '\n'
            'root=$(git rev-parse --show-toplevel) || exit 1\n'
            'input=$(mktemp) || exit 1\n'
            'trap \'rm -f "$input"\' EXIT HUP INT TERM\n'
            'cat > "$input" || exit 1\n'
            'python3 ' + shlex.quote(str(script)) +
            ' check-push --repo "$root" --destination "$2" < "$input" || exit 1\n')
    if backup.exists():
        text += shlex.quote(str(backup)) + ' "$@" < "$input"\n'
    return text


def install(root, requested_role):
    if git(root, 'config', '--null', '--get', 'core.hooksPath', optional=True):
        raise GuardError('custom core.hooksPath needs review before installation')
    hooks = gitpath(root, 'hooks')
    hook, backup = hooks / 'pre-push', hooks / 'pre-push.before-publication-guard'
    for path in (hooks, hook, backup):
        if path.is_symlink():
            raise GuardError('hook paths must not be symlinks')
    previous = hook.read_text() if hook.exists() else ''
    if '# labo-reference-privacy-v1' in previous:
        if requested_role != 'local-only':
            raise GuardError('source archive guard cannot become a public policy checkout')
        import reference_privacy
        try:
            reference_privacy.install(root)
        except reference_privacy.PrivacyError as exc:
            raise GuardError(str(exc)) from exc
    else:
        if previous and MARKER not in previous and backup.exists():
            raise GuardError('hook backup exists; inspect before replacing')
        if previous and MARKER not in previous and not os.access(hook, os.X_OK):
            raise GuardError('existing inactive hook needs review')
        hooks.mkdir(parents=True, exist_ok=True)
        if previous and MARKER not in previous:
            hook.rename(backup)
        hook.write_text(hook_text(Path(__file__).resolve(), backup.resolve()))
        hook.chmod(0o755)
    git(root, 'config', '--local', 'labo.pushRole', requested_role)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('mode', choices=['install', 'status', 'check', 'review', 'check-push'])
    parser.add_argument('--repo', type=Path, required=True)
    parser.add_argument('--role', choices=['local-only', 'policy'])
    parser.add_argument('--base')
    parser.add_argument('--head', default='HEAD')
    parser.add_argument('--destination')
    parser.add_argument('--content-reviewed', action='store_true')
    args = parser.parse_args()
    try:
        root = args.repo.resolve()
        if Path(git(root, 'rev-parse', '--show-toplevel').decode().strip()).resolve() != root:
            raise GuardError('select the repository root')
        if args.mode == 'install':
            if not args.role:
                raise GuardError('select an explicit role')
            install(root, args.role)
        elif args.mode == 'status':
            hook = gitpath(root, 'hooks/pre-push')
            custom = git(root, 'config', '--null', '--get', 'core.hooksPath', optional=True)
            print(json.dumps({'role': role(root), 'hooksPath': custom[:-1].decode() if custom else 'default',
                  'custom_hooks_path_configured': bool(custom),
                  'default_pre_push_present': hook.is_file() and os.access(hook, os.X_OK),
                  'review_record_present': gitpath(root, 'labo-publication-review.json').is_file()}, indent=2))
        elif args.mode == 'check-push':
            check_push(root, args.destination, sys.stdin.read().splitlines())
        else:
            if not args.base:
                raise GuardError('select an explicitly verified public base')
            report = check(root, args.base, args.head)
            if args.mode == 'review':
                if role(root) != 'policy' or not args.destination or not args.content_reviewed:
                    raise GuardError('review requires policy role, destination and content review')
                report.update(destination=args.destination, content_reviewed=True)
                path = gitpath(root, 'labo-publication-review.json')
                if path.is_symlink():
                    raise GuardError('review record must be a real file')
                path.write_text(json.dumps(report, indent=2) + '\n')
            print(json.dumps(report, indent=2))
    except (GuardError, OSError, ValueError, KeyError) as exc:
        print('Publication guard: ' + str(exc), file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
