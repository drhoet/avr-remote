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
			mappedSources: function() {
				return this.zone.sources.map( function(v, index) {
					return {
						id: index,
						name: v[0],
						icon: v[1],
					};
				});
			},
			sources1: function() {
				return this.mappedSources.slice(0, this.mappedSources.length / 2);
			},
			sources2: function() {
				return this.mappedSources.slice(this.mappedSources.length / 2);
			},
		},
		methods: {
			sourceIcon: function( id ) {
				return 'svg/sprite/input_sources_24px.svg#' + id;
			},
		},
	});
});