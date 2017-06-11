"use strict";

function Zone(avr, zoneId, state) {
	this.avr = avr;
	this.zoneId = zoneId;
	this.name = state.name;
	this.inputs = state.inputs;
	this._selected_input = null;
	this._power = null;
	this._volume = null;

	this.updateZone = function(zoneId, state) {
		avr.send({
			type: 'zone',
			zoneId: zoneId,
			state: state,
		});
	}
}

Zone.prototype = {
	get selected_input() {
		return this._selected_input;
	},
	set selected_input(value) {
		if (value !== this._selected_input) {
			console.log('sending selected input: ' + value);
			this._selected_input = value;
			this.updateZone(this.zoneId, {
				'input': this._selected_input
			});
		}
	},
	get power() {
		return this._power;
	},
	set power(value) {
		if (value !== this._power) {
			console.log('sending power: ' + value);
			this._power = value;
			this.updateZone(this.zoneId, {
				'power': this._power
			});
		}
	},
	get volume() {
		return this._volume;
	},
	set volume(value) {
		if (value !== this._volume) {
			console.log('sending volume: ' + value);
			this._volume = value;
			this.updateZone(this.zoneId, {
				'volume': this._volume
			});
		}
	},
	onZoneUpdate(state) {
		if ('input' in state) {
			this.onSelectedInputUpdated(state.input);
		}
		if ('power' in state) {
			this.onPowerUpdated(state.power);
		}
		if ('volume' in state) {
			this.onVolumeUpdated(state.volume);
		}
	},
	onSelectedInputUpdated(value) {
		if (value !== this._selected_input) {
			this._selected_input = value;
			this.selected_input = value; // trigger the update of the property, so vue.js also knows it updated
		}
	},
	onPowerUpdated(value) {
		if (value !== this._power) {
			this._power = value;
			this.power = value; // trigger the update of the property, so vue.js also knows it updated
		}
	},
	onVolumeUpdated(value) {
		if (value !== this._volume) {
			this._volume = value;
			this.volume = value; // trigger the update of the property, so vue.js also knows it updated
		}
	},
};

function Avr() {
	var _socket = null;
	var _self = this;

	this.name = '';
	this.ip = '';
	this.zones = [];
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
		_self.zones = [];
		for (var z = 0; z < state.zones.length; ++z) {
			_self.zones.push(new Zone(_self, z, state.zones[z]));
		};
		_self.connected = true;
	}

	function onMessage(event) {
		let msg = JSON.parse(event.data);
		console.log('<< [' + msg.type + '] ', msg.state)
		switch (msg.type) {
			case 'static_info':
				onStaticInfoUpdate(msg.state);
				break;
			case 'zone':
				if (_self.zones[msg.zoneId]) {
					_self.zones[msg.zoneId].onZoneUpdate(msg.state);
				} else {
					console.warn('Received a zone update for non-existing zone: ' + msg.zoneId, event);
				}
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
