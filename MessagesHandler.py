from MessageGenerator import MessageGenerator

# Class that handles all message generators. It basically is a list that
# contains message gerators and runs them
class MessagesHandler:
    def __init__(self, simplepush_devices, system_addresses, extra_modes):
        self.__simplepush_devices = simplepush_devices
        self.__debug = extra_modes["debug"] or extra_modes["verbose"]
        self.__send_message = extra_modes["emulation"] or extra_modes["verbose"] or (not extra_modes["debug"])
        self.__system_addresses = system_addresses
        self.__collectors = []

    def add_collector(self, collector_func, *args):
        message_gen = MessageGenerator(self.__simplepush_devices,  self.__system_addresses, self.__debug, self.__send_message, collector_func)
        self.__collectors.append([message_gen, args])

    def run(self):
        for collector in self.__collectors:
            collector[0].generate_message(*collector[1])
