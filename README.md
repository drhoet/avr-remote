# avr-remote
A stand-alone AVR remote website, intended to replace the limited and not-user-friendly ones that are running on several AVRs.

This project builds a python web application that provides a user-friendly web interface to remote control your AVR. It therefore remote connects to the AVR.

## Requirements
1. Python 3
2. Flask (`pip3 install flask` should do the trick)
3. requests (`pip3 install requests` should do the trick)

## Installation
1. Clone the git repo
2. Create a configuration file, similar to:
```
AVR_MODULE = 'avrremote.avr.marantz'
AVR_CLASS = 'Marantz'
```
3. Start the app as follows:
```
AVRREMOTE_SETTINGS=<absolute path to your config file> FLASK_APP=avrremote python3 -m flask run
```

A stand-alone web server will be started, running on port 5000 on localhost. If you want it to be visible to the outside world, add a parameter `-h 0.0.0.0` to the command line above.