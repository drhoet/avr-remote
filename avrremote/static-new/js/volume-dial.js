collector.register($.get('templates/volume-dial.html', function(template) {
	console.log('loaded volume-dial');
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
			},
			mute: {
				type: Boolean,
				required: false,
				default: false,
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
				'release': function(value) {
					vm.$emit('volumeChanged', value)
				}
			});
		},
		computed: {
			displayVolume: function() {
				return this.formatVolume(this.volume);
			},
		},
		methods: {
			formatVolume: function(value) {
				if (this.step < 1) {
					return sprintf('%04.1f', value);
				} else {
					return value;
				}
			}
		},
		watch: {
			volume: function(value) {
				this.$nextTick(function() {
					$(this.$el).find('input').trigger('change');
				});
			},
			step: function(value) {
				$(this.$refs.input).trigger('configure', {
					'step': value
				});
			},
			rotation: function(value) {
				$(this.$refs.input).trigger('configure', {
					'rotation': value
				});
			},
			max: function(value) {
				$(this.$refs.input).trigger('configure', {
					'max': value
				});
			},
		},
	});
	console.log('registered volume-dial');
}));
