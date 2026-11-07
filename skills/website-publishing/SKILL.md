---
name: website-publishing
description: Draft or review mathematical web expositions, paper pages and academic profiles; maintain and publish a research website using verified source versions and the user's existing site tools.
---

# Research on the web

Before substantive work, follow [eligibility and handoff](../research-router/references/editing-capability.md).

For each user request, follow the [required consultation](../research-router/references/consultation.md).

When author identity, voice, or preferences matter, consult the Labo workspace
[author profile](../../../profile/author-identity.md) when available. Keep
personal facts there rather than in skill text; update only explicit durable
facts or corrections from the user, or facts they ask to save, with source
context. Apply this skill's normal verification and publication rules.

Use for mathematical web explanations, paper/talk pages, an academic profile
and site maintenance. Read [website policy](references/website-policy.md).
Infer audience, source version, destination and whether the request is for a
private explanation, a public-page draft or a live publication. Preserve the
existing site format and generator; no specific backend is required.

## Workflow

1. Identify the sources and intended visibility before drafting. A private
   explanation can use the requested current draft. A public explanation of
   an existing paper uses its identified public edition. An explicitly requested
   release of unpublished work has its own selected scope; do not silently
   convert one mode into another.
2. Inspect the relevant sources and existing page/configuration. Trace claims,
   dates, links and profile facts to evidence. If unpublished material has
   already shaped the context, produce a public-version exposition in a fresh
   context limited to the selected public sources; if unavailable, expose that
   limit and check every added claim against the permitted edition.
3. Write for the intended reader under
   [reader pull](../mathematical-exposition/references/reader-pull.md): the
   conclusion, a picture, why it matters and the key idea first; then each
   section with a plain opening, gap-free definitions and steps, figures that
   do work, and a closing that leads on; limitations and a route to the exact
   source last. Headings are natural claims or questions, without role labels
   such as 「問い｜」 or 「定義｜」. The page must read fully without following
   any link, and repository paths or `.md` names never appear on it. Keep
   pedagogical reconstruction distinct from what the source states. For a
   substantial paper reading or proof reconstruction, use `reading-reference`.
4. Before treating a drafted or substantially revised exposition as ready,
   run the [exposition-review](../exposition-review/SKILL.md) loop on the
   rendered page: independent flow review, then adversarial critique, triage
   and re-review. A page only its producer has read is a draft. Run
   `scripts/check_citations.py` on every changed page against its previous
   version; no rewrite may leave a dangling citation or drop a reference entry.
   Build/preview with the site's own tools. Check mathematical rendering,
   diagrams, links and narrow/wide layouts on the actual result. Review the
   selected release files and diff, including assets and linked documents.
5. Publish when authorized for that content and destination, using the existing
   deployment process. A current request to publish supplies authorization;
   do not demand a second confirmation by default. If authorization is missing,
   finish the reviewable draft and checks before asking about publication.
   Verify the live result when deployed and report its actual URL/status.

Keep private drafts in a private destination. Use the existing `website/`
project when present; research, Lean evidence, manuscripts and reference
originals retain their own homes. Generic skill improvements belong in the
user's labo-skills fork; site-specific configuration stays with that site.

For review-only work, return located findings under `W` criteria without
editing. State source edition, inspected pages, checks and unresolved issues.
Drafted, locally built, reviewed and deployed are distinct outcomes.
