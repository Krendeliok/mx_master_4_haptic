import subprocess

from actions.handlers.base import Action
from actions.factory import ActionFactory


@ActionFactory.register("shell_command")
class ShellCommandAction(Action):
    def __init__(self, command: str):
        self.command = command

    def execute(self) -> None:
        subprocess.Popen(
            self.command,
            shell=True,
            start_new_session=True,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
