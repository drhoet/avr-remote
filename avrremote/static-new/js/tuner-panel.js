collector.register($.get('templates/tuner-panel.html', function(template) {
	console.log('loaded tuner-panel');
	Vue.component('tuner-panel', {
		template: template,
		props: {
			item: {
				type: Object,
				required: true,
			},
		},
		computed: {
			freqMin: function() {
				switch (this.item.band) {
					case "AM":
						return 522;
					case "FM":
						return 87.50;
					default:
						return 0;
				}
			},
			freqMax: function() {
				switch (this.item.band) {
					case "AM":
						return 1611;
					case "FM":
						return 108;
					default:
						return 0;
				}
			},
			freqStep: function() {
				switch (this.item.band) {
					case "AM":
						return 9;
					case "FM":
						return 0.05;
					default:
						return 0;
				}
			},
		},
	});
	console.log('registered tuner-panel');
}));
