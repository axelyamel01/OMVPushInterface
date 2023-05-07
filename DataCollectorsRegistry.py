# Module that contains all the helper functions to handle data collection
import DataCollectors

# Module that handles the messages
from MessagesHandler import MessagesHandler

# Helper function for register new data collectors. Just add the following:
#
#   message_handler.add_collector(DataCollectors.collector_function, parameters)
def generate_data_collectors_registry(message_handler, args):
    if type(message_handler) != MessagesHandler:
        sys.exit("Error: Issue handling the registry for the messages handler")

    debug_collector = args.debug or args.emulate or args.verbose

    # Run the CPU temperature collector with 70 C as the critical temperature
    message_handler.add_collector(DataCollectors.temperature_collector, 70, debug_collector)

    # Run the updates needed collector, temporary data will be stored in /var/tmp/"
    message_handler.add_collector(DataCollectors.updates_available_collector, "/var/tmp/", debug_collector)

    # collector for disk space
    message_handler.add_collector(DataCollectors.disk_space_collector, "/", "root-drive", "/var/tmp/", 20.0, 7, debug_collector)

    # TODO: Collectors needed
    #   1) Disks temperature