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

Pylirc
*See file setup_ir_receiver.txt*

## How to run
To start the script use:
`sudo python lightinator.py`

One important thing to note is that this software is still not designed to be used in a general environment. It currently
uses a hack that involves altering the /etc/network/interfaces file on the device to a preset version. This means that
any custom configurations might be overwritten!

## Contributions
Matz "Nano" Larsson - Code base