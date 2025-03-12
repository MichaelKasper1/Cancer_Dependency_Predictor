<template>
  <div v-if="plotData && plotData.data && plotData.layout" class="plot-container">
    <div ref="plotlyChart"></div>
  </div>
</template>

<script>
import Plotly from 'plotly.js-dist';

export default {
  props: {
    plotData: {
      type: Object,
      required: false,
      default: () => ({ data: [], layout: {} }) // Default empty structure
    }
  },
  watch: {
    plotData: {
      handler(newPlotData) {
        if (newPlotData && newPlotData.data && newPlotData.layout) {
          this.$nextTick(() => { // Ensure DOM updates before rendering
            this.renderPlot(newPlotData);
          });
        } else {
          console.error("Invalid plotData received:", newPlotData);
        }
      },
      immediate: true
    }
  },
  methods: {
    renderPlot(plotData) {
      const plotlyChart = this.$refs.plotlyChart;
      if (!plotlyChart) {
        console.error("Plotly div is not ready yet.");
        return;
      }
      Plotly.newPlot(plotlyChart, plotData.data, plotData.layout)
        .catch(err => console.error("Plotly render error:", err));
    }
  }
};
</script>

<style scoped>
.plot-container {
  width: 100%;
  height: 100%;
}
</style>