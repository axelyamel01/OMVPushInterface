import time

# Class that handles helper functions
class Utils:
    # Gather the current date and time. Returns the following:
    #
    #   ["MM/DD/YYYY", "HH:MM:SS [AM|PM]"]
    def get_current_date_and_time(self):
        curr_time = time.time()
        local_time = time.localtime(curr_time)
        date = str(local_time.tm_mon) + "/" + str(local_time.tm_mday) + \
                "/" + str(local_time.tm_year)
        hour = local_time.tm_hour
        if hour > 12:
            hour = hour - 12
            ampm = "PM"
        elif hour == 12:
            ampm = "PM"
        else:
            ampm = "AM"

        minutes = local_time.tm_min
        seconds = local_time.tm_sec

        actual_time = ""
        if hour < 10:
            actual_time = "0" + str(hour) + ":"
        else:
            actual_time = str(hour) + ":"

        if minutes < 10:
            actual_time = actual_time + "0" + str(minutes) + ":"
        else:
            actual_time = actual_time + str(minutes) + ":"

        if seconds < 10:
            actual_time = actual_time + "0" + str(seconds)
        else:
            actual_time = actual_time + str(seconds)

        actual_time = actual_time + " " + ampm

        final_time_stamp = ["Date: " + date, "Time: " + actual_time]
        return final_time_stamp

    # Generate a comment for auto generated files.
    def auto_generated_file_comment(self, collector_name):
        comment = "# This file was auto-generated by the OMV push notification " + collector_name + " collector.\n"
        comment = comment + "# Do NOT modify it.\n"
        time_info = self.get_current_date_and_time()
        comment = comment + "#   " + time_info[0] + "\n"
        comment = comment + "#   " + time_info[1] + "\n#\n"

        return comment

    # Given an input string, convert it to the expected type
    def convert_str_to_type(self, source_str, dest_type):
        ret_result = None
        correct_conv = False
        if dest_type == bool:
            supported_true_str = ["true", "1", "enable"]
            supporter_false_str = ["false", "1", "disable"]

            check_val = source_str.lower()
            if check_val in supported_true_str:
                ret_result = True
                correct_conv = True
            elif check_val in supporter_false_str:
                ret_result = False
                correct_conv = True

        elif dest_type == int:
            if source_str.isnumeric():
                ret_result = int(source_str)
                correct_conv = True

        elif dest_type == str:
            ret_result = str(source_str)
            correct_conv = True

        elif dest_type == float:
            try:
                ret_result = float(source_str)
                correct_conv = True
            except ValueError:
                ret_result = source_str

        else:
           ret_result = source_str

        return ret_result, correct_conv

    def get_collectors_available(self):
        collectors_available = ["temperature_collector", "updates_available_collector", "disk_space_collector"]
        return collectors_available

