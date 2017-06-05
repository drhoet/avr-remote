$.get('templates/accordion-panel.html', function( template ) {
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
});