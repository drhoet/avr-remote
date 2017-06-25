collector.register($.get('templates/tuner-panel.html', function(template) {
	console.log('loaded tuner-panel');
	let FrequencyBand = {
		template: '<canvas ref="canvas"></canvas>',
		props: {
			band: {
				type: String,
				required: true,
			},
			freq: {
				type: Number,
				requred: true,
			},
		},
		mounted: function() {
			this.drawCanvas();
			window.addEventListener('resize', this.drawCanvas);
		},
		beforeDestroy: function() {
			window.removeEventListener('resize', this.drawCanvas);
		},
		computed: {
			freqMin: function() {
				switch (this.band) {
					case "AM":
						return 522;
					case "FM":
						return 87.50;
					default:
						return 0;
				}
			},
			freqMax: function() {
				switch (this.band) {
					case "AM":
						return 1611;
					case "FM":
						return 108;
					default:
						return 0;
				}
			},
			freqStep: function() {
				switch (this.band) {
					case "AM":
						return 9;
					case "FM":
						return 0.05;
					default:
						return 0;
				}
			},
		},
		methods: {
			findClosestValidNbTicksPerFreq(value) {
				let allowed = [10, 5, 2, 1, 0.5, 0.2, 0.1, 0.05, 0.02, 0.01];
				for (let i = 0; i < allowed.length; ++i) {
					if (value >= allowed[i]) {
						return allowed[i];
					}
				}
				return 0.1;
			},
			drawCanvas: function() {
				let canvas = this.$refs.canvas;
				canvas.width = canvas.parentElement.clientWidth;
				canvas.height = canvas.parentElement.clientHeight;
				let ctx = canvas.getContext('2d');

				// background
				ctx.fillStyle = '#999999';
				ctx.fillRect(0, 0, canvas.width, canvas.height);

				// calculations
				ctx.font = '1.5rem roboto';
				let minPadding = Math.ceil(ctx.measureText(this.freqMax + 'MM').width); // padding needed to print labels completely
				let maxBandWidth = canvas.width - minPadding;
				let minTickWidth = Math.ceil(ctx.measureText(this.freqMax).width / 10); // 10 ticks MUST be wider than the width of one label, otherwise the labels overlap
				// first we want to estimate how many ticks we want to draw.
				let maxNbTicks = maxBandWidth / minTickWidth;
				let maxNbTicksPerFreq = maxNbTicks / (this.freqMax - this.freqMin);
				// now set this at max 10, and must be a divisor of 10, otherwise we get weird frequence labels
				let nbTicksPerFreq = this.findClosestValidNbTicksPerFreq(maxNbTicksPerFreq);
				// to be able to calculate in whole numbers, move the frequency scale to the 't' scale:
				// this scale is constructed, so that we want to draw a guide line for every whole t
				let firstTick = Math.floor(nbTicksPerFreq * this.freqMin); // freqMin could be fractional!
				let lastTick = Math.ceil(nbTicksPerFreq * this.freqMax); // freqMax could be fractional!
				// we got a minimum tick width, but maybe it can be wider and still fit in the window
				let tickWidth = Math.max(minTickWidth, Math.floor(maxBandWidth / (lastTick - firstTick)));
				let bandWidth = tickWidth * (lastTick - firstTick);
				let padding = Math.floor((canvas.width - bandWidth) / 2); // max half pixel wrong...

				// actual frequency
				let position = Math.floor(nbTicksPerFreq * this.freq) - firstTick;
				ctx.strokeStyle = '#f00';
				ctx.lineWidth = 4;
				ctx.beginPath();
				ctx.moveTo((position * tickWidth) + padding, 0);
				ctx.lineTo((position * tickWidth) + padding, canvas.height);
				ctx.stroke();
				ctx.closePath();

				// frequency band
				ctx.strokeStyle = '#fff';
				ctx.fillStyle = '#fff';
				ctx.lineWidth = 1;
				for (let tick = firstTick; tick <= lastTick; tick += 1) {
					let x = (tick - firstTick) * tickWidth + padding;
					ctx.beginPath();
					ctx.moveTo(x, 0);
					ctx.lineTo(x, tick % 10 == 0 ? 30 : tick % 5 == 0 ? 25 : 20);
					ctx.stroke();
					ctx.closePath();
					if (tick % 10 == 0) {
						let freq = tick / nbTicksPerFreq;
						let textWidth = ctx.measureText(freq).width;
						ctx.fillText(freq, x - textWidth / 2, 50);
					}
				}
			}
		},
		watch: {
			freq: function() {
				this.drawCanvas();
			},
			band: function() {
				this.drawCanvas();
			}
		}
	};

	Vue.component('tuner-panel', {
		template: template,
		props: {
			item: {
				type: Object,
				required: true,
			},
		},
		components: {
			'frequency-band': FrequencyBand,
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
			freqUnit: function() {
				switch (this.item.band) {
					case "AM":
						return 'KHz';
					case "FM":
						return 'MHz';
					default:
						return '';
				}
			}
		},
		methods: {
			inputIcon: function(id) {
				return 'svg/sprite/input_sources_24px.svg#' + id;
			},
		},
	});
	console.log('registered tuner-panel');
}));
