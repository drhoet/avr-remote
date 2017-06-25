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
			findClosestValidNbGuideLinesPerFreq(value) {
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
				let minPadding = ctx.measureText(this.freqMax + 'MM').width; // padding needed to print labels completely
				let maxBandWidth = canvas.width - minPadding;
				// first we want to estimate how many guide lines we want to draw. Every 4-5 pixels looks nice.
				let nbGuideLinesPerFreq = maxBandWidth / (this.freqMax - this.freqMin + 1) / 4; // 10 -- 0.2
				// now set this at max 10, and must be a divisor of 10, otherwise we get weird frequence labels
				nbGuideLinesPerFreq = this.findClosestValidNbGuideLinesPerFreq(nbGuideLinesPerFreq);
				// to be able to calculate in whole numbers, move the frequency scale to the 'f' scale:
				// this scale is constructed, so that we want to draw a guide line for every whole f
				// FM: 875 .. 1080 (i.e. 10 * freq)
				// AM: 104 .. 323 (i.e. 0.2 * freq)
				let minF = Math.floor(nbGuideLinesPerFreq * this.freqMin);
				let maxF = Math.ceil(nbGuideLinesPerFreq * this.freqMax);
				let tickWidth = Math.floor(maxBandWidth / (maxF - minF + 1));
				let bandWidth = tickWidth * (maxF - minF + 1);
				let padding = Math.floor((canvas.width - bandWidth) / 2); // max half pixel wrong...

				// actual frequency
				let position = Math.floor(nbGuideLinesPerFreq * this.freq) - minF;
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
				for (let f = minF; f <= maxF; f += 1) {
					let x = (f - minF) * tickWidth + padding;
					ctx.beginPath();
					ctx.moveTo(x, 0);
					ctx.lineTo(x, f % 10 == 0 ? 30 : f % 5 == 0 ? 25 : 20);
					ctx.stroke();
					ctx.closePath();
					if (f % 10 == 0) {
						let freq = f / nbGuideLinesPerFreq;
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
