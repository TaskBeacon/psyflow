from __future__ import annotations

import shutil
import tempfile
from pathlib import Path

import click
import importlib.resources as pkg_res
from cookiecutter.main import cookiecutter

from .qa_cli import main as qa_command
from .sim_cli import main as sim_command


def _render_template(project_name: str, cwd: Path, *, in_place: bool) -> Path:
    tmpl_dir = pkg_res.files("psyflow.templates") / "cookiecutter-psyflow"
    extra = {"project_name": project_name}
    if not in_place:
        cookiecutter(str(tmpl_dir), output_dir=str(cwd), no_input=True, extra_context=extra)
        return cwd / project_name

    tmp = Path(tempfile.mkdtemp(prefix="psyflow-"))
    try:
        cookiecutter(str(tmpl_dir), output_dir=str(tmp), no_input=True, extra_context=extra)
        rendered = tmp / project_name
        overwrite_all = False
        for item in rendered.iterdir():
            dest = cwd / item.name
            if dest.exists() and not overwrite_all:
                resp = input(
                    f"WARNING: Existing '{item.name}' detected. Overwrite this and all remaining? [y/N]: "
                ).strip().lower()
                if resp == "y":
                    overwrite_all = True
                else:
                    click.echo(f"  Skipping '{item.name}'")
                    continue
            if item.is_dir():
                shutil.copytree(item, dest, dirs_exist_ok=overwrite_all)
            else:
                shutil.copy2(item, dest)
    finally:
        shutil.rmtree(tmp)
    return cwd


@click.group(context_settings={"help_option_names": ["-h", "--help"]})
def main() -> None:
    """psyflow command-line tools."""


@main.command("init")
@click.argument("project_name", required=False)
def init(project_name: str | None) -> None:
    """Create a new PsychoPy task from the bundled template."""
    cwd = Path.cwd()
    in_place = project_name is None or project_name == cwd.name
    name = cwd.name if in_place else str(project_name)
    out = _render_template(name, cwd, in_place=in_place)
    click.echo(f"Initialized project: {out}")


main.add_command(qa_command, name="qa")
main.add_command(sim_command, name="sim")


if __name__ == "__main__":
    main()
