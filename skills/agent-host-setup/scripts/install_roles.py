#!/usr/bin/env python3
"""Preview/create native roles; preserve every existing differing file."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import tomllib

import yaml


ROLES = {
    "math-decomposer": ["Read", "Glob", "Grep", "Agent"],
    "math-proof-worker": ["Read", "Glob", "Grep", "Edit", "Write", "Bash"],
    "math-verifier": ["Read", "Glob", "Grep"],
}


def render_roles(workspace: Path, host: str, model: str, effort: str,
                 policy_root: Path | None = None) -> dict[Path, str]:
    workspace = workspace.resolve()
    policy_root = (policy_root or Path(__file__).resolve().parents[3]).resolve()
    contract = policy_root / "skills/research-router/references/mathematical-roles.md"
    if not contract.is_file():
        raise ValueError(f"missing checked-out role contract: {contract}")
    try:
        relative = policy_root.relative_to(workspace).as_posix()
    except ValueError as exc:
        raise ValueError("policy checkout must be mounted within the target workspace") from exc
    if host == "claude":
        if (workspace / ".claude").resolve() != policy_root:
            raise ValueError("Claude needs the policy at .claude or a whole-directory .claude alias to it")
        relative = ".claude"
    if not model.strip() or "\n" in model:
        raise ValueError("supply one explicitly selected callable model")
    if "luna" in model.lower():
        raise ValueError("Luna is restricted to evidence/coordination in this fork")
    allowed = {"low", "medium", "high", "xhigh", "max", "ultra"}
    if effort not in allowed or (host == "claude" and effort == "ultra"):
        raise ValueError("unsupported effort spelling; verify support for the selected model")
    files = {}
    for name, tools in ROLES.items():
        skill = policy_root / "skills" / name / "SKILL.md"
        text = skill.read_text(encoding="utf-8")
        if not text.startswith("---\n") or len(text.split("---", 2)) != 3:
            raise ValueError(f"invalid role skill frontmatter: {skill}")
        metadata = yaml.safe_load(text.split("---", 2)[1])
        if (not isinstance(metadata, dict) or metadata.get("name") != name
                or not isinstance(metadata.get("description"), str)
                or not metadata["description"].strip()
                or metadata.get("disable-model-invocation") is True):
            raise ValueError(f"role skill must have matching name, description and enabled preload: {skill}")
        description = metadata["description"]
        if host == "codex":
            prompt = (f"Read {relative}/skills/{name}/SKILL.md and execute the current bounded assignment "
                      "using that skill. You are already the delegated agent; load it as instructions "
                      "instead of invoking a fork or spawning a replacement merely to activate it.")
            values = {"name": name, "description": description, "model": model,
                      "model_reasoning_effort": effort, "developer_instructions": prompt}
            content = "".join(f"{key} = {json.dumps(value, ensure_ascii=False)}\n"
                              for key, value in values.items())
            tomllib.loads(content)
            files[workspace / ".codex/agents" / f"{name}.toml"] = content
        elif host == "claude":
            front = {"name": name, "description": description, "model": model,
                     "effort": effort, "tools": tools, "skills": [name]}
            prompt = (f"Execute the current bounded assignment using the already-preloaded {name} "
                      "instructions. You are already the delegated agent; do not invoke the skill again.")
            content = "---\n" + yaml.safe_dump(front, sort_keys=False) + "---\n\n" + prompt + "\n"
            files[workspace / ".claude/agents" / f"{name}.md"] = content
        else:
            raise ValueError(f"unknown host: {host}")
    return files


def install(files: dict[Path, str], *, apply: bool = False) -> list[str]:
    # Check all collisions before creating any files, including dangling links.
    for path, content in files.items():
        workspace = path.parents[2].resolve()
        if not path.resolve().is_relative_to(workspace):
            raise ValueError(f"role path escapes the workspace through a symlink: {path}")
        if path.is_symlink() or (path.exists() and (not path.is_file() or path.read_text() != content)):
            raise ValueError(f"preserve existing role; merge manually: {path}")
    changes = [str(path) for path in files if not path.exists()]
    if apply:
        for path, content in files.items():
            if path.exists():
                continue
            path.parent.mkdir(parents=True, exist_ok=True)
            with path.open("x", encoding="utf-8") as stream:
                stream.write(content)
    return changes


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workspace", type=Path, required=True)
    parser.add_argument("--host", choices=("codex", "claude"), required=True)
    parser.add_argument("--model", required=True)
    parser.add_argument("--effort", required=True)
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    try:
        files = render_roles(args.workspace, args.host, args.model, args.effort)
        changes = install(files, apply=args.apply)
    except (ValueError, OSError) as exc:
        parser.exit(2, f"error: {exc}\n")
    print(json.dumps({"applied": args.apply, "create": changes,
                      "unchanged": len(files) - len(changes)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
