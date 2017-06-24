console.log('loaded utils');
Vue.component('transition-auto-expand', {
	functional: true,
	render: function(createElement, context) {
		var data = {
			props: {
				name: 'auto-expand',
				mode: 'out-in'
			},
			on: {
				enter: function(el) {
					el.style.height = 'auto'
					var endHeight = getComputedStyle(el).height
					el.style.height = '1px'
					el.offsetHeight // force repaint
					el.style.height = endHeight;
				},
				afterEnter: function(el) {
					el.style.height = 'auto'
				},
				beforeLeave: function(el) {
					el.style.height = getComputedStyle(el).height
					el.offsetHeight // force repaint
					el.style.height = '0px'
				}
			}
		}
		return createElement('transition', data, context.children)
	}
});
console.log('registered utils');
