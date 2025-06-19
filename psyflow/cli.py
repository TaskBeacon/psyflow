import sys
import tempfile
import shutil
from pathlib import Path

import click
from cookiecutter.main import cookiecutter
from cookiecutter.exceptions import OutputDirExistsException
import importlib.resources as pkg_res

@click.command()
@click.argument("project_name", required=False)
def climain(project_name):
    """Create a new PsychoPy task from the bundled template.

    Parameters
    ----------
    project_name : str, optional
        Name of the project directory. If omitted or equal to the current
        directory name, files are generated in place.

    Returns
    -------
    None
        Files are created on disk for their side effect.

    Examples
    --------
    >>> psyflow-init mytask
    """
    # 1. Locate our bundled template
    tmpl_dir = pkg_res.files("psyflow.templates") / "cookiecutter-psyflow"

    cwd = Path.cwd()
    cur_name = cwd.name

    # 2. Decide: in-place vs new-folder
    in_place = (project_name is None) or (project_name == cur_name)

    # 3. Choose final name
    if in_place:
        name = cur_name
    else:
        name = project_name

    # 4. Cookiecutter kwargs
    extra = {"project_name": name}
    cc_kwargs = dict(
        no_input=True,
        extra_context=extra
    )

    if not in_place:
        # Standard behavior: create a new ./<name> folder
        cookiecutter(str(tmpl_dir), output_dir=str(cwd), **cc_kwargs)
        return

    # 5. In-place mode: render to a temp dir, then copy up
    tmp = Path(tempfile.mkdtemp(prefix="psyflow-"))
    try:
        cookiecutter(str(tmpl_dir), output_dir=str(tmp), **cc_kwargs)
        rendered = tmp / name

        # Copy everything from rendered/* → cwd/*
        for item in rendered.iterdir():
            dest = cwd / item.name
            if item.is_dir():
                shutil.copytree(item, dest, dirs_exist_ok=True)
            else:
                shutil.copy2(item, dest)

        click.echo(f"Initialized project in place: {cwd}")
    finally:
        shutil.rmtree(tmp)

if __name__ == "__main__":
    climain()
