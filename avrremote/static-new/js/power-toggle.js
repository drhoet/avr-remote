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
			btnStyle: function() {
				if( this.power === null ) {
					return 'btn-default off disabled';
				} else {
					return this.power ? 'btn-success on' : 'btn-default off';
				}
			},
			disabled: function() {
				return this.power === null ? 'disabled' : '';
			}
		},
		methods: {
			toggle: function() {
				if( !(this.power === null) ) {
					this.$emit('update:power', !this.power)
				};
			},
		},
	});
});