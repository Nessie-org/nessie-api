from importlib.metadata import entry_points
from nessie_api.models.plugin import Action, plugin

if __name__ == "__main__":

    def main():
        print("Hello from nessie!")
        plugins = entry_points(group="nessie_plugins")
        print(f"Found {len(plugins)} plugins.")
        for plugin_entry in plugins:
            plugin_instance = plugin_entry.load()()
            plugin_instance.activate()
            action = Action(name="test_action", payload={"key": "value"})
            plugin_instance.handle(action, setup={"example_setup": "example_value"})
            plugin_instance.deactivate()

    main()
