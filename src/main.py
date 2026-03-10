from importlib.metadata import entry_points
from nessie_api.models.plugin import plugin

if __name__ == "__main__":

    def main():
        print("Hello from nessie!")
        plugins = entry_points(group="nessie_plugins")
        print(f"Found {len(plugins)} plugins.")
        for plugin_entry in plugins:
            plugin_instance = plugin_entry.load()()
            plugin_instance.activate()
            plugin_instance.deactivate()

    main()
