$.get('templates/zone.html', function( template ) {
	Vue.component('Zone', {
		template: template,
		props: {
			zone: {
				type: Object,
				required: true,
			},
			config: {
				type: Object,
				required: true,
			},
		},
		computed: {
			panelId: function() {
				return '#zone' + this.zone.id + '-body';
			},
			mappedInputs: function() {
				return this.zone.inputs.map( function(v, index) {
					return {
						id: index,
						name: v[0],
						icon: v[1],
					};
				});
			},
			inputs1: function() {
				return this.mappedInputs.slice(0, this.mappedInputs.length / 2);
			},
			inputs2: function() {
				return this.mappedInputs.slice(this.mappedInputs.length / 2);
			},
		},
		methods: {
			inputIcon: function( id ) {
				return 'svg/sprite/input_sources_24px.svg#' + id;
			},
		},
	});
});