from actions.handlers.base import Action
from actions.factory import ActionFactory
from actions.handlers.log import LogAction


class ActionResolver:
    @classmethod
    def resolve(cls, config: dict | str) -> Action:
        if isinstance(config, dict):
            return ActionFactory.create(config)
        return LogAction(str(config))
