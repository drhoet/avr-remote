$.get('templates/power-toggle.html', function( template ) {
	Vue.component('PowerToggle', { 
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
});