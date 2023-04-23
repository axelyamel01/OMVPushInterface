# module for parsing args
import argparse

import sys
import pathlib
import copy
import os

# class to handle all the messages
from MessagesHandler import MessagesHandler

# Module for handling the data collectors
from DataCollectorsRegistry import generate_data_collectors_registry

def args_parser():
    working_dir = str(pathlib.Path(__file__).parent.resolve())
    parser = argparse.ArgumentParser(description='Push notifications system for OMV')
    parser.add_argument("-c", "--config", help="Config file that contains the credentials for Simplepush", \
                        default=working_dir + "/config/push-notifications-system.cfg")
    parser.add_argument("-d", "--debug", help="Enable debug mode, messages will be printed and not sent", \
                        action='store_true')
    parser.add_argument("-e", "--emulate", help="Enable emulation mode, message generated by debug mode will be sent rather than print", \
                        action='store_true')

    args = parser.parse_args()
    if not os.path.isfile(args.config):
        sys.exit("Error: Simplepush config file " + args.config + " not found")

    return args

# Parse the configuration file. Check config/push-notifications-system.cfg for
# a template
def parse_config_file(config_file_path):
    config_file = open(config_file_path, "r")
    allowed_sections = {
        "simplepush-device" : ["key", "password", "salt"],
        "omv-system-info" : ["omv-hostname", "omv-domain-name", "omv-port", "omv-web-protocol"]
    }

    omv_system_info = {
            "omv-hostname" : "",
            "omv-domain-name" : "",
            "omv-port" : "",
            "omv-web-protocol" : ""
    }

    simplepush_device = {
        "key" : "",
        "password" : "",
        "salt" : ""
    }

    simplepush_devices = []

    lines = config_file.readlines()

    counter = 1
    curr_section = ""
    omv_system_set = False
    for line in lines:
        strip_line = line.strip()
        if strip_line == "":
            continue

        if strip_line[0] == '#':
            continue

        split_line = strip_line.split()
        key = split_line[0].rstrip(split_line[0][-1])
        if key in allowed_sections:
            if curr_section == "omv-system-info":
                if omv_system_info["omv-hostname"] == "" or omv_system_info["omv-domain-name"] == "":
                    config_file.close()
                    sys.exit("Error: Incorrect OMV system configuration in config file. " \
                             "Check around line " + str(counter))

            elif curr_section == "simplepush-device":
                curr_device = simplepush_devices[-1]
                if curr_device["key"] == "" or curr_device["password"] == "" or curr_device["salt"] == "":
                    config_file.close()
                    sys.exit("Error: Incorrect Simplepush configuration in config file. " + \
                             "Check around line " + str(counter))


            if key == "simplepush-device":
                new_device = copy.deepcopy(simplepush_device)
                simplepush_devices.append(new_device)

            elif key == "omv-system-info":
                if omv_system_set == True:
                    config_file.close()
                    sys.exit("Error: Double OMV system configuration in config file. " + \
                             "Check around line " + str(counter))

                omv_system_set = True

            else:
                config_file.close()
                sys.exit("Error: Incorrect section in config file. Check around line " + str(counter))

            curr_section = key

        elif curr_section != "" and key in allowed_sections[curr_section]:
            if curr_section == "omv-system-info":
                if omv_system_info[key] != "":
                    config_file.close()
                    sys.exit("Error: Repeated entry for OMV system configuration in config file. Check around line " + str(counter))

                omv_system_info[key] = split_line[1]

            elif curr_section == "simplepush-device":
                if simplepush_devices[-1][key] != "":
                    config_file.close()
                    sys.exit("Error: Repeated entry for Simplepush device configuration in config file. Check around line " + str(counter))

                simplepush_devices[-1][key] = split_line[1]

            else:
                config_file.close()
                sys.exit("Error: Something went wrong parsing the config file. Check around line " + str(counter))

        else:
            config_file.close()
            sys.exit("Error: Incorrect entry in config file. Check around line " + str(counter))

        counter = counter + 1

    config_file.close()

    # Exit if there is no device registered
    if len(simplepush_devices) == 0:
        sys.exit("Error: No Simplepush device found in the config file")

    # Set the defaults not found
    if omv_system_info["omv-web-protocol"] == "":
        omv_system_info["omv-web-protocol"] = "http"

    if omv_system_info["omv-port"] == "":
        omv_system_info["omv-port"] = 80

    return [simplepush_devices, omv_system_info]

def generate_system_web_address(omv_system_info):
    # TODO: Perhaps we don't need to specify this in the config file. I suspect
    # there is a way to query the OS and get all the OMV info needed
    omv_hostname = omv_system_info["omv-hostname"]
    omv_port = omv_system_info["omv-port"]
    omv_domain_name = omv_system_info["omv-domain-name"]
    omv_web_protocol = omv_system_info["omv-web-protocol"]

    if omv_hostname == "" or omv_port == "" or omv_domain_name == "" or omv_web_protocol == "":
        sys.exit("Error: Incorrect OMV system information.")

    system_web_address = omv_web_protocol + "://" + omv_hostname + "." + omv_domain_name
    if omv_port != "80":
        system_web_address = system_web_address + ":" + omv_port

    return system_web_address

def main():

    args = args_parser()

    welcome_string = "Running OMV push notifications interface "
    extra_modes = []
    if args.debug:
        extra_modes.append("debug")
    if args.emulate:
        extra_modes.append("emulation")

    modes = ""
    if len(extra_modes) > 0:
        modes = "(modes enabled: "
        for mode in extra_modes:
            modes = modes + mode + " |"
        modes = modes[:-2] + ")"

    welcome_string = welcome_string + modes
    print(welcome_string)

    simplepush_devices, omv_system_info = parse_config_file(args.config)
    system_address = generate_system_web_address(omv_system_info)

    if args.debug or args.emulate:
        print("\nSimplepush devices registered:")
        counter = 1
        for device in simplepush_devices:
            print("    * Simplepush device " + str(counter) + ":")
            print("        - Key: " + device["key"])
            print("        - Password: " + '*'*len(device["password"]))
            print("        - Salt: " + device["salt"] + "\n")
            counter = counter + 1

        print("OMV web address: " + system_address + "\n")

        if args.debug:
            print("Messages won't be sent, they will be printed in the following format:\n")
            print("Line 1: Title")
            print("Line 2: Message body line 1")
            print("Line 3: Message body line 2")
            print("\n=========================================================\n")

    debug_collector = args.debug or args.emulate
    message_handler = MessagesHandler(simplepush_devices, system_address, args.debug)
    generate_data_collectors_registry(message_handler, args)
    message_handler.run()

    print("OMV push notifications done")

if __name__ == "__main__":
    main()
