from nessie_api.models import plugin


@plugin(name="test_plugin")
def test_plugin_factory():
    def test_handler(action):
        print(f"Handling action: {action.name} with payload: {action.payload}")

    handlers = {"test_action": test_handler}
    requires = []
    return handlers, requires
