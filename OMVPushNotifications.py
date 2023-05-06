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
        "omv-system-address" : ["name", "hostname", "domain-name", "port", "web-protocol", "ip"]
    }

    omv_system_info = {
            "name" : "",
            "hostname" : "",
            "domain-name" : "",
            "port" : "",
            "web-protocol" : "",
            "ip" : ""
    }

    simplepush_device = {
        "key" : "",
        "password" : "",
        "salt" : ""
    }

    simplepush_devices = []
    omv_systems = []

    lines = config_file.readlines()

    counter = 0
    curr_section = ""
    omv_system_name_found = False

    for line in lines:
        counter = counter + 1
        strip_line = line.strip()
        if strip_line == "":
            continue

        if strip_line[0] == '#':
            continue

        split_line = strip_line.split()
        key = split_line[0].rstrip(split_line[0][-1])
        if key in allowed_sections:
            if curr_section == "omv-system-address":
                curr_omv_system = omv_systems[-1]
                good_omv_config = curr_omv_system["hostname"] != "" and curr_omv_system["domain-name"] != ""
                if not good_omv_config:
                    good_omv_config = curr_omv_system["ip"] != ""
                if not good_omv_config:
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

            elif key == "omv-system-address":
                new_omv_system = copy.deepcopy(omv_system_info)
                new_omv_system["name"] = "OMV-" + str(len(omv_systems) + 1)
                omv_system_name_found = False
                omv_systems.append(new_omv_system)

            curr_section = key

        elif curr_section != "" and key in allowed_sections[curr_section]:
            if len(split_line) < 2:
                config_file.close()
                sys.exit("Error: Empty field in config file. Check around line " + str(counter))
            if curr_section == "omv-system-address":
                good_key = omv_systems[-1][key] == ""
                if not good_key and key == "name" and not omv_system_name_found:
                    good_key = True
                    omv_system_name_found = True
                if not good_key:
                    config_file.close()
                    sys.exit("Error: Repeated entry for OMV address configuration in config file. Check around line " + str(counter))

                omv_systems[-1][key] = split_line[1]

            elif curr_section == "simplepush-device":
                if simplepush_devices[-1][key] != "":
                    config_file.close()
                    sys.exit("Error: Repeated entry for Simplepush device configuration in config file. Check around line " + str(counter))

                simplepush_devices[-1][key] = split_line[1]

        else:
            config_file.close()
            sys.exit("Error: Incorrect entry in config file. Check around line " + str(counter))

    config_file.close()

    # Exit if there is no device was registered
    if len(simplepush_devices) == 0:
        sys.exit("Error: No Simplepush device found in the config file")

    # Exit if there is no system was registered
    if len(omv_systems) == 0:
        sys.exit("Error: No OMV system found in the config file")

    # Set the defaults not found
    for omv_system in omv_systems:
        if omv_system["web-protocol"] == "":
            omv_system["web-protocol"] = "http"

        if omv_system["port"] == "":
            omv_system["port"] = 80

    return [simplepush_devices, omv_systems]

def generate_system_web_address(system_info):
    # TODO: Perhaps we don't need to specify this in the config file. I suspect
    # there is a way to query the OS and get all the OMV info needed
    hostname = system_info["hostname"]
    port = system_info["port"]
    domain_name = system_info["domain-name"]
    web_protocol = system_info["web-protocol"]
    ip = system_info["ip"]

    if port == "" or web_protocol == "":
        return ""

    system_web_address = web_protocol + "://"
    if hostname and domain_name:
        system_web_address = system_web_address + hostname + "." + domain_name
    elif ip:
        system_web_address = system_web_address + ip
    else:
        return ""

    if port != "80":
        system_web_address = system_web_address + ":" + port

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
    system_addresses = []
    for omv_address in omv_system_info:
        system_address = generate_system_web_address(omv_address)
        if system_address == "":
            sys.exit("Error: Incorrect OMV system information.")
        system_addresses.append([omv_address["name"], system_address])


    if args.debug or args.emulate:
        print("\nSimplepush devices registered:")
        counter = 1
        for device in simplepush_devices:
            print("    * Simplepush device " + str(counter) + ":")
            print("        - Key: " + device["key"])
            print("        - Password: " + '*'*len(device["password"]))
            print("        - Salt: " + device["salt"] + "\n")
            counter = counter + 1

        if len(system_addresses) == 1:
            print("OMV web address found: " + system_addresses[0][1])
        elif len(system_addresses) > 1:
            print("OMV web addresses found: ")
            for system_address in system_addresses:
                print("    * " + system_address[0] + ": " + system_address[1])
        print("")

        if args.debug:
            print("NOTE: Messages won't be sent, they will be printed in the following format:\n")
            print("    Title")
            print("    Message body line 1")
            print("             " + u'\u22ee')
            print("    Message body line n\n")
            print("    Message footer")
            print("\n=========================================================\n")

    debug_collector = args.debug or args.emulate
    message_handler = MessagesHandler(simplepush_devices, system_addresses, args.debug)
    generate_data_collectors_registry(message_handler, args)
    message_handler.run()

    print("OMV push notifications done")

if __name__ == "__main__":
    main()
