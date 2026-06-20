import webbrowser

from actions.handlers.base import Action
from actions.factory import ActionFactory


@ActionFactory.register("open_url")
class OpenUrlAction(Action):
    def __init__(self, url: str):
        self.url = url

    def execute(self) -> None:
        webbrowser.open(self.url)