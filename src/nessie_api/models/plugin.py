from typing import Any, Callable


class NoAvailablePluginError(Exception):
    pass


class Action:
    def __init__(self, name: str, payload: Any):
        self.name = name
        self.payload = payload


ActionHandlerMap = dict[str, Callable[[Action], Any]]


class Plugin:
    def __init__(
        self,
        name: str,
        handlers: ActionHandlerMap,
        requires: list[str] = [],
        setup_requires: dict[str, type] = {},
        verbose: bool = False,
    ):
        self.name = name
        self.handlers = handlers
        self.requires = requires
        self.setup_requires = setup_requires
        self.verbose = verbose

    def activate(self):
        print(f"Activating plugin: {self.name}")

    def deactivate(self):
        print(f"Deactivating plugin: {self.name}")

    @property
    def provided_actions(self) -> list[str]:
        return list(self.handlers.keys())

    def handle(self, action: Action, setup: dict[str, Any] = None) -> Any:
        handler = self.handlers.get(action.name)
        if handler:
            if self.verbose:
                print(f"Handling action: {action.name} with plugin: {self.name}")
            if setup:
                if self.verbose:
                    print(f"Using setup: {setup} for action: {action.name}")
                return handler(action, setup)
            else:
                return handler(action)


def plugin(name: str, verbose: bool = False) -> Any:

    def inner(
        f: Callable[[], dict[str, Any]],
    ) -> Callable[[], Plugin]:
        def wrapper() -> Plugin:
            data = f()
            handlers = data.get("handlers", {})
            requires = data.get("requires", [])
            setup_requires = data.get("setup_requires", {})
            return Plugin(
                name=name,
                handlers=handlers,
                requires=requires,
                setup_requires=setup_requires,
                verbose=verbose,
            )

        return wrapper

    return inner
