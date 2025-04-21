import sys
from pathlib import Path
import click
from cookiecutter.main import cookiecutter
import importlib.resources as pkg_res

@click.command(context_settings={"ignore_unknown_options": True})
@click.argument("project_name", required=False)
def climain(project_name):
    """
    psyflow-init [PROJECT_NAME]

    If PROJECT_NAME is omitted, or equals the current folder name,
    we scaffold *in place* (i.e. into CWD). Otherwise we create a
    new folder PROJECT_NAME under CWD.
    """
    # locate your bundled template
    tmpl_dir = pkg_res.files("psyflow.templates") / "cookiecutter-psyflow"

    cwd = Path.cwd()
    # decide where cookiecutter should put the project
    if project_name is None:
        # no arg => in‐place
        project_name = cwd.name
        output_dir = cwd.parent
    elif project_name == cwd.name:
        # same name as current dir => in‐place
        output_dir = cwd.parent
    else:
        # new subfolder under cwd
        output_dir = None  # cookiecutter default is CWD

    # run cookiecutter
    cookiecutter(
        str(tmpl_dir),
        no_input=True,
        extra_context={"project_name": project_name},
        output_dir=str(output_dir) if output_dir else None,
    )

if __name__ == "__main__":
    climain()
