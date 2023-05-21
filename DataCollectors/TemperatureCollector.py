# module for collecting cpu-temps
import psutil

# Function for collecting temperature
# Input:
#   critical_temp => critical temperature to enable the warning
#   debug => generate the message even if the critical temperature
#            wasn't reached, useful for debug
#
# TODO: add as parameter other hardwares like HDD
def temperature_collector(critical_temp: float, debug: bool):
    curr_temperature = psutil.sensors_temperatures()['coretemp'][0][1]

    result = [False, "", ""]

    if curr_temperature >= critical_temp or debug:
        title = "Critical temperature found in OMV system"
        message = "CPU reached " + str(curr_temperature) + " C" + u"\u00b0" + "\n"
        result = [True, title, message]

    return result