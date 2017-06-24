"use strict";

class Endpoint {
	constructor(avr) {
		this.avr = avr;
		this.properties = {}; // these hold the last known value of the property. Used to avoid sending to the AVR when a value has not changed.
	}

	registerProperty(name) {
		this.properties[name] = null;
		Object.defineProperty(this, name, {
			get: function() {
				return this.properties[name];
			},
			set: function(newValue) {
				let oldValue = this.properties[name];
				if (newValue !== oldValue) {
					console.log('sending ' + name + ': ' + newValue);
					this.properties[name] = newValue;
					this.send(name, newValue);
				}
			}
		});
	}

	send(propertyName, propertyValue) {
		console.warn('No send function implemented for ', this, '. Skipping sending of property ' +
			propertyName + '=', propertyValue);
	}

	onStateUpdate(state) {
		for (let property in state) {
			if (state.hasOwnProperty(property)) {
				if (this.properties.hasOwnProperty(property)) {
					let newValue = state[property];
					if (newValue !== this.properties[property]) {
						this.properties[property] = newValue;
						this[property] = newValue; // trigger the update of the property, so vue.js also knows it updated
					}
				} else {
					console.warn('Received update for unregistered property: ' + property);
				}
			}
		}
	}
}

class Zone extends Endpoint {
	constructor(avr, zoneId, static_state) {
		super(avr);
		this.zoneId = zoneId;
		this.name = static_state.name;
		this.inputs = static_state.inputs;
		this.registerProperty('input');
		this.registerProperty('power');
		this.registerProperty('volume');
		this.registerProperty('mute');
	}

	send(propertyName, propertyValue) {
		let state = {};
		state[propertyName] = propertyValue;
		avr.send({
			type: 'zone',
			zoneId: this.zoneId,
			state: state
		})
	}
}

class Tuner extends Endpoint {
	constructor(avr, internalId) {
		super(avr);
		this.internalId = internalId;
		this.registerProperty('band');
		this.registerProperty('freq');
	}

	send(propertyName, propertyValue) {
		let state = {};
		state[propertyName] = propertyValue;
		avr.send({
			type: 'tuner',
			internalId: this.internalId,
			state: state
		})
	}
}

function Avr() {
	var _socket = null;
	var _self = this;

	this.name = '';
	this.ip = '';
	this.zones = [];
	this.internals = [];
	this.connected = false;

	this.connect = function(url) {
		_socket = new WebSocket(url);
		_socket.onmessage = onMessage;
		_socket.onerror = onError;
		_socket.onclose = onClose;
	};

	this.disconnect = function() {
		if (_socket) {
			_socket.close();
		}
	};

	this.send = function(msg) {
		if (_socket && _self.connected) {
			console.log('>> [' + msg.type + '] ', msg, msg.state)
			_socket.send(JSON.stringify(msg));
		}
	};

	function onStaticInfoUpdate(state) {
		_self.name = state.name;
		_self.ip = state.ip;
		_self.volume_step = state.volume_step;
		for (let z = 0; z < state.zones.length; ++z) {
			_self.zones.push(new Zone(_self, z, state.zones[z]));
		}
		for (let i = 0; i < state.internals.length; ++i) {
			if (state.internals[i] == 'tuner') {
				_self.internals.push(new Tuner(_self, i));
			} else {
				_self.internals.push(null);
			}
		}
		_self.connected = true;
	}

	function onMessage(event) {
		let msg = JSON.parse(event.data);
		console.log('<< [' + msg.type + '] ', msg.state, msg)
		switch (msg.type) {
			case 'static_info':
				onStaticInfoUpdate(msg.state);
				break;
			case 'zone':
				if (_self.zones[msg.zoneId]) {
					_self.zones[msg.zoneId].onStateUpdate(msg.state);
				} else {
					console.warn('Received a zone update for non-existing zone: ' + msg.zoneId, event);
				}
				break;
			case 'tuner':
				if (_self.internals[msg.internalId]) {
					_self.internals[msg.internalId].onStateUpdate(msg.state);
				} else {
					console.warn('Received an update for a non-existing internal: ' + msg.internalId, event);
				}
				break;
			case 'error':
				alert(msg.state.message);
				break;
			default:
				console.warn('Invalid message type: ' + msg.type, event);
		}
	}

	function onError(event) {
		console.log(event);
	}

	function onClose(event) {
		console.log(event);
	}

}
