# avr-remote
A stand-alone AVR remote website, intended to replace the limited and not-user-friendly ones that are running on several AVRs.

This project builds a python web application that provides a user-friendly web interface to remote control your AVR. It therefore remote connects to the AVR.

## Requirements
1. Python 3
2. aiohttp (`pip3 install aiohttp` should do the trick)

## Extra requirements if using for Onkyo AVR
1. onkyo-eiscp (https://github.com/miracle2k/onkyo-eiscp)

## Installation
1. Clone the git repo
2. Create a configuration file, similar to:
```
{
	"avr_module": "avrremote.avr.marantz",
	"avr_class": "Marantz",
	"avr_connection": {
		"ip": "192.168.12.4"
	},
}
```
3. Start the app as follows:
```
AVRREMOTE_SETTINGS=<absolute path to your config file> AIO_APP_PATH=avrremote adev runserver
```

A stand-alone web server will be started, running on port 5000 on 0.0.0.0.
