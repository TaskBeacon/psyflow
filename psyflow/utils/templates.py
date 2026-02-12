"""Template/scaffolding helper utilities."""

from cookiecutter.main import cookiecutter
import importlib.resources as pkg_res


def taps(task_name: str, template: str = "cookiecutter-psyflow"):
    """Generate a task skeleton using the bundled template."""
    tmpl_dir = pkg_res.files("psyflow.templates") / template
    cookiecutter(
        str(tmpl_dir),
        no_input=True,
        extra_context={"project_name": task_name},
    )
    return task_name

