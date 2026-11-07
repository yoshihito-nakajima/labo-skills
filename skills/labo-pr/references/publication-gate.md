# Public contribution gate

Apply the [publication boundary](../../labo-git/SKILL.md#publication-boundary)
to both fork pushes and upstream PRs. Only the independent policy Git is
eligible by default; everything outside it stays local. A private destination
does not widen the scope. `.claude` aliases the same policy checkout locally.

1. **Classify** each changed file as public generic policy/tooling,
   private research/source/writing, or ambiguous. Start with an explicit list of
   public files needed for the requested reusable fix. The default contribution
   is rules/procedures, necessary reusable tooling and fictional verification
   examples. Exclude manuscripts, research-specific reading/reference notes,
   acquired papers/code archives, PDFs, data/results, private logs, conversations,
   screenshots and local publication-candidate records unless the particular
   content and its publication are explicitly authorized. Classify content, not
   directory names: generic skill `references/` instructions may be public;
   research material remains private even inside a skill directory. Book originals,
   extracted claims/proofs, courses, catalogs, source correspondence, progress,
   private instructions and navigation under workspace `local/` stay local,
   including when the GitHub repository is private. Only their generic
   procedures/tools/templates and genuinely fictional tests are PR candidates.
2. **Extract** a minimal public fix with fictional fixtures. Remove names,
   private claims, unpublished conjectures, personal URLs, file paths, and
   source text unless independently approved for publication. Extract the reusable
   decision rule or procedure; renaming people or files does not make a private
   mathematical claim, proof or source-based reading account a public fixture.
   Replace motivating incidents with genuinely fictional examples that stand on
   their own. Preserve necessary legitimate attribution for public reusable
   material. A publicly reachable paper or archive, or permission to read/cite it,
   is not by itself permission or a reason to redistribute its contents. Link
   appropriate public sources rather than automatically bundling acquired files.
   Keep unresolved private or ambiguous material out of the public branch and
   report any resulting scope limitation privately.
3. **Verify** that the public diff stands on its own and tests without
   access to a private `labo` checkout. Review status in the policy checkout
   and its parent when one exists; stage and review selected paths in the
   policy checkout only. Verify the contents of selected files and bundled/generated
   outputs, not only their names or extensions. Do not publish a private source
   merely to make a generic test pass; make the fixture self-contained instead.
   A standalone checkout has no parent gitlink step.
4. **Choose** the PR head in the researcher's fork and the base in the shared
   upstream, checking actual repository URLs and branch names. If the fork
   contains unrelated customizations, prepare the contribution from the intended
   upstream base and select only relevant commits or changes; do not replace
   the user's working branch or submit the entire fork delta. A checkout may have a
   detached HEAD: preserve local work and attach it to the selected branch
   before committing. Inspect remote URLs; a name such as `origin` does not
   prove it is the researcher's fork. Use the researcher's branch names;
   do not prescribe a parallel branch hierarchy for everyday work.
5. **Review** the complete proposed branch diff and included commits, not
   just the latest working-tree diff. Inspect each included commit's contents:
   material added and later deleted is still published in that history. If
   necessary, preserve the existing work and build a clean contribution branch
   containing only the extracted fix. Inspect the PR title/body, commit messages,
   attachments, images, logs and linked artifacts for private content or identifying
   paths as well. Do not expose private details even in a public exclusion list.
   Keep a local record of the selected public scope, excluded material categories,
   reviewed base/head and checks. State the observed research-workflow
   problem, resulting behavior, reproduction or synthetic example, and checks
   in the PR description. Review destination, base, title and body with the
   human when publication is not already requested; keeping an improvement
   fork-only is equally legitimate.
6. **Publish** within the policy repository only. A push request alone does
   not request a PR; a requested PR includes its necessary reviewed branch
   push. Neither operation requires a parent commit, parent push, parent PR
   or gitlink update. PR acceptance does not automatically adopt a version.
7. **Adopt** a selected policy commit in one's own fork, and then
   update `.agents` and its private-parent gitlink when authorized,
   with local checks. Adoption need not wait for upstream acceptance or a
   push; the parent records the chosen version locally. Publish a reviewed
   policy commit to the fork only within the requested scope. Never auto-update
   to a remote branch tip or discard local changes. Policy push, policy PR and
   local parent version recording are independent operations.

The upstream maintainer can contribute from a branch in the shared repository;
a fork of one's own repository under the same account is not required. Other
researchers use the fork-to-upstream workflow above.

The human may push changes directly. When the user has already explicitly
requested the particular PR, that request supplies the publication decision;
do not demand a second confirmation merely to follow this checklist.

`.gitignore` is not a privacy barrier: once secret material was committed
to a public history, ignoring it later does not remove that history.
