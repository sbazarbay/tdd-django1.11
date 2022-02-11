from fabric.context_managers import settings, shell_env
from fabric.api import run


def _get_manage_dot_py(host):
    return f"~/sites/{host}/venv/bin/python ~/sites/{host}/manage.py"


def _get_server_env_vars(host):
    env_lines: str = run(f"cat ~/sites/{host}/.env")
    env_lines = env_lines.splitlines()
    return dict(line.split("=") for line in env_lines if line)


def reset_database(host):
    manage_dot_py = _get_manage_dot_py(host)
    with settings(host_string=f"cheena@{host}"):
        run(f"{manage_dot_py} flush --noinput")


def create_session_on_server(host, email):
    manage_dot_py = _get_manage_dot_py(host)
    with settings(host_string=f"cheena@{host}"):
        env_vars = _get_server_env_vars(host)
        with shell_env(**env_vars):
            session_key: str = run(f"{manage_dot_py} create_session {email}")
            return session_key.strip()
