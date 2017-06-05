collector.register( $.get('templates/power-toggle.html', function( template ) {
	console.log('loaded power-toggle');
	Vue.component('power-toggle', { 
		template: template,
		model: {
			prop: 'checked',
			event: 'change',
		},
		props: {
			zoneId: {
				type: Number,
				required: true,
			},
			checked: {
				required: true,
			},
		},
		computed: {
			disabled: function() {
				return this.checked === null;
			},
			uid: function() {
				return 'power-toggle-' + this.zoneId;
			}
		},
		methods: {
			updateChecked: function( value ) {
				this.$emit('change', value );
			},
		},
	});
	console.log('registered power-toggle');
}) );