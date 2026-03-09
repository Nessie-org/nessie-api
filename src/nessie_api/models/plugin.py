from typing import Any, Callable


class NoAvailablePluginError(Exception):
    pass


# TODO : Intent is just a placeholder for now
class Action:
    def __init__(self, name: str, payload: Any):
        self.name = name
        self.payload = payload


ActionHandlerMap = dict[str, Callable[[Action], Any]]
PluginData = tuple[ActionHandlerMap, list[str]]


class Plugin:
    def __init__(
        self,
        name: str,
        handlers: ActionHandlerMap,
        requires: list[str] = [],
    ):
        self.name = name
        self.handlers = handlers
        self.requires = requires

    def activate(self):
        print(f"Activating plugin: {self.name}")

    def deactivate(self):
        print(f"Deactivating plugin: {self.name}")

    @property
    def provided_actions(self) -> list[str]:
        return list(self.handlers.keys())

    def handle(self, action: Action) -> bool:
        for action_name, handler in self.handlers.items():
            if action_name == action.name:
                print(f"Handling action: {action.name} with plugin: {self.name}")
                handler(action)
                return True
        return False


def plugin(name: str) -> Any:

    def inner(
        f: Callable[[], PluginData],
    ) -> Callable[[], Plugin]:
        def wrapper() -> Plugin:
            handlers, requires = f()
            return Plugin(name=name, handlers=handlers, requires=requires)

        return wrapper

    return inner
