# Reference privacy

`reference/` is a local-only source archive, including bibliographic records,
PDFs, extracted text, figures, supplements and downloaded code. Open access
does not make an exception. Neither public nor private GitHub is a destination.

Before saving sources, check parent `git ls-files -- reference` is empty and
`git check-ignore -v -- reference/<key>/<file>` confirms exclusion. Ignore rules
alone do not untrack files. Never use `git add -f` for this archive, register it
as a submodule, add a remote to its local Git, disable privacy hooks, or copy
restricted sources/metadata/excerpts to parent-tracked or policy paths.
Direct uploads, attachments, external services and repository backups are also
sharing: do not use them for this archive. Review derived reading notes and
corpus records before placing confidential content in a sendable repository.
Sources already stored elsewhere retain their restrictions; moving or renaming
them never authorizes sharing. Public bibliographic citations may be used
normally when they reveal no confidential information.

Local history, when requested, uses an independent `reference/.git`, no remotes,
no LFS/external object storage, and an executable pre-push hook rejecting every
push (including URL pushes). Preserve original bytes and verify actual blobs.
Book processing caches, full OCR and page renders remain in ignored temporary
areas unless explicitly requested as part of the source archive. Book working
repositories must not accidentally absorb these originals.

## Explicit migration and protection

Layout initialization only appends `/reference/`, `/writing/.corpus/` and `/local/` to
the parent ignore rules;
it does not migrate existing tracking, initialize Git, or install hooks.
When the user requests migration:

1. Inspect index, worktree, source hashes, LFS, effective hook configuration and
   existing local repositories. Preserve unrelated work and existing hooks.
2. Exclude `/reference/` in the parent and remove its paths from the parent
   index using `git rm --cached`, preserving all working files. Commit only the
   migration paths; do not stage unrelated research or policy changes.
3. Initialize the local archive only on explicit request. Preserve formerly
   tracked files even if downloaded `.gitignore` files would hide them.
   Keep local archive snapshots and provenance local; compare hashes after
   migration. No remote, push, LFS service or automatic cloud backup.
4. After verifying a baseline commit exists on the existing remote, install
   parent guards explicitly with `python3 <policy>/scripts/reference_privacy.py
   install --workspace <workspace> --baseline <verified-commit>`. Never choose
   an unverified local HEAD as a whitelist. The guard preserves/chains existing
   pre-commit/pre-push hooks and copies its runtime into the local hooks folder.
   Custom `core.hooksPath` needs review; installation fails rather than overwrites it.
5. Check staged reference additions are rejected and all commits newer than
   the baseline are inspected, including intermediate commits, branches and
   tags. A clean final tree alone is insufficient. Missing guard/config or Git
   inspection failure must reject the operation. Verify both repositories'
   effective hooks after migration and after restoring a workspace on a new
   computer; hooks and local Git are not transported by cloning the parent.

Hooks are protection against ordinary mistakes, not an access-control boundary
against someone deliberately bypassing them. Never use `--no-verify` or altered
hook paths to bypass a privacy failure. Copying the same data elsewhere also
evades path checks and remains prohibited. If a push is blocked, inspect and
repair the commits before retrying. An ignore/removal commit does not erase
prior history or already uploaded LFS objects. Report such history honestly;
remote deletion or history rewriting requires its own authorized operation.

## Local-only corpus

`writing/.corpus/` is the workspace-wide local-only corpus for both reading and
writing. Its originals, registration/index metadata, excerpts, comparisons and
selection records all stay outside the parent and policy Git. Public access,
open licensing, and private GitHub do not create exceptions. Keep its location
and source bytes; a local Git is independent, has no remotes, stores actual
bytes without LFS, and rejects every push including explicit URL pushes.
Never force-add it, register a submodule, bypass hooks, copy its data to a
tracked alternate path, or upload it directly. Existing source locations retain
their restrictions; links do not grant permission to share their targets.

The parent must ignore `/writing/.corpus/` and track no entries beneath it.
For an authorized migration, preserve a first local snapshot of the exact
pre-migration files and local provenance before correcting storage notes or
performing an audit. Remove parent tracking with `git rm --cached`, retaining
working files, and commit only the migration paths. The same explicit parent
installer protects both archives. It retains the existing reference baseline
and records a corpus baseline from explicitly verified remote history. Every
pushed tip must contain neither archive. Intermediate corpus entries are
permitted only when their entire path/mode/object manifest exactly matches
that already-remote corpus baseline; added or changed entries are rejected,
even if later deleted. This exception never whitelists local HEAD or extends
the reference baseline. Already uploaded history may remain; removing tracking
does not erase it. Do not rewrite remote history without separate authorization.

When local history is requested, initialize and protect the selected archive
with `python3 <policy>/scripts/reference_privacy.py install-archive --workspace
<workspace> --archive writing/.corpus` (or `--archive reference`). The command
preserves content, rejects existing remotes or unreviewed hooks, installs the
deny-all pre-push hook and locally disables clean filters so PDFs remain real
blobs. It does not make a snapshot automatically: inspect existing ignore
rules, explicitly stage formerly tracked files without force-add, commit
locally, and compare actual blobs and hashes. Verify effective hooks, remotes
and filters after migration or restore. Parent hooks fail closed on missing
baseline/configuration/runtime or failed Git inspection and preserve existing
LFS hooks. Hooks cannot stop deliberate bypass or uploads via other tools;
those actions remain prohibited by this rule.

Detailed source selections, local IDs, paths, access history and excerpts belong
in `writing/.corpus/selections/<document>/corpus.toml` or another record inside
the local corpus. Review pre-existing paper `decisions/corpus.toml` before
staging it: never copy local selection metadata into a tracked paper. A tracked
paper decision or `writing/.rules/` may contain only independently adopted,
minimal nonconfidential formatting/exposition rules, without private provenance
or distinctive source wording. The corpus remains descriptive rather than a
stylistic requirement.

## Workspace-local book materials

The entire workspace `local/` is private, including its originals, derived
mathematics, metadata, private instructions, navigation, caches and output.
`local/` itself has no Git. New books/topics default to no Git; only an explicitly
selected project may have guarded local history. Preserve the legacy independent
`local/materials/` Git. Original books in `local/original/` are gitignored and must
never enter any Git, including local history. Review inputs containing originals
remain outside Git as well.
Follow [reading-book storage](../../reading-book/references/storage.md) for
placement, child push protection and stopped-writer migration. Do not relocate
activity outside the workspace merely to avoid parent Git tracking.

Before writing private data, add the exact `/local/` parent exclusion. Refresh
existing parent guards with `reference_privacy.py refresh --workspace <workspace>`;
this requires and preserves both independently verified reference/corpus
baselines. `check-local` verifies exclusion, an empty protected parent index,
the effective hooks and the current installed runtime. Refresh does not trust
HEAD or add a local/ baseline. First-time installation still requires the
verified-remote procedure above. Parent commit protection rejects forced files
and gitlinks anywhere under `local/`; push protection inspects every reachable
commit of every sent branch or tag, including annotated tags and intermediate
add-then-remove leaks. `local/` has no historical exemption. Existing LFS/hooks
are chained and missing runtime/configuration fails closed. The same limits
on deliberate bypass and direct uploads apply.
