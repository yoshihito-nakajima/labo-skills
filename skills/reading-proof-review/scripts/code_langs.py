"""Language table for code shown in reading pages (HTML and TeX).

One row per language. Builders ask this table instead of testing file extensions themselves, so
adding a language is one row here. Nothing in this file is specific to any paper.

What a builder needs from a language:
  listings   TeX `listings` language name (None: no color, plain listing)
  tex_def    a \\lstdefinelanguage snippet when `listings` does not ship the language
  comment    line-comment tokens; used to cut comments before looking for function calls
  index_base 0 or 1 -- tell the reader when it differs from the maths they are reading
  order      "row" / "column" -- default storage order of matrices
  api_prefix prefix of the API-card keys for this language ("" for the main language)
  call(name) regex that finds a call of `name` in comment-stripped text
  notes      short, language-specific traps worth a line in a line note (English; a paper-specific
             builder may translate them)

An unknown extension is never silently treated as another language: `lang_of` returns None and
`warn_unknown` collects the file names so the build can print them.
"""
import re
from pathlib import Path

_NAME = r"(?<![\w\.])"


def _py(n):   return _NAME + re.escape(n) + r"\s*\("
def _mat(n):  return _NAME + re.escape(n) + r"\b"
def _jl(n):   return _NAME + re.escape(n) + r"(?:!|\.)?\s*\("
def _r(n):    return _NAME + re.escape(n) + r"\s*\("
def _cpp(n):  return r"(?<![\w])" + re.escape(n) + r"\s*[\(<{]"


JULIA_DEF = (r"\lstdefinelanguage{Julia}{morekeywords={abstract,begin,break,catch,const,continue,do,else,"
             r"elseif,end,export,finally,for,function,global,if,import,in,let,local,macro,module,"
             r"mutable,quote,return,struct,try,using,where,while,true,false,nothing},"
             r"sensitive=true,morecomment=[l]{\#},morecomment=[n]{\#=}{=\#},morestring=[b]\"}")

LANGS = {
    "python": dict(name="Python", exts=(".py",), listings="Python", tex_def=None, comment=("#",),
                   index_base=0, order="row", api_prefix="", call=_py,
                   notes=("Indices start at 0; slices a:b exclude b.",
                          "numpy arrays are row-major; a 1-D array has no row/column distinction.")),
    "matlab": dict(name="MATLAB", exts=(".m",), listings="Matlab", tex_def=None, comment=("%",),
                   index_base=1, order="column", api_prefix="m:", call=_mat,
                   notes=("Indices start at 1; a:b includes b.", "Matrices are column-major; ' is the conjugate transpose.")),
    "octave": dict(name="Octave", exts=(), listings="Octave", tex_def=None, comment=("%", "#"),
                   index_base=1, order="column", api_prefix="oct:", call=_mat,
                   notes=("Mostly MATLAB-compatible, but not every MATLAB function exists or behaves identically.",
                          "Also .m files: pass override='octave' when the file is Octave.")),
    "julia": dict(name="Julia", exts=(".jl",), listings="Julia", tex_def=JULIA_DEF, comment=("#",),
                  index_base=1, order="column", api_prefix="jl:", call=_jl,
                  notes=("Indices start at 1; a:b includes b.", "f.(x) broadcasts f over x; a trailing ! means the function mutates its argument.",
                         "Arrays are column-major.")),
    "r": dict(name="R", exts=(".r",), listings="R", tex_def=None, comment=("#",),
              index_base=1, order="column", api_prefix="r:", call=_r,
              notes=("Indices start at 1; x[a:b] includes b and a negative index drops elements.",
                     "Matrices are column-major; data frames are lists of columns, not matrices.")),
    "cpp": dict(name="C++", exts=(".cpp", ".cc", ".cxx", ".hpp", ".hh", ".h"), listings="C++", tex_def=None, comment=("//",),
                index_base=0, order="row", api_prefix="cpp:", call=_cpp,
                notes=("Indices start at 0; there is no bounds check with operator[].",
                       "Check ownership: a & is a reference (no copy), a value argument is copied.",
                       "Libraries differ: Eigen is column-major by default, plain arrays are row-major.")),
}

_BY_EXT = {e: k for k, v in LANGS.items() for e in v["exts"]}


def lang_of(path, override=None):
    """Language key for a file path, or None when the extension is unknown."""
    if override:
        return override if override in LANGS else None
    return _BY_EXT.get(Path(str(path)).suffix.lower())


_UNKNOWN = []


def spec(path, override=None):
    """Row for `path`; unknown extensions are recorded and get a plain (uncolored) row."""
    k = lang_of(path, override)
    if k is None:
        if str(path) not in _UNKNOWN: _UNKNOWN.append(str(path))
        return dict(name="(unknown language)", listings=None, tex_def=None, comment=(), index_base=None,
                    order=None, api_prefix=None, call=None, notes=(), key=None)
    return dict(LANGS[k], key=k)


def warn_unknown():
    """File names seen with an unknown extension. A build should print these and fail only if asked."""
    return list(_UNKNOWN)


def strip_comments(lines, sp):
    out = []
    for l in lines:
        for tok in sp["comment"]:
            l = l.split(tok)[0]
        out.append(l)
    return "\n".join(out)


def tex_lang_option(sp):
    """`language=...` option text for lstinputlisting (empty when no color is available)."""
    return "language=%s," % sp["listings"] if sp["listings"] else ""


def tex_definitions(used_keys):
    """\\lstdefinelanguage lines needed for the languages actually used."""
    return "\n".join(LANGS[k]["tex_def"] for k in used_keys if k in LANGS and LANGS[k]["tex_def"])
