collector.register($.get('templates/settings.html', function(template) {
	console.log('loaded settings');
	Vue.component('settings', {
		template: template,
		props: {
			appConfig: {
				type: Object,
				required: true,
			},
			show: {
				type: Boolean,
				required: true,
			}
		},
		data: function() {
			return {
				errorMessage: null,
				url: this.appConfig.ip,
				volumeMax: this.appConfig.volume_max,
				rotation: this.appConfig.rotation,
			};
		},
		methods: {
			save: function() {
				try {
					this.appConfig.ip = this.url;
					this.appConfig.volume_max = parseFloat(this.volumeMax);
					this.appConfig.rotation = this.rotation;
					this.appConfig.save();
					this.errorMessage = null;
					this.close();
				} catch (e) {
					this.errorMessage = e.message;
				}
			},
			close: function() {
				this.$emit('close')
			}
		},
	});
	console.log('registered settings');
}));
