"""Compile scoped mathematical notation to display TeX."""

import re


TOKEN = re.compile(r"@[A-Za-z][A-Za-z0-9]*|\\[A-Za-z]+|\\.|[A-Za-z][A-Za-z0-9]*|[0-9]+|\s+|.", re.S)
NAME = re.compile(r"[A-Za-z][A-Za-z0-9]*")
OPERATOR = re.compile(r"[A-Za-z][A-Za-z0-9 ]*")
GREEK = frozenset("alpha beta gamma delta epsilon varepsilon zeta eta theta kappa lambda mu nu xi rho sigma tau phi varphi psi omega Delta Sigma Psi Gamma Lambda Omega".split())
TEX = frozenset(r"""
  \frac \tfrac \sqrt \left \right \big \Big \bigl \bigr \Bigl \Bigr
  \lvert \rvert \lVert \rVert \langle \rangle \lceil \rceil \lfloor \rfloor
  \{ \} \, \; \! \quad \qquad \mid \colon \dots \cdots \ldots
  \in \notin \subset \subseteq \supseteq \cup \cap \setminus \times \varnothing
  \to \mapsto \longrightarrow \circ \cdot \otimes \oplus \odot \pm \mp
  \wedge \vee \neg \implies \Rightarrow \iff \Leftrightarrow
  \le \leq \ge \geq \lt \gt \ne \neq \equiv \approx \sim \asymp \propto
  \succeq \prec \succ \perp \top \infty \partial \nabla \pi
  \sin \cos \log \ln \exp \min \max \sup \inf \ker \det \dim \lim
  \overline \bar \widehat \hat \widetilde \tilde \dot \ddot \star \dagger
  \int \sum \prod \mathinner \substack \Chi
""".split())
OPERATORS = {"op": "operatorname", "operatorname": "operatorname",
             "mathrm": "mathrm", "mathbb": "mathbb", "mathcal": "mathcal"}
RELATION = re.compile(r"(?:[=<>]|\\(?:in|notin|subset(?:eq)?|supseteq|leq?|geq?|lt|gt|ne|neq|equiv|approx|sim|asymp|propto|succeq|prec|succ|perp))")
QUANTIFIERS = {"all": r"\forall", "some": r"\exists", "one": r"\exists!"}


def display_name(name):
    if name in GREEK:
        return "\\" + name
    indexed = re.fullmatch(r"([A-Za-z])([0-9]+)", name)
    if indexed:
        return indexed[1] + "_{" + indexed[2] + "}"
    if len(name) == 1:
        return name
    return r"\mathrm{" + name + "}"


class Formula:
    def __init__(self, source):
        self.tokens = iter(match[0] for match in TOKEN.finditer(source))
        self.advance()

    def advance(self):
        token = getattr(self, "token", None)
        self.token = next(self.tokens, None)
        return token

    def expect(self, token):
        if self.token != token:
            raise ValueError(f"{token} が必要（{self.token or '式末尾'}）")
        self.advance()

    def plain_group(self, pattern):
        self.expect("{")
        chunks = []
        while self.token is not None and self.token != "}":
            chunks.append(self.advance())
        self.expect("}")
        value = "".join(chunks)
        if not pattern.fullmatch(value):
            raise ValueError(f"不正な記号名 {value}")
        return value

    def group(self, scope, *, statement=False):
        self.expect("{")
        result = self.expression(scope, statement=statement)
        self.expect("}")
        if not result.strip():
            raise ValueError("空のグループ")
        return result

    def scoped(self, command, scope):
        name = self.plain_group(NAME)
        if name in scope:
            raise ValueError(f"変数 {name} の束縛が重複")
        domain = self.group(scope)
        body = self.group(scope | {name}, statement=command in QUANTIFIERS or command == "setof")
        var = display_name(name)
        if command in QUANTIFIERS:
            quantifier = f"{QUANTIFIERS[command]} {var}"
            if domain.strip() != "*":
                quantifier += rf"\in {domain}"
            return rf"{quantifier},\ \left[{body}\right]"
        if command == "setof":
            return rf"\left\{{{var}\in {domain}\mid {body}\right\}}"
        if command == "limto":
            return rf"\lim_{{{var}\to {domain}}}\left({body}\right)"
        if command == "sumover":
            return rf"\sum_{{{var}\in {domain}}}\left({body}\right)"
        return rf"\left({var}\in {domain}\mapsto {body}\right)"

    def expression(self, scope, *, statement=False):
        parts = []
        has_relation = False
        while self.token is not None and self.token != "}":
            token = self.token
            if token == "{":
                parts.append("{" + self.group(scope) + "}")
                continue
            self.advance()
            has_relation |= bool(RELATION.fullmatch(token)) or token in (r"\pred", r"\all", r"\some", r"\one")
            if token.startswith("@"):
                name = token[1:]
                if name not in scope:
                    raise ValueError(f"自由変数 {name}")
                parts.append("{" + display_name(name) + "}")
            elif token.startswith("\\"):
                command = token[1:]
                if command in ("all", "some", "one", "setof", "sumover", "limto", "fn"):
                    parts.append(self.scoped(command, scope))
                elif command in OPERATORS or command == "pred":
                    name = self.plain_group(OPERATOR)
                    if command == "pred" and self.token != "(":
                        raise ValueError(f"述語 {name} の引数が必要")
                    parts.append(r"\{}{{{}}}".format(OPERATORS.get(command, "operatorname"), name))
                elif token in TEX:
                    parts.append(token)
                else:
                    raise ValueError(f"未定義のコマンド {token}")
            elif token.isascii() and (token.isspace() or token.isdecimal() or token in "+-*/=<>^_()[]|.,:;!"):
                parts.append(token)
            else:
                raise ValueError(f"未束縛または未定義の記号 {token}。変数は @ を付けて宣言する")
        if statement and not has_relation:
            raise ValueError("閉論理式には関係または述語が必要")
        if statement and parts and RELATION.fullmatch(parts[-1].rstrip()):
            raise ValueError("関係記号の後に項が必要")
        return "".join(parts)


def closed_tex(source):
    """Return TeX after checking variable scope. Named set operations are notation."""
    if not isinstance(source, str) or not source.strip():
        raise ValueError("閉論理式が必要")
    prefix, separator, body = source.strip().partition(" :: ")
    domains = []
    scope = set()
    if separator:
        for declaration in prefix.split(";"):
            name, colon, domain = declaration.strip().partition(":")
            if not colon or not NAME.fullmatch(name) or name in scope:
                raise ValueError(f"不正または重複した束縛 {declaration.strip()}")
            quantifier = rf"\forall {display_name(name)}"
            if domain.strip() != "*":
                parsed_domain = parse_expression(domain, scope)
                quantifier += rf"\in {parsed_domain}"
            domains.append(quantifier)
            scope.add(name)
    else:
        body = prefix
    conclusion = parse_expression(body, scope, statement=True)
    if domains:
        clauses = ["&" + domain + "," for domain in domains]
        clauses.append(rf"&\left[{conclusion}\right]")
        return r"\begin{aligned}" + r"\\ ".join(clauses) + r"\end{aligned}"
    return conclusion


def parse_expression(source, scope, *, statement=False):
    formula = Formula(source.strip())
    tex = formula.expression(scope, statement=statement)
    if not tex or formula.token is not None:
        raise ValueError("空の式または対応しない波括弧")
    return tex
