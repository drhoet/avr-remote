collector.register( $.get('templates/accordion-panel.html', function( template ) {
	console.log('loaded accordion-panel');
	Vue.component('accordion-panel', { 
		template: template,
		props: {
			initialActive: {
				type: Boolean,
				required: false,
				default: false,
			}
		},
		data: function() {
			return {
				active: this.initialActive,
			}
		},
		methods: {
			toggle: function() {
				this.active = !this.active;
			},
		},
	});
	console.log('registered accordion-panel');
}) );