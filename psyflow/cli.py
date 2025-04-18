import click
from cookiecutter.main import cookiecutter
import importlib.resources as pkg_res

@click.command()
@click.argument("project_name")
def climain(project_name):
    # pkg_res.files("psyflow.templates") points at the 'templates/' package folder
    tmpl_dir = pkg_res.files("psyflow.templates") / "cookiecutter-psyflow"
    cookiecutter(
        str(tmpl_dir),
        no_input=True,
        extra_context={"project_name": project_name}
    )

if __name__ == "__main__":
    climain()
