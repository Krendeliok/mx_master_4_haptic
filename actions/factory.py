from typing import Callable

from actions.handlers.base import Action


class ActionFactory:
    _registry: dict[str, type[Action]] = {}

    @classmethod
    def register(cls, type_name: str) -> Callable[[type[Action]], type[Action]]:
        def decorator(action_class: type[Action]) -> type[Action]:
            cls._registry[type_name] = action_class
            return action_class
        return decorator

    @classmethod
    def create(cls, config: dict) -> Action:
        action_type = config.pop("type")
        action_class = cls._registry.get(action_type)
        if action_class is None:
            raise ValueError(f"Unknown action type: {action_type!r}")
        return action_class(**config)
