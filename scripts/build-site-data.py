from __future__ import annotations

import ast
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

try:
    import tomllib  # type: ignore[attr-defined]
except ModuleNotFoundError:  # pragma: no cover
    tomllib = None


ROOT = Path(__file__).resolve().parents[1]
WEBSITE_DATA = ROOT / "website" / "src" / "data" / "generated"
REPO_URL = "https://github.com/TaskBeacon/psyflow/blob/main"


@dataclass
class ExportSpec:
    name: str
    module: str
    source_module: str


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def parse_pyproject() -> dict[str, Any]:
    if tomllib is not None:
        with (ROOT / "pyproject.toml").open("rb") as handle:
            data = tomllib.load(handle)
        project = data.get("project", {})
        return {
            "name": project.get("name"),
            "version": project.get("version"),
            "description": project.get("description"),
            "requires_python": project.get("requires-python"),
            "scripts": project.get("scripts", {}),
        }

    text = read_text(ROOT / "pyproject.toml")
    project_block = re.search(r"(?ms)^\[project\]\s*(.*?)^\[", text + "\n[", re.MULTILINE)
    scripts_block = re.search(r"(?ms)^\[project\.scripts\]\s*(.*?)^\[", text + "\n[", re.MULTILINE)

    def _kv(block: str, key: str) -> str | None:
        match = re.search(rf'(?m)^{re.escape(key)}\s*=\s*"([^"]*)"', block)
        return match.group(1) if match else None

    scripts: dict[str, str] = {}
    if scripts_block:
        for line in scripts_block.group(1).splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            scripts[key.strip()] = value.strip().strip('"')

    project_text = project_block.group(1) if project_block else ""
    return {
        "name": _kv(project_text, "name"),
        "version": _kv(project_text, "version"),
        "description": _kv(project_text, "description"),
        "requires_python": _kv(project_text, "requires-python"),
        "scripts": scripts,
    }


def module_file(module_name: str) -> Path:
    rel = module_name.replace(".", "/")
    py = ROOT / f"{rel}.py"
    if py.exists():
        return py
    init = ROOT / rel / "__init__.py"
    if init.exists():
        return init
    raise FileNotFoundError(f"Cannot resolve module file for {module_name}")


def doc_summary(module_name: str, symbol: str | None = None) -> str:
    path = module_file(module_name)
    tree = ast.parse(read_text(path), filename=str(path))

    if symbol is None:
        doc = ast.get_docstring(tree)
        return (doc or "").strip().splitlines()[0] if doc else ""

    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)) and node.name == symbol:
            doc = ast.get_docstring(node)
            return (doc or "").strip().splitlines()[0] if doc else ""
    return ""


def parse_dunder_all(module_name: str) -> list[str]:
    tree = ast.parse(read_text(module_file(module_name)))
    for node in tree.body:
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == "__all__":
                    if isinstance(node.value, (ast.List, ast.Tuple)):
                        values: list[str] = []
                        for elt in node.value.elts:
                            if isinstance(elt, ast.Constant) and isinstance(elt.value, str):
                                values.append(elt.value)
                        return values
    return []


def parse_import_map(module_name: str) -> dict[str, str]:
    tree = ast.parse(read_text(module_file(module_name)))
    base = module_name
    result: dict[str, str] = {}
    for node in tree.body:
        if isinstance(node, ast.ImportFrom):
            if node.level == 0 or node.module is None:
                continue
            source = base
            if node.level == 1:
                source = f"{base}.{node.module}"
            for alias in node.names:
                result[alias.asname or alias.name] = source
    return result


def source_url(module_name: str) -> str:
    path = module_file(module_name).relative_to(ROOT).as_posix()
    return f"{REPO_URL}/{path}"


def resolve_symbol_source(module_name: str, symbol: str) -> str:
    current_module = module_name
    current_symbol = symbol
    seen: set[tuple[str, str]] = set()

    while (current_module, current_symbol) not in seen:
        seen.add((current_module, current_symbol))

        source_module = None
        try:
            import_map = parse_import_map(current_module)
        except FileNotFoundError:
            import_map = {}
        source_module = import_map.get(current_symbol)

        if source_module is None:
            try:
                lazy_map = {
                    item.name: item.source_module
                    for item in parse_lazy_attrs(current_module)
                }
            except FileNotFoundError:
                lazy_map = {}
            source_module = lazy_map.get(current_symbol)

        if source_module is None or source_module == current_module:
            return current_module

        current_module = source_module

    return current_module


def parse_lazy_attrs(module_name: str) -> list[ExportSpec]:
    text = read_text(module_file(module_name))
    pattern = re.compile(r'"([^"]+)":\s*\("([^"]+)",\s*"([^"]+)"\)')
    items: list[ExportSpec] = []
    for name, source_module, _attr_name in pattern.findall(text):
        items.append(
            ExportSpec(
                name=name,
                module=module_name,
                source_module=source_module,
            )
        )
    return items


def build_inventory() -> list[dict[str, Any]]:
    groups: list[dict[str, Any]] = []

    root_exports = parse_lazy_attrs("psyflow")
    groups.append(
        {
            "module": "psyflow",
            "summary": doc_summary("psyflow"),
            "exports": [
                {
                    "name": item.name,
                    "source_module": resolve_symbol_source(item.source_module, item.name),
                    "summary": doc_summary(resolve_symbol_source(item.source_module, item.name), item.name),
                    "source_url": source_url(resolve_symbol_source(item.source_module, item.name)),
                }
                for item in root_exports
            ],
        }
    )

    for module_name in ["psyflow.utils", "psyflow.io", "psyflow.qa", "psyflow.sim"]:
        lazy_exports = parse_lazy_attrs(module_name)
        if lazy_exports:
            exports = [
                {
                    "name": item.name,
                    "source_module": item.source_module,
                    "summary": doc_summary(item.source_module, item.name),
                    "source_url": source_url(item.source_module),
                }
                for item in lazy_exports
            ]
        else:
            export_names = parse_dunder_all(module_name)
            import_map = parse_import_map(module_name)
            exports = []
            for name in export_names:
                source_module = import_map.get(name, module_name)
                exports.append(
                    {
                        "name": name,
                        "source_module": source_module,
                        "summary": doc_summary(source_module, name),
                        "source_url": source_url(source_module),
                    }
                )
        groups.append(
            {
                "module": module_name,
                "summary": doc_summary(module_name),
                "exports": exports,
            }
        )

    return groups


def parse_changelog() -> list[dict[str, Any]]:
    text = read_text(ROOT / "ChangLog.md")
    pattern = re.compile(r"^##\s+([0-9.]+)\s+\(([^)]+)\)\s*$", re.MULTILINE)
    matches = list(pattern.finditer(text))
    releases: list[dict[str, Any]] = []

    for index, match in enumerate(matches):
        version = match.group(1)
        date = match.group(2)
        start = match.end()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        chunk = text[start:end]

        summary_items: list[str] = []
        summary_match = re.search(r"^###\s+Summary\s*$", chunk, re.MULTILINE)
        if summary_match:
            summary_start = summary_match.end()
            next_heading = re.search(r"^###\s+", chunk[summary_start:], re.MULTILINE)
            summary_end = summary_start + next_heading.start() if next_heading else len(chunk)
            summary_block = chunk[summary_start:summary_end]
            for line in summary_block.splitlines():
                line = line.strip()
                if line.startswith("- "):
                    summary_items.append(line[2:].strip())
        releases.append(
            {
                "version": version,
                "date": date,
                "summary": summary_items[:8],
            }
        )
    return releases


def write_json(name: str, payload: Any) -> None:
    WEBSITE_DATA.mkdir(parents=True, exist_ok=True)
    path = WEBSITE_DATA / name
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def main() -> None:
    project = parse_pyproject()
    releases = parse_changelog()
    inventory = build_inventory()
    latest_release = releases[0] if releases else None

    write_json(
        "site-data.json",
        {
            "project": project,
            "latest_release": latest_release,
            "release_count": len(releases),
            "module_count": len(inventory),
        },
    )
    write_json("cli-commands.json", project["scripts"])
    write_json("api-inventory.json", inventory)
    write_json("changelog.json", releases)


if __name__ == "__main__":
    main()
