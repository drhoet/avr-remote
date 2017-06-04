function Zone(zoneId, data) {
	this.id = zoneId;
	this.name = data.zones[zoneId];
	this.inputs = data.inputs;
	this._selected_input = null;
	this._power = null;
	this._volume = null;
}

Zone.prototype = {
	get selected_input() {
		return this._selected_input;
	},
	set selected_input(value) {
		this._selected_input = value;
	},
	get power() {
		return this._power;
	},
	set power(value) {
		this._power = value;
	},
	get volume() {
		return this._volume;
	},
	set volume(value) {
		this._volume = value;
	},
};

window.avr = {
	name: '',
	ip: '',
	volume_step: 0.5,
	zones: [],
	
	set_static_info: function( data ) {
		this.name = data.name;
		this.ip = data.ip;
		this.volume_step = data.volume_step;
		this.zones = [];
		for(var z = 0; z < data.zones.length; ++z) {
			this.zones.push( new Zone(z, data) );
		};
	},
	set_config: function( data ) {
		this.config = data;
	},
	set_status: function( data ) {
		for(var z = 0; z < data.zones.length; ++z) {
			let zone = data.zones[z];
			this.zones[z].volume = zone.volume;
			this.zones[z].power = zone.power;
			this.zones[z].selected_input = zone.input;
		};
	},
};

window.vm = new Vue({
	el: '#app-container',
	data: {
		avr: avr,
		config: {
			rotation: 'clockwise',
			volume_step: avr.volume_step,
			volume_max: 60.0,
		},
	},
})

$.get( '/api/v1.0/static_info', function( data ) {
	avr.set_static_info(data);
});

function pollStatus() {
	$.get( '/api/v1.0/status', function( data ) {
		avr.set_status(data);
	});
}

pollStatus();
setInterval( pollStatus, 5000 );


