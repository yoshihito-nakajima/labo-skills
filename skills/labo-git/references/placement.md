# Folder placement policy

Decide once, per top-level folder, what may leave the machine, and let a script
keep `.gitignore` and the pre-push review in line with that decision. The helper is
[`scripts/placement.py`](../../../scripts/placement.py); it only reads Git state and
never pushes, deletes, untracks or rewrites anything.

## The policy file

`.labo-placement.json` at the repository root maps each top-level folder to one kind:

```json
{
  "folders": {
    "archive": "local-only",
    "drafts":  "private-ok",
    "notes":   "private-ok"
  },
  "allow": ["drafts/figures/*.pdf"]
}
```

- `local-only`: never in the parent Git history and never on any remote. Such a folder
  is ignored, and normally carries its own local Git if history is wanted.
- `private-ok`: may be committed and pushed, but only to a remote verified private.
- There is no public kind. Research material never goes to a public remote, and a
  remote that cannot be verified private is treated as not private. Public destinations
  (a skills fork, a website) are separate repositories handled by the
  [publication boundary](../SKILL.md#publication-boundary), not by this file.
- Books and other paid material are not placed anywhere; they do not enter any Git,
  including a private one. The defaults also keep downloaded originals out of
  `private-ok` folders: `.pdf .zip .epub .djvu .mobi .tar .gz`, and files above 5 MB.
  List an exact glob in `allow` only for own files of such a type (generated figures,
  own distribution bundles). `blocked_suffixes` and `max_file_bytes` may be overridden.

## Commands

```sh
python3 <policy>/scripts/placement.py check     --repo <workspace> [--range <base>..HEAD]
python3 <policy>/scripts/placement.py gitignore --repo <workspace> [--write]
python3 <policy>/scripts/placement.py remote    --url <remote-url>
```

- `check` lists drift and exits 1 on any hard finding: a tracked file in a `local-only`
  folder, a blocked type, an oversize file, or a `local-only` folder missing from
  `.gitignore`. A top-level path not named in the policy is reported as `unclassified`
  and is not fatal. With `--range` it inspects only the commits about to be pushed.
- `gitignore` prints the managed block, or with `--write` replaces it in place and keeps
  every other line. Edit the policy, not the block.
- `remote` asks the GitHub CLI whether a remote is private (read-only network call).
  It exits 0 only for a verified private repository; anything else, including an
  unreachable API or a non-GitHub host, is not private.

## Before a push of the parent

1. `check --range <verified-remote-head>..HEAD` has no hard finding.
2. `remote --url <push-url>` reports private.
3. Read the live remote when other writers exist; a local remote-tracking ref can be stale.
4. Push without force. A guard baseline that tracks verified remote history is moved
   only to a head that was read and inspected.

## Limits

`.gitignore` does not affect files already tracked: `check` finds those, but untracking,
moving or purging history from a remote is a separate decision for the user. The helper
checks paths, types and sizes, not the content or the license of a file; those remain
a human review. It adds no hook; the push guards described in [setup](setup.md) are
unchanged.
