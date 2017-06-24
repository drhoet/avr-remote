collector.register($.get('templates/power-toggle.html', function(template) {
	console.log('loaded power-toggle');
	Vue.component('power-toggle', {
		template: template,
		props: {
			zoneId: {
				type: Number,
				required: true,
			},
			value: {
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
			updateValue: function(value) {
				this.$emit('input', value);
			},
		},
	});
	console.log('registered power-toggle');
}));
