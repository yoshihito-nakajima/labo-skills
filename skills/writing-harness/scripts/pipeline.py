"""Keep every output of a harness in step with its cards.

Called by `cards.py build | watch | hook | stamp` and by the editor server.

- A *source hash* covers everything the outputs are made from (cards, structure,
  harness.toml, preamble, macros, bibliography).
- Each output (`tex:<name>`, `pdf:<name>`, `html`, `read`) records the source hash it
  was made from in `<paper_dir>/.build.json`. `check` reports an output whose hash
  differs as OUTDATED, so a forgotten rebuild is visible.
- `request_build` marks the harness dirty and starts one detached builder per
  harness (a file lock keeps it single). The builder waits for a quiet period, builds,
  and builds again if the cards changed meanwhile. Edits made in quick succession
  therefore cost one build.
"""
import hashlib
import json
import os
import shlex
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPTS.parents[2] / 'src'))
from labo_tools.locking import exclusive_lock, try_exclusive_lock

CARDS_PY = SCRIPTS / 'cards.py'
LABO_PY = SCRIPTS.parents[2] / 'scripts' / 'labo.py'   # present when the skill sits in a labo-skills checkout
SOURCE_SUFFIXES = {'.md', '.yaml', '.yml', '.toml', '.tex', '.bib'}


# ---------------------------------------------------------------- source hash and stamps

def source_files(h):
    files = sorted(h.cards_dir.glob('*/*.md'))
    for key, default in (('structure', 'structure.yaml'), (None, 'harness.toml'), ('preamble', None),
                         ('macros', 'macros.tex'), ('bibliography', None)):
        name = h.cfg.get(key) if key else None
        name = name or default
        if name:
            p = h.root / name
            if p.is_file():
                files.append(p)
    return files


def source_hash(h):
    d = hashlib.sha256()
    for p in source_files(h):
        d.update(str(p.relative_to(h.root) if p.is_relative_to(h.root) else p).encode())
        d.update(b'\0')
        d.update(p.read_bytes())
        d.update(b'\0')
    return d.hexdigest()[:16]


def is_source(h, path):
    """Is this file one the outputs are made from?"""
    p = Path(path).resolve()
    if p.suffix not in SOURCE_SUFFIXES:
        return False
    if p.is_relative_to(h.cards_dir):
        return True
    return p in {q.resolve() for q in source_files(h)}


STATE_FILES = ['.build.json', '.build.lock', '.build.log', '.build.tmp', '.builder.lock', '.dirty']


def paper_dir(h):
    """The render directory; it also holds the build state, kept out of Git by its own .gitignore."""
    d = h.path('paper_dir', 'paper')
    d.mkdir(parents=True, exist_ok=True)
    gi = d / '.gitignore'
    have = gi.read_text(encoding='utf-8').split() if gi.exists() else []
    missing = [f for f in STATE_FILES if f not in have]
    if missing:
        with gi.open('a', encoding='utf-8') as f:
            f.write(''.join(m + '\n' for m in missing))
    return d


def stamp_path(h):
    return paper_dir(h) / '.build.json'


def read_stamps(h):
    try:
        return json.loads(stamp_path(h).read_text(encoding='utf-8'))
    except (OSError, ValueError):
        return {}


def write_stamp(h, output, src=None, **extra):
    p = stamp_path(h)
    p.parent.mkdir(parents=True, exist_ok=True)
    with open(p.with_suffix('.lock'), 'a+b') as lk, exclusive_lock(lk):
        data = read_stamps(h)
        data.setdefault('outputs', {})[output] = {'source': src or source_hash(h),
                                                  'time': datetime.now().isoformat(timespec='seconds'), **extra}
        tmp = p.with_suffix('.tmp')
        tmp.write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding='utf-8')
        tmp.replace(p)


def outdated(h):
    """Outputs whose recorded source hash differs from the current one (or that failed)."""
    outs = read_stamps(h).get('outputs', {})
    cur = source_hash(h) if outs else None
    res = []
    for name, rec in sorted(outs.items()):
        if rec.get('ok') is False:
            res.append(f'OUTDATED {name}: the last build failed ({rec.get("time")}); see {rel_log(h)}')
        elif rec.get('source') != cur:
            res.append(f'OUTDATED {name}: built {rec.get("time")} from older cards (run cards.py build)')
    return res


def rel_log(h):
    return h.rel(paper_dir(h) / '.build.log')


# ---------------------------------------------------------------- the build itself

def tex_targets(h):
    """[(file name, sections or None)] from [build] tex (default: cards.tex)."""
    out = []
    for t in (h.cfg.get('build') or {}).get('tex') or ['cards.tex']:
        if isinstance(t, str):
            out.append((t, None))
        else:
            out.append((t['out'], t.get('sections')))
    return out


def pdf_command(h, tex):
    """Command list that turns paper/<tex> into a PDF, or None when PDFs are off or no builder exists."""
    b = h.cfg.get('build') or {}
    if b.get('pdf') is False:
        return None
    cmd = b.get('pdf_command')
    if cmd is None:
        if not LABO_PY.exists():
            return None
        cmd = [sys.executable, str(LABO_PY), 'output', 'build', '--source', '{tex}']
    if isinstance(cmd, str):
        cmd = shlex.split(cmd)
    texp = (paper_dir(h) / tex).resolve()
    return [c.replace('{tex}', str(texp)).replace('{python}', sys.executable)
             .replace('{labo}', str(LABO_PY)).replace('{harness}', str(h.root)) for c in cmd]


def build(h, pdf=True, log=print):
    """check -> render every TeX target -> PDF -> card viewer -> reading page. Returns 0 on success."""
    import argparse
    import cards as C   # noqa: PLC0415 - cards.py imports this module
    src = source_hash(h)
    cards, errors0 = C.load_cards(h)
    errors, warn = C.check(h, cards, errors0)
    for e in errors:
        log(f'error: {e}')
    if errors:
        log(f'build stopped: {len(errors)} errors in the cards (outputs left as they were)')
        return 1
    status = 0
    for tex, sections in tex_targets(h):
        C.cmd_render(h, argparse.Namespace(out=tex, sections=sections))
        if not pdf:
            continue
        if (h.cfg.get('build') or {}).get('pdf') is False:
            continue
        cmd = pdf_command(h, tex)
        if cmd is None:
            log(f'pdf:{tex}: skipped (set [build] pdf_command in harness.toml)')
            continue
        r = subprocess.run(cmd, cwd=h.workspace, capture_output=True, text=True)
        tail = (r.stdout + r.stderr).strip().splitlines()[-15:]
        if r.returncode:
            status = 1
            log(f'pdf:{tex}: FAILED ({" ".join(cmd[:3])} ...)\n  ' + '\n  '.join(tail))
            write_stamp(h, f'pdf:{tex}', src, ok=False)
        else:
            log(f'pdf:{tex}: ' + (tail[-1] if tail else 'built'))
            write_stamp(h, f'pdf:{tex}', src, ok=True)
    C.cmd_html(h, argparse.Namespace())
    C.cmd_read(h, argparse.Namespace())
    if source_hash(h) != src:
        log('note: the cards changed during the build; build again')
    return status


# ---------------------------------------------------------------- background builder

def dirty_path(h):
    return paper_dir(h) / '.dirty'


def request_build(h, pdf=True):
    """Mark the harness dirty and make sure a detached builder will pick it up."""
    d = dirty_path(h)
    d.parent.mkdir(parents=True, exist_ok=True)
    d.write_text(datetime.now().isoformat(timespec='seconds'), encoding='utf-8')
    if builder_running(h):
        return 'queued'
    args = [sys.executable, str(CARDS_PY), '--root', str(h.root), 'build', '--background']
    if not pdf:
        args.append('--no-pdf')
    with open(paper_dir(h) / '.build.log', 'a') as logf:
        subprocess.Popen(args, stdout=logf, stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL,
                         start_new_session=True, cwd=h.root)
    return 'started'


def builder_running(h):
    lock = paper_dir(h) / '.builder.lock'
    lock.parent.mkdir(parents=True, exist_ok=True)
    with open(lock, 'a+b') as f, try_exclusive_lock(f) as acquired:
        return not acquired


def background(h, pdf=True):
    """Loop of the detached builder: wait for quiet, build, repeat while dirty."""
    with open(paper_dir(h) / '.builder.lock', 'a+b') as lock, try_exclusive_lock(lock) as acquired:
        if not acquired:
            return 0   # another builder owns this harness and will see the marker
        return _background_locked(h, pdf)


def _background_locked(h, pdf):
    quiet = float((h.cfg.get('build') or {}).get('quiet', 3))
    d = dirty_path(h)
    status = 0
    while d.exists():
        age = time.time() - d.stat().st_mtime
        if age < quiet:
            time.sleep(quiet - age + 0.1)
            continue
        mark = d.stat().st_mtime
        print(f'== build {datetime.now().isoformat(timespec="seconds")}', flush=True)
        status = build(h, pdf=pdf, log=lambda s: print(s, flush=True))
        if d.exists() and d.stat().st_mtime == mark:
            d.unlink()
    return status


def build_state(h):
    """For the editor: is a build running, what is outdated, last log lines."""
    log = paper_dir(h) / '.build.log'
    tail = log.read_text(encoding='utf-8', errors='replace').splitlines()[-30:] if log.exists() else []
    if tail:
        last = max((i for i, s in enumerate(tail) if s.startswith('== build')), default=0)
        tail = tail[last:]
    return {'running': builder_running(h) or dirty_path(h).exists(), 'outdated': outdated(h),
            'log': tail, 'source': source_hash(h)}


# ---------------------------------------------------------------- watch and hooks

def watch(h, pdf=True, interval=1.0):
    last = source_hash(h)
    print(f'watching {h.rel(h.root)} (Ctrl-C to stop)', flush=True)
    if outdated(h):
        request_build(h, pdf)
    try:
        while True:
            time.sleep(interval)
            cur = source_hash(h)
            if cur != last:
                last = cur
                print(f'{datetime.now():%H:%M:%S} change -> build {request_build(h, pdf)}', flush=True)
    except KeyboardInterrupt:
        return 0


def hook(event_json):
    """Claude Code PostToolUse hook: rebuild in the background when a harness source file was written.

    Reads the hook JSON from stdin. Silent and exit 0 for any other file, so it is safe
    as a project-wide hook.
    """
    try:
        data = json.loads(event_json or '{}')
    except ValueError:
        return 0
    ti = data.get('tool_input') or {}
    paths = [ti.get('file_path') or ti.get('notebook_path') or '']
    paths += [e.get('file_path', '') for e in ti.get('edits') or [] if isinstance(e, dict)]
    import cards as C   # noqa: PLC0415
    done = set()
    for p in filter(None, paths):
        p = Path(p)
        if not p.is_absolute():
            p = Path(data.get('cwd') or os.getcwd()) / p
        root = next((d for d in p.resolve().parents if (d / 'harness.toml').exists()), None)
        if root is None or root in done:
            continue
        h = C.Harness(root)
        if is_source(h, p):
            done.add(root)
            pdf = (h.cfg.get('build') or {}).get('hook_pdf', True)
            request_build(h, pdf)
    return 0
