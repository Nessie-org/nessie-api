from nessie_api.models import plugin


@plugin(name="test_plugin", verbose=True)
def test_plugin_factory():
    def test_handler(action, setup=None):
        print(
            f"(test plugin) Handling action: {action.name} with payload: {action.payload}"
        )
        if setup:
            print(
                f"(test plugin) Handling with setup: {setup} for action: {action.name}"
            )

    handlers = {"test_action": test_handler}
    requires = []
    setup_requires = {}
    ret_dict = {
        "handlers": handlers,
        "requires": requires,
        "setup_requires": setup_requires,
    }
    return ret_dict
