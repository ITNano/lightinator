# Lightinator
## General
This is a project in order to build a hardware controller for my RGB lights at home. It started as a software
subproject to TechHome (which also includes voice control to start movies etc.), but I decided to make it
external when it grew big. Nowadays it consists of various sensors, buttons and LEDs all built into a wooden
box. The perfect decoration of a living room!

Due to the hardware nature of the project I have also tried to modularize the code more and more, in order to 
make it available for other people with other available hardware. A recent added feature was the configuration
file of all inputs, devices and actions on events. Due to this big changes, no good documentation exists. I plan
on doing that later in the project.

## Requirements
The project is run as a Python 2.7 script. If you ignore the IR controller it might be able to run Python3 (not yet
tested). This might mean that you will have to do alterations in the lib to not load the pylirc lib, will be more
clear in later commits.

RPi.GPIO:
`pip install RPi.GPIO`

Netifaces
`pip install netifaces`

PsUtil
`sudo pip install psutil`

avplay or ffplay (audio)
`sudo apt-get install ffmpeg libavcodec-extra-53`

Pydub (audio)
`sudo pip install pydub`

Pylirc
*See file setup_ir_receiver.txt*

## Configuration
The configuration of hardware, events on sensor usage and similar are all defined in the `lightinator.conf` file with
json markup. The exising configuration file contains a lot of examples on how to do most possible things and is a good
learning example but maybe not a reasonable running setup (though it is a valid setup!). All possible commands is
specified in the `configuration_manual.txt` file. The documentation for LIRC is located in `lirc_conf`.

Note that the documentation for this project still isn't so good, since I doubt it will be used in any large scale
(by many users). If you plan on using this on your system and have any questions, don't hesitate to mail me at
lightinator@matzlarsson.se.

## How to run
### Version 1
To start the script use:
`sudo python v1/lightinator.py`

NOTE: 
One important thing to note is that this version is still not designed to be used in a general environment. It currently
uses a hack that involves altering the /etc/network/interfaces file on the device to a preset version. This means that
any custom configurations might be overwritten!

### Version 2
To start the script use:
`sudo python v2/main.py`


## Contributions
Matz "Nano" Larsson - Code base