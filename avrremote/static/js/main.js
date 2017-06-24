"use strict";
// << Storage
function AppConfig(avr) {
	let _self = this;
	let _avr = avr;

	this.rotation = 'clockwise';
	this.volume_max = 60.0;
	this.ip = window.location.host;
	Object.defineProperties(this, {
		'volume_step': {
			'get': function() {
				return _avr.volume_step;
			},
			'set': function(value) {
				_avr.volume_step = value;
			},
		},
	});

	this.load = function() {
		let stored_config = localStorage.getItem('avr_remote_app_settings');
		if (stored_config) {
			stored_config = JSON.parse(stored_config);
			_self.rotation = stored_config.rotation;
			_self.volume_max = stored_config.volume_max;
			_self.ip = stored_config.ip;
		} else {
			_self.save();
		};
	};
	this.save = function() {
		window.localStorage.setItem('avr_remote_app_settings', JSON.stringify({
			'rotation': _self.rotation,
			'volume_max': _self.volume_max,
			'ip': _self.ip,
		}));
	};

	try {
		_self.load();
	} catch (e) {
		console.warn(
			'Exception raised while loading config from storage. Does you browser support local storage?',
			e);
	}
}
// >> Storage

// << Avr logic
var avr = new Avr();
var config = new AppConfig(avr);

$.when.apply($, collector.promises).then(function() {
	console.log('All is loaded. Going to start the app!');
	window.vm = new Vue({
		el: '#app-container',
		data: {
			avr: avr,
			config: config,
			showSettings: false,
		},
		methods: {
			mapType: function(internal) {
				if (internal instanceof Tuner) {
					return 'tuner-panel';
				}
			}
		}
	});

	avr.connect('ws://' + config.ip + '/ws');
});

window.onbeforeunload = function() {
	avr.disconnect();
}
// >> Avr logic
