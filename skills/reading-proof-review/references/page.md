# The page

Built by `scripts/build_review_page.py` from a spec directory:

- `steps.json`: the [ledger](ledger.md).
- `bodies.json`: per step `l1` (one line, always visible), `l2` (key reasoning, folded), `l3`
  (line-by-line proof, folded again). HTML; math is `<span class="m">TeX</span>` inline or
  `<div class="d">TeX</div>` display.
- `review.json`: title, `summary_html`, optional `intro_html`, `key_ideas_html`, `groups` (headings
  over lists of step ids), `step_review` (risk and evidence per step), `panel` rows, `findings`
  (`id`, `sev` fatal/major/minor/form, `status` confirmed/suspected/unchecked, `short`, `steps`,
  `from`, `detail` HTML, `ruling`), `prior` rows, `prior_hole`, `uncited`, `admitted`, `indicator`.
- `demo.html` (optional): a small self-contained snippet, with its own script, that lets the reader
  move a parameter of a lemma on synthetic data.

Layout: summary and verdict, the result, the proof spine (dependency diagram, then step cards),
the key-versus-standard table, the optional demo, the review, prior work, the indicator.

Fold levels: key steps open to their key reasoning, standard steps stay folded, so the look of the
page is itself the comparison. The side panel opens or closes everything; following a link opens the
folds above its target; printing opens all.

Write the page in the user's language (`--lang`). Say plainly that it is a local file, not
published. Text fields are escaped; HTML fields are trusted, so do not paste untrusted markup.

## As a Reader page (the site route)

Where the workspace has a private site (`website/content/private/` and its generator), the reading
is a Reader page and no standalone HTML is built for the same content
([the two routes](../../labo-layout/references/layout.md#private-html-the-site-route-and-the-standalone-route)).
The spec directory is the same; `scripts/export_site_page.py` writes it as authored Markdown:

```sh
python3 <scripts>/export_site_page.py <spec-dir> --slug <slug> --out-dir website/content/private --lang ja
cargo run --locked --manifest-path website/generator/Cargo.toml -- private   # builds the Reader
```

It writes `<out-dir>/<slug>.md` (frontmatter with title, slug and language) and
`<out-dir>/figures/<slug>/diagram.svg`. `<slug>` is lowercase ASCII with single hyphens; for an
English edition name it `<slug>-en`, which shares the figure directory of `<slug>`.

What comes out: the summary, the result and the key ideas; the dependency diagram as an SVG figure;
each step as a fold with its source, origin and dependencies, its one line, why its class, and inside it
the key reasoning and the line-by-line proof as nested folds; the key-versus-standard, panel, prior-work
and indicator tables; the findings as folds. Step and finding ids become anchors (`step-<id>`, `find-<id>`),
so the links between steps and findings work. Mathematics is `$...$` and `$$...$$`, rendered by the generator.

Differences from the standalone page: the boxes of the diagram are not links (it is an image); every fold starts
closed, so key steps are not open to their reasoning; there is no side panel and no demo. Pages that need a demo
with controls stay on the standalone route.

The Markdown is generated: edit the spec and export again, never the Markdown, and keep no copy of it under
`reading/`. Mention the route in the source's `README.md`. After building, check the page as a reader would:
the folds nest correctly and no in-page link is left without a target.

## Math

KaTeX (free, open source, MIT licence) is inlined so the page stays one offline file. It is not
bundled in this repository. `scripts/fetch_katex.py` downloads a pinned release from the official
npm registry into a per-user cache (`~/.cache/labo-skills/katex/<version>`), checks it against its
published sha512 integrity before unpacking, and extracts only the script, stylesheet, fonts and
licence. `build_review_page.py` looks, in order, at `--katex-dir`, `$KATEX_DIR`, that cache, and a
TeX Live copy; `--fetch-katex` downloads into the cache when none is found. The user's go-ahead is
needed before the first download; after that the page builds offline.

With a complete KaTeX the usual math commands work. If a directory has only some fonts (some TeX
Live copies do) the builder warns, and the commands those fonts would need (`\mathbb`, `\mathbf`,
`\mathcal`, a filled star) must be avoided. Without KaTeX the TeX source stays visible.

## Checks

`check_review_page.py` verifies placeholders, ids, links, a card for every step and finding, and,
with node and KaTeX, every math span and script. It does not see the screen: also open the page,
or take a screenshot with a headless browser, and read the key cards, the comparison table, the
findings list and the verdict.
