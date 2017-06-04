$.get('templates/power-toggle.html', function( template ) {
	Vue.component('PowerToggle', { 
		template: template,
		props: {
			zoneId: {
				type: Number,
				required: true,
			},
			power: {
				required: false,
				twoWay: true,
			}
		},
		computed: {
			internalPower: {
				get: function() {
					return this.power;
				},
				set: function(value) {
					this.$emit('update:power', value);
				}
			},
			disabled: function() {
				return this.power === null;
			},
			uid: function() {
				return 'power-toggle-' + this.zoneId;
			}
		},
	});
});