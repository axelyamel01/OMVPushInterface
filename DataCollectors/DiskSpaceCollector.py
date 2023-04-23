# module for collecting hdd info
import shutil
import os
from datetime import datetime, timedelta

# import utilities
from Utils import Utils

def disk_space_collector(mount_path, disk_name, temp_dir, free_percent, days_interval, debug):
    if not os.path.isdir(mount_path) and not os.path.isfile(mount_path):
        sys.exit("Error: Path provided to the disk space collector doesn't exists")

    result = [False, "", ""]

    disk_info = shutil.disk_usage(mount_path)
    curr_free_percent = (disk_info.free / disk_info.total) * 100.0

    disk_name_fixed = disk_name.replace(" ", "-")
    disk_space_db_file_name = temp_dir + "omv-push-notifications-disk-space-" + str(disk_name_fixed) + ".tmp"
    message_needed = False
    if os.path.isfile(disk_space_db_file_name):
        # If space was freed then delete the old file
        if curr_free_percent > free_percent:
            os.remove(disk_space_db_file_name)
        else:
            num_days_ago = datetime.now() - timedelta(days=days_interval)
            temp_file_time = datetime.fromtimestamp(os.path.getctime(disk_space_db_file_name))
            # Message needed if the temp_file_time is older that the number of days interval
            message_needed = temp_file_time < num_days_ago
    else:
        message_needed = curr_free_percent <= free_percent

    if message_needed or debug:
        total = disk_info.total / float(1<<30)
        total_str = "{:.2f}".format(total)
        if total > 1024:
            total = total / 1024
            total_str = total_str + " TB"
        else:
            total_str = total_str + " GB"

        used = disk_info.used / float(1<<30)
        used_str = "{:.2f}".format(used)
        if used > 1024:
            used = used / 1024
            used_str = used_str + " TB"
        else:
            used_str = used_str + " GB"

        used_str = used_str + " (" + "{:.2f}".format((disk_info.used / disk_info.total) * 100) + "%)"

        free = disk_info.free / float(1<<30)
        free_str = "{:.2f}".format(free)
        if free > 1024:
            free = free / 1024
            free_str = free_str + " TB"
        else:
            free_str = free_str + " GB"

        free_str = free_str + " (" + "{:.2f}".format(curr_free_percent) + "%)"

        title = "OMV system running out of space"
        message = "Mount \'" + mount_path + "\' is running out of space. Current status: \n"
        message = message + "  " + u"\u2022" + " Total: " + total_str + "\n"
        message = message + "  " + u"\u2022" + " Used: " + used_str + "\n"
        message = message + "  " + u"\u2022" + " Free: " + free_str + "\n"

        result = [True, title, message]

        disk_space_db_file = open(disk_space_db_file_name, "w")
        comment_message = Utils().auto_generated_file_comment("disk_space")
        disk_space_db_file.write(comment_message)
        disk_space_db_file.write("Total: " + total_str + "\n")
        disk_space_db_file.write("Used: " + used_str + "\n")
        disk_space_db_file.write("Free: " + free_str + "\n")
        disk_space_db_file.close()

    return result


