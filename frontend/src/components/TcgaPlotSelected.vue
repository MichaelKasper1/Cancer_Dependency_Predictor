<template>
  <div class="plot-container">
    <!-- Boxplot -->
    <div v-if="boxplotData && boxplotData.data && boxplotData.layout" class="plot-section">
      <h3>Boxplot</h3>
      <div ref="boxplotChart"></div>
    </div>

    <!-- Survival Plot -->
    <div v-if="survivalData && survivalData.data && survivalData.layout" class="plot-section">
      <h3>Survival Plot</h3>
      <div ref="survivalChart"></div>
    </div>
  </div>
</template>

<script>
import Plotly from 'plotly.js-dist';

export default {
  props: {
    boxplotData: {
      type: Object,
      required: false,
      default: () => ({ data: [], layout: {} }) // Default empty structure for boxplot
    },
    survivalData: {
      type: Object,
      required: false,
      default: () => ({ data: [], layout: {} }) // Default empty structure for survival plot
    }
  },
  watch: {
    boxplotData: {
      handler(newBoxplotData) {
        if (newBoxplotData && newBoxplotData.data && newBoxplotData.layout) {
          this.$nextTick(() => {
            this.renderBoxplot(newBoxplotData);
          });
        } else {
          console.error("Invalid boxplotData received:", newBoxplotData);
        }
      },
      immediate: true
    },
    survivalData: {
      handler(newSurvivalData) {
        if (newSurvivalData && newSurvivalData.data && newSurvivalData.layout) {
          this.$nextTick(() => {
            this.renderSurvivalPlot(newSurvivalData);
          });
        } else {
          console.error("Invalid survivalData received:", newSurvivalData);
        }
      },
      immediate: true
    }
  },
  methods: {
    renderBoxplot(plotData) {
      const boxplotChart = this.$refs.boxplotChart;
      if (!boxplotChart) {
        console.error("Boxplot div is not ready yet.");
        return;
      }
      Plotly.newPlot(boxplotChart, plotData.data, plotData.layout)
        .catch(err => console.error("Plotly render error for boxplot:", err));
    },
    renderSurvivalPlot(plotData) {
      const survivalChart = this.$refs.survivalChart;
      if (!survivalChart) {
        console.error("Survival plot div is not ready yet.");
        return;
      }
      Plotly.newPlot(survivalChart, plotData.data, plotData.layout)
        .catch(err => console.error("Plotly render error for survival plot:", err));
    }
  }
};
</script>

<style scoped>
.plot-container {
  width: 100%;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.plot-section {
  width: 100%;
  height: 500px;
}
</style>