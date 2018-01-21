# avr-remote
A stand-alone AVR remote website, intended to replace the limited and not-user-friendly ones that are running on several
AVRs.

This project builds a python web application that provides a user-friendly web interface to remote control your AVR. It
therefore remote connects to the AVR.

## Requirements
1. Python 3.6
2. aiohttp (`pip3 install aiohttp` should do the trick)

## Extra requirements if using for Onkyo AVR
1. onkyo-eiscp (https://github.com/miracle2k/onkyo-eiscp). There is currently no version for 3.6 that pip3 can install,
but you can manually install it by downloading the package from PiPy and then running `python3.6 setup.py install`.

## Installation
1. Clone the git repo
2. Create a configuration file, similar to:
```
{
	"avr_module": "avrremote.avr.marantz",
	"avr_class": "Marantz",
	"avr_connection": {
		"ip": "192.168.0.100"
	}
}
```
3. Start the app as follows:
```
AVRREMOTE_SETTINGS=<absolute path to your config file> python3.6 server.py
```

A stand-alone web server will be started, running on port 8080 on 127.0.0.1.

Run with `--help` for more options.
