 $.get('templates/volume-dial.html', function( template ) {
	Vue.component('volume-dial', { 
		template: template,
		props: {
			volume: {
				type: Number,
				required: false,
			},
			rotation: {
				type: String,
				default: 'clockwise',
			},
			max: {
				type: Number,
				default: 100,
			},
			step: {
				type: Number,
				default: 1.0,
			}
		},
		mounted: function() {
			var vm = this;
			$(this.$refs.input).knob({
				'min': 0,
				'max': this.max,
				'step': this.step,
				'rotation': this.rotation,
				'displayPrevious': true,
				'angleOffset': -125,
				'angleArc': 250,
				'width': 220, //fixme
				'height': 175, //fixme
				'format': function( value ) {
					if( this.step < 1) {
						return sprintf('%04.1f', value);
					} else {
						return value;
					}
				},
				'release': function( value ) {
					vm.$emit('update:volume', value)
				}
			});
		},
		computed: {
			displayVolume: function() {
				if( this.step < 1) {
					return sprintf('%04.1f', this.volume);
				} else {
					return this.volume;
				}
			},
		},
		watch: {
			volume: function(value) {
				this.$nextTick(function() {
					$(this.$el).find('input').trigger('change');
				});
			},
		},
	});
});