#!/usr/bin/env python3
"""Folder placement policy for a research workspace: what may leave the machine.

Two kinds only. There is no public kind: research material never goes to a public
remote, and a remote counts as acceptable only after it is verified private.

  local-only   never in the parent Git history or on any remote
  private-ok   may be committed and pushed, but only to a verified private remote

The policy file is `.labo-placement.json` at the repository root. Commands:

  check      report drift between the policy and what is tracked (read-only)
  gitignore  print, or with --write update, the managed ignore block
  remote     verify with the GitHub CLI that a remote URL is private (network, read-only)

Nothing here pushes, deletes or rewrites anything.
"""
from __future__ import annotations

import argparse
import fnmatch
import json
import os
from pathlib import Path
import re
import subprocess
import sys

POLICY_FILE = '.labo-placement.json'
KINDS = ('local-only', 'private-ok')
# Material that is never committed to any remote, whatever its folder: books and
# other bulky downloaded originals. A folder may allow specific own files by glob.
DEFAULT_BLOCKED = ('.pdf', '.zip', '.epub', '.djvu', '.mobi', '.tar', '.gz')
DEFAULT_MAX_BYTES = 5_000_000
BEGIN = '# >>> labo-placement (managed) >>>'
END = '# <<< labo-placement (managed) <<<'


class PlacementError(RuntimeError):
    pass


def git(root, *args):
    env = {k: v for k, v in os.environ.items() if not k.startswith('GIT_')}
    result = subprocess.run(['git', '-C', str(root), *args], capture_output=True, env=env)
    if result.returncode:
        raise PlacementError('Git inspection failed: ' + ' '.join(args[:2]))
    return result.stdout


def load_policy(root):
    path = Path(root) / POLICY_FILE
    if not path.is_file() or path.is_symlink():
        raise PlacementError('missing ' + POLICY_FILE + ' (a regular file at the repository root)')
    try:
        data = json.loads(path.read_text(encoding='utf-8'))
    except ValueError as exc:
        raise PlacementError('invalid JSON in ' + POLICY_FILE) from exc
    folders = data.get('folders')
    if not isinstance(folders, dict) or not folders:
        raise PlacementError('"folders" must map top-level folder names to a kind')
    for name, kind in folders.items():
        if kind not in KINDS:
            raise PlacementError('unknown kind %r for %r; use one of %s (there is no public kind)'
                                 % (kind, name, ', '.join(KINDS)))
        if '/' in name or name in ('', '.', '..', '.git'):
            raise PlacementError('folder names are single top-level names: ' + repr(name))
    blocked = tuple(s.lower() for s in data.get('blocked_suffixes', DEFAULT_BLOCKED))
    allow = tuple(data.get('allow', ()))
    max_bytes = int(data.get('max_file_bytes', DEFAULT_MAX_BYTES))
    return {'folders': folders, 'blocked': blocked, 'allow': allow, 'max_bytes': max_bytes}


def allowed(path, allow):
    return any(fnmatch.fnmatchcase(path, pattern) for pattern in allow)


def tracked(root):
    return [p.decode('utf-8', 'surrogateescape')
            for p in git(root, 'ls-files', '-z').split(b'\0') if p]


def head_sizes(root):
    sizes = {}
    out = subprocess.run(['git', '-C', str(root), 'ls-tree', '-r', '-l', '-z', 'HEAD'],
                         capture_output=True)
    if out.returncode:
        return sizes  # no commit yet
    for entry in out.stdout.split(b'\0'):
        if not entry:
            continue
        meta, _, name = entry.partition(b'\t')
        fields = meta.split()
        if len(fields) == 4 and fields[3].isdigit():
            sizes[name.decode('utf-8', 'surrogateescape')] = int(fields[3])
    return sizes


def range_paths(root, revision_range):
    """Paths added or modified by commits in a range, e.g. the commits about to be pushed."""
    out = git(root, 'log', '--format=', '--name-only', '-z', '--diff-filter=AM', revision_range)
    return sorted({p.decode('utf-8', 'surrogateescape') for p in out.split(b'\0') if p.strip()})


def top(path):
    return path.split('/', 1)[0]


def inspect(root, policy, paths, sizes):
    findings = []
    folders = policy['folders']
    for path in paths:
        kind = folders.get(top(path))
        if kind is None:
            if '/' in path or path not in ('.gitignore', '.gitattributes', '.gitmodules',
                                           POLICY_FILE, 'README.md', 'AGENTS.md', '.agents', '.claude'):
                findings.append(('unclassified', path))
            continue
        if kind == 'local-only':
            findings.append(('tracked-in-local-only', path))
            continue
        if allowed(path, policy['allow']):
            continue
        if Path(path).suffix.lower() in policy['blocked']:
            findings.append(('blocked-type', path))
        elif sizes.get(path, 0) > policy['max_bytes']:
            findings.append(('oversize', path))
    return findings


def cmd_check(args):
    root = args.repo.resolve()
    policy = load_policy(root)
    paths = range_paths(root, args.range) if args.range else tracked(root)
    findings = inspect(root, policy, paths, head_sizes(root))
    gitignore = (root / '.gitignore').read_text(encoding='utf-8') if (root / '.gitignore').is_file() else ''
    missing = [n for n, k in policy['folders'].items()
               if k == 'local-only' and '/' + n + '/' not in gitignore.splitlines()]
    report = {'scope': args.range or 'tracked files', 'findings':
              [{'kind': k, 'path': p} for k, p in findings],
              'local_only_not_ignored': missing}
    print(json.dumps(report, ensure_ascii=False, indent=2))
    hard = [f for f in findings if f[0] != 'unclassified']
    return 1 if hard or missing else 0


def render_block(policy):
    lines = [BEGIN, '# Generated from ' + POLICY_FILE + '; edit the policy, not this block.']
    lines += ['/' + n + '/' for n, k in sorted(policy['folders'].items()) if k == 'local-only']
    lines.append(END)
    return '\n'.join(lines) + '\n'


def cmd_gitignore(args):
    root = args.repo.resolve()
    block = render_block(load_policy(root))
    if not args.write:
        sys.stdout.write(block)
        return 0
    path = root / '.gitignore'
    text = path.read_text(encoding='utf-8') if path.is_file() else ''
    pattern = re.compile(re.escape(BEGIN) + r'.*?' + re.escape(END) + r'\n?', re.S)
    text = pattern.sub(lambda _m: block, text) if pattern.search(text) else \
        text + ('' if not text or text.endswith('\n') else '\n') + block
    path.write_text(text, encoding='utf-8')
    return 0


def parse_github(url):
    match = re.match(r'^(?:https://github\.com/|git@github\.com:)([\w.-]+)/([\w.-]+?)(?:\.git)?/?$', url)
    if not match:
        raise PlacementError('only github.com remotes can be verified; treat any other as not private')
    return match.group(1), match.group(2)


def cmd_remote(args):
    owner, name = parse_github(args.url)
    result = subprocess.run(['gh', 'api', 'repos/%s/%s' % (owner, name), '--jq', '.private'],
                            capture_output=True, text=True)
    answer = result.stdout.strip()
    if result.returncode or answer not in ('true', 'false'):
        print(json.dumps({'url': args.url, 'private': 'unverified'}))
        return 1
    print(json.dumps({'url': args.url, 'private': answer == 'true'}))
    return 0 if answer == 'true' else 1


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest='mode', required=True)
    check = sub.add_parser('check')
    check.add_argument('--repo', type=Path, required=True)
    check.add_argument('--range', help='commits to inspect, e.g. origin/main..HEAD')
    check.set_defaults(run=cmd_check)
    ignore = sub.add_parser('gitignore')
    ignore.add_argument('--repo', type=Path, required=True)
    ignore.add_argument('--write', action='store_true')
    ignore.set_defaults(run=cmd_gitignore)
    remote = sub.add_parser('remote')
    remote.add_argument('--url', required=True)
    remote.set_defaults(run=cmd_remote)
    args = parser.parse_args(argv)
    try:
        return args.run(args)
    except PlacementError as exc:
        print('placement: ' + str(exc), file=sys.stderr)
        return 2


if __name__ == '__main__':
    sys.exit(main())
