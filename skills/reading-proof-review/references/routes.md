# Where the page goes: the site route and the standalone route

A private reading page is made by exactly one of two routes; the two are not mixed. The contract is
in [labo-layout](../../labo-layout/references/layout.md#private-html-the-site-route-and-the-standalone-route);
this file says what to run.

## Choose

1. Does the workspace have a private site (`website/content/private/` and its generator)? If yes,
   the page is a **Reader page** (site route), except a companion, which runs code with controls
   and stays standalone. If no, it is **standalone**.
2. Write the route in the source's `reading/<slug>/README.md` (`layout new reading` creates it with a
   `Route:` line). Moving a page to the other route is a separate request.

## Site route

| Kind | Command | Result |
|---|---|---|
| Proof review | `python3 <scripts>/export_site_page.py <spec-dir> --slug <slug> --out-dir website/content/private --lang ja` | `<slug>.md` and `figures/<slug>/diagram.svg` |
| Prose page | write `website/content/private/<slug>.md` (authored Markdown, [prose.md](prose.md)) | the page itself |

Then build the Reader: `cargo run --locked --manifest-path website/generator/Cargo.toml -- private`.
The generator needs nested `::: details Summary {#anchor}` blocks. The Markdown of a proof review is
generated: edit the spec and export again. Keep no copy of site Markdown under `reading/`.

## Standalone route

| Kind | Command |
|---|---|
| Proof review | `python3 <scripts>/build_review_page.py <spec-dir> --out reading/<slug>/<slug>-review.html --lang <lang>` |
| Proof book | `python3 <scripts>/proof_book.py build <project>` |
| Companion | `python3 <scripts>/build_pair.py PAIR.json --workspace <root>` (or `build_companion.py`) |
| Prose page | `python3 <scripts>/build_prose_page.py reading/<slug>/<slug>.md --out reading/<slug>/<slug>.html` |

Check with `check_review_page.py <page.html>` (ids, in-page links, mathematics; companions use
`check_companion.py`). The **master stays in `reading/<slug>/`**; copy it to `output/` with
`output copy-html --source reading/<slug>/<page>.html`. KaTeX is embedded so the page is one offline file;
`fetch_katex.py` downloads a pinned, integrity-checked copy once the user agrees.

## Same Markdown, either route

The prose dialect is that of the site generator, so one authored Markdown page can be built by the site
or by `build_prose_page.py`. Choose one for a given page and record it; do not publish both.
