window.avr = {
	name: '',
	ip: '',
	volume_step: 0.5,
	zones: [],
	
	set_static_info: function( data ) {
		this.name = data.name;
		this.ip = data.ip;
		this.volume_step = parseFloat(data.volume_step);
		this.zones = [];
		for(var z = 0; z < data.zones.length; ++z) {
			this.zones.push({
				id: z,
				name: data.zones[z],
				inputs: data.inputs,
				selected_input: data.input,
				power: null,
				volume: 0.0,
			});
		};
	},
	set_config: function( data ) {
		this.config = data;
	}
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