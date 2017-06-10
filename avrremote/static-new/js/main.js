"use strict";

window.config = {
	rotation: 'clockwise',
	volume_max: 60.0,
	get volume_step() {
		return avr.volume_step;
	},
	set volume_step(value) {
		avr.volume_step = value;
	}
};

var avr = new Avr();

$.when.apply($, collector.promises).then(function() {
	console.log('All is loaded. Going to start the app!');
	window.vm = new Vue({
		el: '#app-container',
		data: {
			avr: avr,
			config: config,
		},
	});

	avr.connect('ws://' + window.location.host + '/ws');
});

window.onbeforeunload = function() {
	avr.disconnect();
}
