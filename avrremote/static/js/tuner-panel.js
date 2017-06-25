"use strict";
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
				required: true,
			},
		},
		data: function() {
			return {
				internalFreq: this.freq,
				canvasSize: {
					width: 0,
					height: 0,
				},
				canvas: null,
				ctx: null,
			}
		},
		mounted: function() {
			this.canvas = this.$refs.canvas;
			this.ctx = this.canvas.getContext('2d');
			this.ctx.font = '1.5rem roboto';

			this.updateDimensions();
			this.drawCanvas();
			window.addEventListener('resize', this.updateDimensions);
			this.$refs.canvas.addEventListener('mousedown', this.mouseDown);
		},
		beforeDestroy: function() {
			this.$refs.canvas.removeEventListener('mousedown', this.mouseDown);
			window.removeEventListener('resize', this.updateDimensions);
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
			maxBandWidth: function() {
				// the maximum bandwidth, making sure the first and last label fit in the canvas
				let minPadding = Math.ceil(this.ctx.measureText(this.freqMax + 'MM').width); // padding needed to print labels completely
				return this.canvasSize.width - minPadding;
			},
			minTickWidth: function() {
				// the minimal width of a tick, making sure that the tick labels don't overlap
				return Math.ceil(this.ctx.measureText(this.freqMax + ' ').width / 10); // 10 ticks MUST be wider than the width of one label, otherwise the labels overlap
			},
			nbTicksPerFreq: function() {
				// esimate how many ticks we want to draw
				let maxNbTicks = this.maxBandWidth / this.minTickWidth;
				let maxNbTicksPerFreq = maxNbTicks / (this.freqMax - this.freqMin);
				// now set this at max 10, and must be a divisor of 10, otherwise we get weird frequence labels
				return this.findClosestValidNbTicksPerFreq(maxNbTicksPerFreq);
			},
			// to be able to calculate in whole numbers, move the frequency scale to the 't' scale:
			// this scale is constructed, so that we want to draw a guide line for every whole t
			firstTick: function() {
				return Math.floor(this.nbTicksPerFreq * this.freqMin); // freqMin could be fractional!
			},
			lastTick: function() {
				return Math.ceil(this.nbTicksPerFreq * this.freqMax); // freqMax could be fractional!
			},
			tickWidth: function() {
				// the width of one tick in pixels
				// we got a minimum tick width, but maybe it can be wider and still fit in the window
				return Math.max(this.minTickWidth, Math.floor(this.maxBandWidth / (this.lastTick - this.firstTick)));
			},
			padding: function() {
				// the padding we need left and right to center the band (in pixels)
				let bandWidth = this.tickWidth * (this.lastTick - this.firstTick);
				return Math.floor((this.canvasSize.width - bandWidth) / 2); // max half pixel wrong...
			}
		},
		methods: {
			updateDimensions: function() {
				// settings this here will make sure the computed properties are invalidated!
				this.canvasSize.width = this.canvas.parentElement.clientWidth;
				this.canvasSize.height = this.canvas.parentElement.clientHeight;

				// resize the real thing
				this.canvas.width = this.canvasSize.width;
				this.canvas.height = this.canvasSize.height;
				this.drawCanvas();
			},
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
				let ctx = this.ctx;

				// background
				ctx.fillStyle = '#999999';
				ctx.fillRect(0, 0, this.canvasSize.width, this.canvasSize.height);

				// actual frequency
				let position = Math.floor(this.nbTicksPerFreq * this.internalFreq) - this.firstTick;
				ctx.strokeStyle = '#f00';
				ctx.lineWidth = 4;
				ctx.beginPath();
				ctx.moveTo(position * this.tickWidth + this.padding, 0);
				ctx.lineTo(position * this.tickWidth + this.padding, this.canvasSize.height);
				ctx.stroke();
				ctx.closePath();

				// frequency band
				ctx.strokeStyle = '#fff';
				ctx.fillStyle = '#fff';
				ctx.lineWidth = 1;
				ctx.font = '1.5rem roboto';
				for (let tick = this.firstTick; tick <= this.lastTick; tick += 1) {
					let x = (tick - this.firstTick) * this.tickWidth + this.padding;
					ctx.beginPath();
					ctx.moveTo(x, 0);
					ctx.lineTo(x, tick % 10 == 0 ? 30 : tick % 5 == 0 ? 25 : 20);
					ctx.stroke();
					ctx.closePath();
					if (tick % 10 == 0) {
						let freq = tick / this.nbTicksPerFreq;
						let textWidth = ctx.measureText(freq).width;
						ctx.fillText(freq, x - textWidth / 2, 50);
					}
				}
			},
			pagex2freq: function(pageX) {
				let x = pageX - this.canvas.getBoundingClientRect().left;
				if (x < this.padding) {
					x = this.padding;
				} else if (x > this.canvasSize.width - this.padding) {
					x = this.canvasSize.width - this.padding;
				}
				let bandWidth = this.canvasSize.width - 2 * this.padding;
				let tempFreq = this.freqMin + (this.freqMax - this.freqMin) * (x - this.padding) /
					bandWidth;
				// round to the closest allowed frequency
				return this.freqStep * Math.round(tempFreq / this.freqStep);
			},
			mouseDown: function(e) {
				if (e.button == 0) {
					e.preventDefault();
					let vm = this;
					var move = function(e) {
						vm.internalFreq = vm.pagex2freq(e.pageX);
						vm.$emit('freqSeek', vm.internalFreq);
						vm.drawCanvas();
					};
					var mouseUp = function(e) {
						vm.canvas.removeEventListener('mousemove', move);
						vm.canvas.removeEventListener('mouseup', mouseUp);
						vm.canvas.removeEventListener('mouseleave', mouseCancel);
						vm.internalFreq = vm.pagex2freq(e.pageX);
						vm.$emit('freqChange', vm.internalFreq);
					};
					var mouseCancel = function(e) {
						vm.canvas.removeEventListener('mousemove', move);
						vm.canvas.removeEventListener('mouseup', mouseUp);
						vm.canvas.removeEventListener('mouseleave', mouseCancel);
						vm.internalFreq = vm.freq;
						vm.drawCanvas();
					};
					vm.canvas.addEventListener('mousemove', move);
					vm.canvas.addEventListener('mouseup', mouseUp);
					vm.canvas.addEventListener('mouseleave', mouseCancel);
				}
			},
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
		data: function() {
			return {
				seekPosition: this.item.freq,
			}
		},
		computed: {
			freqUnit: function() {
				switch (this.item.band) {
					case "AM":
						return 'KHz';
					case "FM":
						return 'MHz';
					default:
						return '';
				}
			},
			freqFormat: function() {
				switch (this.item.band) {
					case "AM":
						return '%.0f';
					case "FM":
						return '%.2f';
					default:
						return '';
				}
			},
			displaySeekPosition: function() {
				return sprintf(this.freqFormat, this.seekPosition);
			}
		},
		watch: {
			'item.freq': function(freq) {
				this.seekPosition = freq;
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
