from actions.handlers.base import Action


class LogAction(Action):
    def __init__(self, label: str):
        self.label = label

    def execute(self) -> None:
        print(f"Triggered: {self.label}")
