# OMV push notifications interface

Author: Axel Y. Rivera <br />
Email: axelrivera1986@gmail.com <br />
Version: 2023.05.06

## Summary

OMV push notifications is a tool for collecting data from the OS, parse and sending it to a device through push notifications It uses the [Simplepush](https://simplepush.io/) app to communicate with the device. The basic idea is that the user downloads the Simplepush from the app store, the configure the OMV push notifications interface and then get the notifications needed in the device. The app is available for [Android](https://play.google.com/store/apps/details?id=io.simplepush) and [iOS](https://apps.apple.com/us/app/simplepush-notifications/id1569978086).

## Release notes:

- 2023.05.06:
    * Changed the config section `omv-system-info` to `omv-system-address`
    * Allowed to configure multiple `omv-system-address` sections
    * Added field `name` for `omv-system-address`
    * Added field `ip` for `omv-system-address`
    * If `ip` is provided, then `hostname` and `domain-name` not needed in `omv-system-address`
    * Removed `omv-` from the fields of `omv-system-address`
- 2023.04.23:
    * Fixed bug when there is no `simplepush-device` registered in config file
    * Added disk space collector
    * Added description for each collector in the collectors' [README](/DataCollectors/README.md) file.
- 2023.04.22:
    * Fixed a bug in the updates available collector where the number of updates available mismatched between debug and non-debug modes
    * Added extra comments in the updates available and temperature collectors
    * Added extra comments in the Utils module
- 2023.04.18:
    * Moved all data collectors into one directory to keep it organized
    * Added README for data collectors
- 2023.04.16:
    * Added README
    * Added data collectors registry
    * Added support for multiple devices
    * Updated config file parsing
    * Updated the `updates_available_collector` to use `/var/temp` rather than a local temp
- 2023.04.08
    * Intial version

## Command-line arguments available:
- `-h, --help` : show this help message and exit
- `-c CONFIG, --config CONFIG` : Config file that contains the credentials for SimplePush
- `-d, --debug` : Enable debug mode, messages will be printed and not sent
- `-e, --emulate` : Enable emulation mode, message generated by debug mode will be sent rather than print

## Pre-requirements:

The current implementation requires some basic coding knowledge. You don't need to know Python then Google will help you, but you need to understand basic concepts like functions, classes, parameters, lists, etc. Part of the [TODO](#todo) work is to simplify the interaction and remove this pre-requirement.

## Pre-configuration:

This step will guide you to configure your Simplepush app. Do this first before start using the OMV push notifications interface. It is important that you can send a message from your system to your device with a simple example.

1. Install the Simplepush app in your device. Then go to the settings and set a password (`Settings -> Encryption -> Password`). Also, write down your `key` and `salt`. The `key` is provided to you during the first login, or you can collect it in `Settings -> Your key`. The `salt` is also in the same encryption tab where you set your password.

2. Install the Simplepush dependency package
    - [Simplepush API](https://github.com/simplepush/simplepush-python): `pip3 install simplepush`

3. Open a new text file, copy the following python commands, modify the `key`, `password` and `salt` with the settings from step 1, and save it (e.g. `test-simple.py`). You can modify the `title` and `message` if you want to. These commands work in the python console too.

   ```
   import simplepush
   simplepush.send(key='YourKey', password='YourPassword', salt='YourSalt', title='Simple title', message='Simple message body')
   ```

4. Run the test with the following command:

   ```
   python3 test-simple.py
   ```

   There is a chance that the python missing packages message will pop-up when trying to run the simple test case. Install the packages needed using `pip3` and run the test command again. I apologies for not listing the extra dependencies I needed to install, I forgot which one I installed. Do **NOT** keep going further until you can send a simple message and get it in your device using the example. This is the core of the tool.

## How to use OMV push notifications interface?

The basic idea is to keep things as simple as possible (I hope it is simple for you `:)`). This interface was created with the idea that the OS is [OpenMediaVault](https://www.openmediavault.org/), which is based on Debian Linux. I'm pretty sure with some small tweeks you can use it with other Linux distros.

1. Make sure you did the steps mentioned in the [Pre-configuration](#pre-configuration) section. If not, go back and try to run the simple test. If the simple test doesn't run, the rest won't work.

2. Download or copy the repo

3. Create a config file, or use the template in [config/push-notifications-system.cfg](/config/push-notifications-system.cfg). If you are using the template, make sure to update it. The config file is split in sections and key-words. It must have at least one `simplepush-device` section and one `omv-system-address` section.

    - `simplepush-device` : Section for the information related to the device that will receive the message
        - `key` : Simplepush key located in your app (**required**)
        - `password` : Simplepush password set by you in the app (**required**)
        - `salt` : Simplepush salt from the app (**required**)

    - `omv-system-address` : Section for the information related to the OMV system network
        - `name` : Preferred name for the current network configuration (**default value is `OMV-#`**)
        - `hostname` : Host name of your OMV system (**required if `ip` is not provided**)
        - `domain` : Domain of your OMV system (**required if `ip` is not provided**)
        - `web-protocol` : Web protocol used to access the web interface (**default value is `http`**)
        - `port` : Port used to access OMV web interface (**default value is `80`**)
        - `ip` : IP address of your OMV system (**required if `hostname` and `domain` are not provided**)


    The **required** fields need to be set before creating another section. The fields with **default value** will set a default value if the field is not added to the section. I strongly suggest to check the [template file](/config/push-notifications-system.cfg) to have an idea how the config file works.

4. Take a look at the registered collectors in [DataCollectorsRegistry.py](/DataCollectorsRegistry.py) and update any parameter you need. For example, the disk space collector is registered as follows:

    ```
    message_handler.add_collector(DataCollectors.disk_space_collector, "/", "root-drive", "/var/tmp/", 20.0, 7,    debug_collector)
    ```

    This means that the disk space collector will compute the information using the following parameters:
    - `"/"` (root): mount path
    - `"root-drive"` : name used to identify drive
    - `"/var/tmp/"`: path for storing temporary data
    - `"20.0"` : message will be sent if there is 20% or less of space free
    - `"7"` : number of days to resend the message if needed

    Try changing these paramaters to your preferred setup. For more details on the registered collectors and the paramaters, refer to the [README](/DataCollectors/README.md) in the data collectors directory.

5. Run it through the terminal with the following command: `python3 /PATH/TO/OMVPushNotifications.py -c /PATH/TO/CONFIG/FILE`. If `-c` is not added then the [template file](/config/push-notifications-system.cfg) will be used as config file, therefore make sure it is configured properly. You can use `-d` to print in the messages in the command line rather than send them. Also, you can use `-e` to force the debug message to be sent (for example, if the CPU didn't reached the critical temperature but you want to print the current one). This is helpful to make sure that data is being collected properly and the information is sent.

6. Once you tested the interface in the terminal, go to the OMV web interface and schedule a new task (`System -> Scheduled Tasks`) with the command `python3 /PATH/TO/OMVPushNotifications.py -c /PATH/TO/CONFIG/FILE` and the time interval you would like (e.g. every 5 minutes).

7. Save the task and apply it.

8. Done! (I hope this is simple `:)`)

## How it works?

The implementation of OMV push notifications interface is pretty simple. The basic idea is that a function collector will collect the data, parse it, and create the title and message. The message generator will take the information and send it to the devices that were configured through the config file, or print it in the screen if debug mode is enabled. The message handler is used to register and run the data collectors. For more details about how the data collectors work and how to implement a new one, take a look at the [README.md](/DataCollectors/README.md) file in the DataCollectors directory.

## Notes:

There is no warranties using this tool. Also, this is **NOT** an official tool, plugin, package, or application from OpenMediaVault, Simplepush or its communities. This interface is a simple tool I developed as a side project. Feel free to contact me if you need help with it.

## TODO:
1. Add an extra parameter to the temperature collector for collecting other temperatures like HDD.
2. A simpler way to register a collector that won't depend on modifying source code.
3. Simplify the installation and configuration.
4. Add verbose mode (debug + emulation)