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
		if( value !== this._selected_input ) {
			console.log('sending selected input: ' + value);
			this._selected_input = value;
			$.ajax({
				url: '/api/v1.0/zone/' + this.id + '/input',
				type: 'PUT',
				data: JSON.stringify({ value: this._selected_input }),
				contentType: 'application/json; charset=utf-8'					
			});
		}
	},
	get power() {
		return this._power;
	},
	set power(value) {
		if( value !== this._power ) {
			console.log('sending power: ' + value);
			this._power = value;
			$.ajax({
				url: '/api/v1.0/zone/' + this.id + '/power',
				type: 'PUT',
				data: JSON.stringify({ value: this._power }),
				contentType: 'application/json; charset=utf-8'					
			});
		}
	},
	get volume() {
		return this._volume;
	},
	set volume(value) {
		if( value !== this._volume ) {
			console.log('sending volume: ' + value);
			this._volume = value;
			$.ajax({
				url: '/api/v1.0/zone/' + this.id + '/volume',
				type: 'PUT',
				data: JSON.stringify({ value: this._volume }),
				contentType: 'application/json; charset=utf-8'
			});
		}
	},
	onSelectedInputUpdated( value ) {
		if( value !== this._selected_input ) {
			this._selected_input = value;
			this.selected_input = value; // trigger the update of the property, so vue.js also knows it updated
		}
	},
	onPowerUpdated( value ) {
		if( value !== this._power ) {
			this._power = value;
			this.power = value; // trigger the update of the property, so vue.js also knows it updated
		}
	},
	onVolumeUpdated( value ) {
		if( value !== this._volume ) {
			this._volume = value;
			this.volume = value; // trigger the update of the property, so vue.js also knows it updated
		}
	},
};

window.avr = {
	name: '',
	ip: '',
	volume_step: 0.5,
	zones: [],
	connected: false,
	
	set_static_info: function( data ) {
		this.name = data.name;
		this.ip = data.ip;
		this.volume_step = data.volume_step;
		this.zones = [];
		for(var z = 0; z < data.zones.length; ++z) {
			this.zones.push( new Zone(z, data) );
		};
		this.connected = true;
	},
	set_config: function( data ) {
		this.config = data;
	},
	set_status: function( data ) {
		for(var z = 0; z < data.zones.length; ++z) {
			let zone = data.zones[z];
			this.zones[z].onVolumeUpdated( zone.volume );
			this.zones[z].onPowerUpdated( zone.power );
			this.zones[z].onSelectedInputUpdated( zone.input );
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
});

$.get( '/api/v1.0/static_info', function( data ) {
	avr.set_static_info(data);
	pollStatus();
	setInterval( pollStatus, 5000 );
});

function pollStatus() {
	$.get( '/api/v1.0/status', function( data ) {
		avr.set_status(data);
	});
}


