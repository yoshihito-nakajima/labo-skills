# {slug}

One source, one directory: everything made from this source lives here. The source's identity,
edition and covered scope are in [reference.md](reference.md).

## What is here

| Kind | Root file | Output | Status |
|---|---|---|---|
| (for example, Japanese translation) | `{slug}-ja.tex` | `output/{slug}-ja.pdf` | |
| (for example, explanation) | `{slug}-ja-expansion.tex` | `output/{slug}-ja-expansion.pdf` | |

Name a root so that its stem begins with `{slug}`; a stem that does not is published as `{slug}-<stem>`.
Sections or data of one kind go in a subdirectory (`sections/`, `companion/`). Put the fingerprint of the
source files this directory was made from in one `source-sha256.txt`.

## Route for a private HTML page

Route: (site | standalone | none)

- **site**: the page is authored Markdown at `website/content/private/{slug}.md`, built by the site generator.
  Keep no copy of it here, and build no standalone HTML for the same content.
- **standalone**: the master HTML (and its spec) stay in this directory; copy it to `output/` with
  `output copy-html --source reading/{slug}/<page>.html`.

Moving a page from one route to the other is a separate request.

## Notes

What was read, what is missing, and the next step.
