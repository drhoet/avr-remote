collector.register($.get('templates/modal.html', function(template) {
	console.log('loaded modal');
	Vue.component('modal', {
		template: template,
		props: {
			ok: {
				type: String,
				required: false,
				default: "OK",
			},
			cancel: {
				type: String,
				required: false,
				default: "Cancel",
			},
			showCancel: {
				type: Boolean,
				required: false,
				default: true,
			},
			canOk: {
				type: Boolean,
				required: false,
				default: true,
			},
			canCancel: {
				type: Boolean,
				required: false,
				default: true,
			}
		},
		data: function() {
			return {
				show: false,
			}
		},
	});
	console.log('registered modal');
}));
