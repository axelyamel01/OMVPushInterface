# module for handling apt
import apt_pkg

# module for handling OS relating stuffs
import os
import sys

# import utilities
from Utils import Utils

# Collect the packages that needs update.
# Input:
#
#   temp_directory => directory used to store temporary data
#   debug => display the message even if there is no new package to update,
#            useful for debug
def updates_available_collector(temp_directory: str, debug: bool):
    result = [False, '', '']
    packages_to_update = []

    #collect the packages that need update
    apt_pkg.init()
    cache = apt_pkg.Cache(None)
    dep_cache = apt_pkg.DepCache(cache)
    for pkg in cache.packages:
        current_version = pkg.current_ver
        if current_version == None:
            continue

        # There is an update if the candidate version in apt is different than
        # the current installed version
        candidate_version = dep_cache.get_candidate_ver(pkg)
        if current_version == candidate_version:
            continue

        # Build a small list of the packages needed
        package_name = "Package name: " + pkg.name + "\n"
        package_curr_ver = "  Current installed version: " + current_version.ver_str + "\n"
        package_update_ver = "  Newer version available: " + candidate_version.ver_str + "\n"

        packages_to_update.append([package_name, package_curr_ver, package_update_ver])

        if not "Depends" in candidate_version.depends_list:
            continue

        # Identify any dependency that will be installed due to this package
        for dep_list in candidate_version.depends_list["Depends"]:
            for dep in dep_list:
                target_pkg = dep.target_pkg

                # If the dependency has a target package, and the package is
                # currently installed, then skip it. The main loop that checks for
                # updates will update it.
                if target_pkg.current_ver != None:
                    continue

                # Traverse through the list of target versions and check if there
                # is at least one variation of the dependency installed
                dep_ver_installed = False
                for target_ver in dep.all_targets():
                    target_ver_pkg = target_ver.parent_pkg
                    if target_ver_pkg.current_ver != None:
                        dep_ver_installed = True
                        break

                if dep_ver_installed:
                    continue

                # Add the dependency as part of the updates list
                ver_str = dep_cache.get_candidate_ver(target_pkg).ver_str
                package_name = "Package name: " + target_pkg.name + "\n"
                package_curr_ver = "  Current installed version: " + ver_str + "\n"
                package_update_ver = "  Newer version available: " + ver_str + "\n"

                packages_to_update.append([package_name, package_curr_ver, package_update_ver])

    # Check if there was packages collected before
    update_needed_db_file_name = temp_directory + "omv-push-notifications-update-pkgs.tmp"

    prev_data_collected = []
    if os.path.isfile(update_needed_db_file_name):
        # If any package was collected before but we don't have new packages
        # now, then it means that an update was done. Delete the temp file
        # and exit.
        if len(packages_to_update) == 0:
            os.remove(update_needed_db_file_name)
            if debug:
                title = "Update available for OMV system"
                message = "There is no new package available for update.\n"
                result = [True, title, message]
            return result

        ## Parse the old data base
        read_file = open(update_needed_db_file_name, 'r')
        entry_in_file = []
        lines = read_file.readlines()
        counter = 0
        correct_tags = ["Package name", "Current installed version", "Newer version available"]
        for line in lines:
            strip_line = line.strip()
            if len(strip_line) == 0:
                prev_data_collected.append(entry_in_file[:])
                entry_in_file.clear()
                continue

            if strip_line[0] == '#':
                continue

            split_line = strip_line.split(':')
            if not split_line[0] in correct_tags:
                print(split_line[0])
                read_file.close()
                sys.exit("Error: Incorrect entry in system updates data-base: " + \
                          update_needed_db_file_name)
            entry_in_file.append(strip_line)

        read_file.close()

    # Message is needed if one of the entries in the new data base is not found
    # in the old data base, or debug is enabled
    num_new_pkgs = 0
    if len(prev_data_collected) != 0 and not debug:
        for pkg in packages_to_update:
            package_found = False
            for old_pkg in prev_data_collected:
                if pkg[0].strip() == old_pkg[0] and pkg[1].strip() == old_pkg[1] and pkg[2].strip() == old_pkg[2]:
                    package_found = True
                    break
            if not package_found:
                num_new_pkgs = len(packages_to_update)
                break
    else:
        num_new_pkgs = len(packages_to_update)

    message_needed = num_new_pkgs > 0 or debug
    utils = Utils()

    # Generate the new message
    if message_needed:
        title = "Update available for OMV system"
        message = ""
        if num_new_pkgs == 0:
            message = "There is no new package available for update.\n"
        elif num_new_pkgs == 1:
            message = "There is " + str(num_new_pkgs) + " new package available for update.\n"
        else:
            message = "There are " + str(num_new_pkgs) + " new packages available for update.\n"

        result = [True, title, message]

    # Write a new data base if needed
    if num_new_pkgs > 0:
        update_needed_db_file = open(update_needed_db_file_name, "w")
        comment_message = utils.auto_generated_file_comment("updates_available")
        update_needed_db_file.write(comment_message)
        for pkg in packages_to_update:
            update_needed_db_file.write(pkg[0])
            update_needed_db_file.write(pkg[1])
            update_needed_db_file.write(pkg[2])
            update_needed_db_file.write("\n")
        update_needed_db_file.close()

    return result