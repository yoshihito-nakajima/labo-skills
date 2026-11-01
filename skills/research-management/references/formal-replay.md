# Explicit selected-source Lean replay

- [Supported local environment](#supported-local-environment)
- [What actually runs](#what-actually-runs)
- [Evidence and axiom policy](#evidence-and-axiom-policy)
- [Tests and real execution](#tests-and-real-execution)
- [Primary references](#primary-references)

Use replay when an authorized review needs actual execution evidence for one
catalog claim's exact formal mapping. It complements the
[evidence protocol](evidence.md); it does not replace proof review, a full Lake
project rebuild, an external proof checker, or informal-to-formal alignment.

Resolve `<labo-script>` from the real skill directory as usual. First inspect
the read-only plan:

```sh
python3 <labo-script> evidence replay \
  --catalog research/example/claims.yaml --claim finite-cover --format json
```

Without `--execute`, this only reads the explicitly selected catalog, project,
prepared dependencies, and installed toolchain. It hashes existing inputs and
prints preflight problems and planned commands. It does not invoke Lean, Lake,
elan, Git, a shell, or the network, and does not create temporary files or
change any evidence. A plan can be printed even when execution prerequisites
are unavailable; `preflight.ready` distinguishes readiness from mere planning.

After inspecting the project and dependencies as trusted code, explicitly run:

```sh
python3 <labo-script> evidence replay \
  --catalog research/example/claims.yaml --claim finite-cover \
  --execute --timeout 120 --format json
```

`--timeout` is a finite positive wall-clock limit **per command**, not a global
budget. Exactly one claim is selected; the runner never implicitly executes
the catalog's whole dependency graph. The catalog and formal mapping are
validated, but other claims' projects are not executed.

## Supported local environment

The source must be an ordinary `.lean` file below the selected project. The
project must have its existing Lake file, `lean-toolchain`, and
`lake-manifest.json`, even for an empty dependency set. This runner does not
evaluate the Lake file. Its deliberately narrow automatic mode supports:

- An exact stable `leanprover/lean4:v4.X.Y` pin. Nightly, floating, custom and
  release-candidate pins are unavailable rather than guessed.
- A previously installed native toolchain with `bin/lean` (POSIX) or
  `bin/lean.exe` (Windows) and `lib/lean/Init.olean`. By default its directory is
  `$ELAN_HOME/toolchains/leanprover--lean4---v4.X.Y`, or the conventional
  `.elan/toolchains` below the user's home when `ELAN_HOME` is unset. No executable
  is discovered through `PATH`, and no elan shim is invoked. An existing native
  installation can instead be selected with `--toolchain-dir /absolute/path`.
- Simple ASCII dotted module/declaration names. Quoted identifiers, Unicode
  names, custom source roots, reserved root modules, and module-system-specific
  visibility that prevents ordinary import require a manual audit. The module
  is the selected source's project-relative path without `.lean`, with path
  separators replaced by dots. This is not a Lake source-root resolver.
- Prepared imports in the conventional `.lake/build/lib/lean` and each pinned
  dependency's `.lake/build/lib/lean`. Old/custom build directories are not
  guessed. Missing required imports produce an actual Lean failure.
- Root-manifest Git dependencies pinned to full lowercase 40-character commit
  IDs, already present in `.lake/packages/NAME` with matching local Git HEAD.
  Detached and ordinary loose/packed Git refs are read without executing Git.
  Local path dependencies, Git worktrees, package overrides, alternate package
  directories, and dependency subdirectories require manual replay.

Symlinked inputs and toolchains are rejected. Duplicate prepared module names
outside the selected module are unavailable, not silently resolved by search
order. Existing selected-module artifacts are not used for its audit: the newly
built temporary artifact has priority. Prepared imports can still be stale or
dirty relative to source. Their actual bytes, sources and pins are fingerprinted;
HEAD matching alone does **not** establish a clean checkout, reproducible build,
or correspondence between those artifacts and their sources.

The installed binary's actual `--version` must match the pin. Its `--help` must
advertise the required trust, root and stdin options. Unsupported installations
stop before the source build. Native executable format recognition is a guard
against accidental script/shim selection, not executable authenticity checking.

## What actually runs

Execution uses argument vectors, never `shell=True`, and a controlled environment
containing the selected toolchain's binary directory, system default search
paths, `LEAN_SYSROOT`, the explicit prepared `LEAN_PATH`, and locale settings.
Windows additionally preserves `SYSTEMROOT` when set. The complete actual
argument vector, working directory, environment, stdin, exit code, stdout,
stderr and duration are included for each attempted command. The steps are:

1. Query the selected native Lean binary's version and help.
2. Build **the selected source only** with the same binary, `--trust=0`, an
   explicit project root and `-o` pointing to a fresh temporary `.olean`.
3. Start a separate invocation of that same binary with `--trust=0 --stdin`.
   Import the freshly built selected module, run `#check @Declaration` and
   `#print Declaration` with explicit/full pretty-printing (`pp.all`, including
   deep terms) and a large `pp.maxSteps` limit, then run
   `#print axioms Declaration`. These options are registered in the official
   Lean 4.19.0 `Lean/PrettyPrinter/Delaborator/Options.lean`; no unregistered
   `pp.maxDepth` option is emitted.

The output is retained verbatim as execution evidence; pretty-printing is not a
canonical serialization of theorem semantics. The selected declaration may
itself be imported by the selected source: automatic replay does not establish
the declaration's original source ownership. Inspect the mapping, printed type,
definitions and alignment separately. A success exit code without a built
artifact or recognizable, unique axiom-audit output is **not** accepted as a
completed replay.

No `lake build`, `lake update`, `lake env`, cache getter, installer, automatic
toolchain update or dependency fetch is launched. In particular, Lake's
documented `--no-cache` prevents cache downloads, but it is not a general
no-network switch; ordinary builds can synchronize dependencies. This runner
therefore bypasses Lake instead of guessing a `--no-update` flag or claiming
that a normal build is offline.

**This is not network or filesystem isolation.** Lean is a programming language
and project/dependency code can execute during elaboration, import or other
compile-time processing. `--execute` means execute the selected **trusted** code
with those side effects; it is not permission to install missing dependencies
or deliberately download resources. Inspect first; use an externally configured
sandbox for untrusted code, including unreviewed generated proofs. The runner
cannot enforce a no-network policy on arbitrary Lean code.

On POSIX a timeout kills the process group, including ordinary descendants.
Deliberately detached processes are outside this trusted-code contract. On
Windows a timeout kills the direct Lean process; descendant termination is not
guaranteed and the report says so. File-backed stdout/stderr capture prevents
inherited output-pipe handles from holding the runner indefinitely after the
direct process exits. This is not a Windows job-object sandbox.

## Evidence and axiom policy

The report records hashes before and after execution: the catalog, all selected
project and prepared dependency `.lean` files, pinned environment/configuration
files, compiled `.olean`/`.ilean` files and relevant native/IR artifacts, the
native Lean executable, and the selected toolchain's Lean library files. It
also hashes the controlled environment and newly built artifact. These complete
hash maps can be large; use the text summary for ordinary inspection and JSON
when preserving an auditable manifest. Untracked files outside this explicitly
inventoried scope are not covered. Source/env changes or unreadable inputs
during execution invalidate completion. Hashes cannot detect a change that is
made and restored between the two observations.

Report states mean:

| State | Meaning |
| --- | --- |
| `plan` | Read-only plan; no command was executed, even if ready |
| `unavailable` | Execution was requested but a prerequisite was absent or unsupported; no Lean invocation occurred |
| `failed` | An attempted command, version/feature check, artifact check, axiom audit, or input-stability check failed |
| `completed` | Selected-source build and exact declaration/axiom observations completed with stable tracked inputs; **not approval** |

Each command retains its own `not-run`, `completed`, `failed`, `timeout`, or
`unavailable` state. Unattempted checks are never presented as passing. If
execution stopped before the axiom command, the axiom audit remains `not-run`.

`#print axioms` is transitive. Any reported `sorryAx` makes replay fail, including
when only an imported helper uses a placeholder. No source-text grep is used as
a substitute. All other reported axioms remain exposed in full with
`review_required: true`: this runner does not adopt an axiom allowlist on the
reviewer's behalf. Distinguish standard logical axioms such as `propext`,
`Classical.choice`, and `Quot.sound` from custom assumptions and native-compute
trust. Depending on Lean version, native evaluation can expose
`Lean.trustCompiler` or dedicated computation axioms. A custom axiom can make a
theorem conditional or vacuous; a `completed` replay does not endorse it. Record
the exact allowed assumptions and why they match the informal theorem in the
separate kernel/trust and alignment review.

Even a replay reporting no axioms uses the selected Lean implementation, runtime,
compiled imports and operating environment. It does not constitute independent
kernel verification, prove the informal statement, detect all malicious code,
or replace an external checker. Merely requesting `--trust=0` is not represented
as a guarantee that every prepared import was independently re-checked.

The runner prints the report and removes only its own temporary build directory;
it never automatically saves over an existing report. If preserving stdout,
choose a new report path and use an exclusive-create or no-clobber mechanism.
An existing kernel report, catalog verdict/status, passing review snapshot or
alignment report is never overwritten, refreshed, approved or promoted by
replay. A human/agent must separately interpret the evidence and perform the
actual scoped review. Preserve previous evidence through normal version control.

## Tests and real execution

Synthetic unit tests exercise planning without subprocesses/writes, exact command
records, supported/unsupported toolchains, prepared inputs, changed sources,
timeouts, failure propagation, transitive `sorryAx`, custom axioms and malformed
audit output. Mocked Lean output is explicitly test data, never kernel evidence.

To require a real smoke test against a toolchain that is **already installed**:

```sh
LABO_REPLAY_TOOLCHAIN_DIR=/absolute/path/to/prepared/toolchain \
LABO_REQUIRE_REAL_LEAN=1 \
python3 -m unittest discover -s tests -p test_formal_replay.py -v
```

The real test builds an elementary theorem, checks a transitive-placeholder
failure, and observes a custom axiom. Without a selected toolchain the test
truthfully skips; `LABO_REQUIRE_REAL_LEAN=1` turns a missing selection into a
failure. This hook installs nothing. Mocked Windows path/process tests do not
claim a real Windows Lean run. CI must explicitly provision a pinned toolchain
outside the runner before requiring the smoke test.

## Primary references

- [Lean: Validating a Lean Proof](https://lean-lang.org/doc/reference/latest/ValidatingProofs/)
  distinguishes elaboration, transitive axiom audits, external checkers,
  meaning/alignment and malicious code.
- [Lean's FAQ](https://lean-lang.org/faq/) explains that building or opening Lean
  code can execute arbitrary code and recommends isolation for untrusted code.
- [Lake's reference](https://lean-lang.org/doc/reference/latest/Build-Tools-and-Distribution/Lake/)
  documents dependency synchronization, build caches, `lake env`, package
  overrides and the actual CLI options. The direct-runner design intentionally
  avoids invoking these dependency-management pathways.
- [Lean's axiom-printing implementation](https://github.com/leanprover/lean4/blob/master/src/Lean/Elab/Print.lean)
  uses `collectAxioms` and emits the recognized declaration-specific output.

References describe the upstream tools; the report's actual version, commands,
outputs and hashes identify what this particular replay executed.
