# Writing corpus

This local-only workspace corpus holds examples and source references shared
by writing, reading notes and lectures. It records descriptive evidence, not
requirements. Select only examples relevant to the audience and document type.

Keep the entire corpus, including its index, registration metadata, excerpts
and selection records, outside the parent and policy Git. Local history uses
an independent `.git`, no remotes or LFS, and a deny-all pre-push hook covering
URL pushes too. No public or private GitHub, direct upload, forced parent add,
hook bypass or tracked alternate-path copies, including for open materials.
Keep existing originals in their established locations and preserve their bytes
and restrictions; link to them without treating links as publication permission.

For each source, record a stable ID, kind, path or citation, version and precise
locator, relevant scope, useful features and limits. Learn terminology, rhythm,
transitions and explanatory pacing without copying distinctive wording or claims.
Record detailed selections and judgments in local
`selections/<document>/corpus.toml`. A tracked paper decision or writing rule
may contain only minimal independently adopted nonconfidential rules, without
local source IDs, paths, excerpts or private provenance.
