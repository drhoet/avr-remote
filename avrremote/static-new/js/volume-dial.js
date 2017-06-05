 $.get('templates/volume-dial.html', function( template ) {
	Vue.component('volume-dial', { 
		template: template,
		props: {
			value: {
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
				'format': this.formatVolume,
				'release': function( value ) {
					vm.$emit('input', value)
				}
			});
		},
		computed: {
			displayVolume: function() {
				return this.formatVolume( this.value );
			},
		},
		methods: {
			formatVolume: function( value ) {
				if( this.step < 1) {
					return sprintf('%04.1f', value);
				} else {
					return value;
				}
			}
		},
		watch: {
			value: function(value) {
				this.$nextTick(function() {
					$(this.$el).find('input').trigger('change');
				});
			},
		},
	});
});