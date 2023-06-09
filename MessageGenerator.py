import time

import simplepush

from Utils import Utils

# Class that use a data collector function to check if a message is
# needed. If so, then send it
class MessageGenerator:
    def __init__(self, simplepush_devices, system_addresses, debug, send_message, collector_func):
        self.__collector_func = collector_func
        self.__simplepush_devices = simplepush_devices
        self.__debug = debug
        self.__send_message = send_message
        self.__system_addresses = system_addresses

    # return true if the result is generated correctly
    def __bad_result(self, result):
        if type(result) != list or len(result) != 3:
            return True

        if type(result[0]) != bool or not result[0]:
            return True

        title = result[1]
        message = result[2]

        if type(title) != str or len(title) == 0:
            return True
        if type(message) != str or len(message) == 0:
            return True

        return False

    # Run the that collects the data
    def __collector_function(self, *args):
        result = [False, "", ""]
        if not args:
            result = self.__collector_func()
        else:
            result = self.__collector_func(*args)

        return result

    # Run the function that collects the data with the proper args
    #
    # In order to generate a message, the collectors function must return a
    # list with the following form
    #
    #   [True, "Title", "Message"]
    #
    # Use function self.__bad_result to check if your message is correct
    def generate_message(self, *args):
        result = self.__collector_func(*args)
        if not self.__bad_result(result):
            curr_title = result[1]
            curr_message = result[2]
            curr_message = curr_message + self.__generate_message_footer()
            if self.__send_message:
                for device in self.__simplepush_devices:
                    curr_key = device["key"]
                    curr_password = device["password"]
                    curr_salt = device["salt"]
                    simplepush.send(key=curr_key, password=curr_password, \
                            salt=curr_salt, title=curr_title, message=curr_message)

            if self.__debug:
                print(curr_title)
                print(curr_message)
                print("\n=========================================================\n")

    def __generate_message_footer(self):
        time_info = Utils().get_current_date_and_time()
        footer = "\nOMV Web link"
        if len(self.__system_addresses) == 1:
            footer = footer + ": " + self.__system_addresses[0][1] + "\n"
        elif len(self.__system_addresses) > 1:
            footer = footer + "s: \n"
            for sys_address in self.__system_addresses:
                footer = footer + "    " + u'\u2022' + " " + sys_address[0] + ": " + sys_address[1] + "\n"

        footer  = footer + time_info[0] + "\n" + time_info[1]
        return footer