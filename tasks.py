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
    PLATFORM_ARG = dict(env={'PYTHONUNBUFFERED': 'True', 'PIPENV_DONT_LOAD_ENV': '1'})
else:
    PLATFORM_ARG = dict(pty=True, env={'PIPENV_DONT_LOAD_ENV': '1'})


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
    ctx.run("pipenv run flake8 pulseapi", **PLATFORM_ARG)
    print("Running tests")
    manage(ctx, "test")


@task
def setup(ctx):
    """Automate project's configuration and dependencies installation"""
    setup_finish_instructions = (
      "Done!\n"
      "You can get a full list of inv commands with 'inv -l'\n\n"
      "If you only want to login with Django admin credentials, your setup is complete and you can run the server using 'inv runserver',\n"
      "To enable login using Google and/or Github:\n"
      "1. Set up a Google client here: https://console.developers.google.com/apis/credentials. Optionally also create a Github client here: https://github.com/settings/applications/new.\n The Authorized domain is http://test.example.com:8000 and the redirect url is http://test.example.com:8000/accounts/google/login/callback/ (replace google with github for the github redirect url).\n"
      "2. Create a superuser by running 'pipenv run python manage.py createsuperuser'\n"
      "3. When it's done, start your dev server by running 'inv runserver'.\n"
      "4. Login to the admin interface as a superuser and create an instance each of 'Social Application', one for Google and one for Github with their client ids and secrets filled in.\n"
      "5. You can now login using Google and/or Github.\n"
    )
    with ctx.cd(ROOT):
        if os.path.isfile(".env"):
            print("'.env' file found:\n"
                  "- If you want to completely redo your dev setup, delete your '.env' file and your database. Then "
                  "run 'inv setup' again.\n"
                  "- If you want to catch up with the latest changes, like after a 'git pull', run 'inv catch-up' "
                  "instead.")
        else:
            print("Copying default environment variables")
            copy("sample.env", ".env")
            print("Installing Python dependencies")
            ctx.run("pipenv install --dev")
            print("Applying database migrations")
            ctx.run("inv migrate")
            print("Creating fake data")
            ctx.run("inv manage load_fake_data")
            # Windows doesn't support pty, skipping createsuperuser step
            if platform == 'win32':
                print(setup_finish_instructions)
            else:
                print("Creating superuser")
                ctx.run("pipenv run python manage.py createsuperuser", pty=True)
                print(setup_finish_instructions)


@task()
def catch_up(ctx):
    """Install dependencies and apply migrations"""
    print("Installing Python dependencies")
    ctx.run("pipenv install --dev")
    print("Applying database migrations")
    ctx.run("inv migrate")
