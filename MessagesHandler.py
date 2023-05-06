from MessageGenerator import MessageGenerator

# Class that handles all message generators. It basically is a list that
# contains message gerators and runs them
class MessagesHandler:
    def __init__(self, simplepush_devices, system_addresses, debug):
        self.__simplepush_devices = simplepush_devices
        self.__debug = debug
        self.__system_addresses = system_addresses
        self.__collectors = []

    def add_collector(self, collector_func, *args):
        message_gen = MessageGenerator(self.__simplepush_devices,  self.__system_addresses, self.__debug, collector_func)
        self.__collectors.append([message_gen, args])

    def run(self):
        for collector in self.__collectors:
            collector[0].generate_message(*collector[1])
