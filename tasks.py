from sys import platform
from shutil import copy

from invoke import task

# Workaround for homebrew installation of Python (https://bugs.python.org/issue22490)
import os
os.environ.pop('__PYVENV_LAUNCHER__', None)

ROOT = os.path.dirname(os.path.realpath(__file__))

# Python commands's outputs are not rendering properly. Setting pty for *Nix system and
# "PYTHONUNBUFFERED" env var for Windows at True.
if platform == 'win32':
    PLATFORM_ARG = dict(env={'PYTHONUNBUFFERED': 'True'})
else:
    PLATFORM_ARG = dict(pty=True)


@task(optional=['option', 'flag'])
def manage(ctx, command, option=None, flag=None):
    """Shorthand to manage.py. inv manage [COMMAND] [-o OPTION] [-f FLAG]. ex: inv manage runserver -o 3000"""
    with ctx.cd(ROOT):
        if option:
            ctx.run(f"pipenv run python manage.py {command} {option}", **PLATFORM_ARG)
        elif flag:
            ctx.run(f"pipenv run python manage.py {command} --{flag}", **PLATFORM_ARG)
        else:
            ctx.run(f"pipenv run python manage.py {command}", **PLATFORM_ARG)


@task
def runserver(ctx):
    """Start a web server"""
    manage(ctx, "runserver")


@task
def migrate(ctx):
    """Updates database schema"""
    manage(ctx, "migrate")


@task
def makemigrations(ctx):
    """Creates new migration(s) for apps"""
    manage(ctx, "makemigrations")


@task
def test(ctx):
    """Run tests"""
    print("Running flake8")
    ctx.run("pipenv run flake8 pulseapi  --ignore=E722", **PLATFORM_ARG)
    print("Running tests")
    manage(ctx, "test")


@task
def setup(ctx):
    """Prepare your dev environment after a fresh git clone"""
    with ctx.cd(ROOT):
        print("Copying default environment variables")
        copy("sample.env", ".env")
        print("Installing Python dependencies")
        ctx.run("pipenv install --dev")
        print("Applying database migrations")
        ctx.run("inv migrate")
        print("Creating fake data")
        ctx.run("inv manage load_fake_data")
        print("Creating 'client_secrets.json' file")
        ctx.run("pipenv run python generate_client_secrets.py", **PLATFORM_ARG)
        # Windows doesn't support pty, skipping createsuperuser step
        if platform == 'win32':
            print("Done!\n"
                  "To finish your setup:\n"
                  "1. Set up a Google client here: https://console.developers.google.com/apis/credentials.\n"
                  "Then, open 'client_secrets.json' and edit 'client_id' and 'client_secret' with your Google "
                  "client's values.\n"
                  "2. Create a superuser by running 'pipenv run python manage.py createsuperuser'\n"
                  "When it's done, start your dev server by running 'inv runserver'. You can get a full list of inv "
                  "commands with 'inv -l'")
        else:
            print("Creating superuser")
            ctx.run("pipenv run python manage.py createsuperuser", pty=True)
            print("Done!\n"
                  "To finish your setup, set up a Google client here: "
                  "https://console.developers.google.com/apis/credentials.\n"
                  "Then, open 'client_secrets.json' and edit 'client_id' and 'client_secret' with your Google "
                  "client's values.\n"
                  "When it's done, start your dev server by running 'inv runserver'. You can get a full list of inv "
                  "commands with 'inv -l'")
