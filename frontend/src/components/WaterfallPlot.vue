<template>
  <div v-if="dataReady" class="plot-container">
    <div v-if="dataReady" ref="plot"></div>
  </div>
</template>

<script>
import Plotly from 'plotly.js-dist';
import EventBus from '../utils/eventBus';
import { nextTick } from 'vue';

export default {
  name: 'WaterfallPlot',
  props: {
    column: String,
    gene: String,
  },
  data() {
    return {
      dataReady: false,
      plotData: null,
    };
  },
  async mounted() {
    EventBus.on('plotDataReady', this.handlePlotData);
    EventBus.on('newColumnOrGeneSelected', this.handleNewColumnSelected);
  },
  beforeUnmount() {
    EventBus.off('plotDataReady', this.handlePlotData);
    EventBus.off('newColumnOrGeneSelected', this.handleNewColumnSelected);
  },
  methods: {
    handlePlotData(plotData) {
      this.plotData = plotData;
      this.dataReady = true;
      nextTick(() => {
        this.createPlot();
      });
    },
    handleNewColumnSelected({ column, gene }) {
      console.log('New column or gene selected:', column, gene);
      this.fetchData(column, gene);
    },
    getCsrfToken() {
      const name = 'csrftoken';
      const cookies = document.cookie.split(';');
      for (let cookie of cookies) {
        cookie = cookie.trim();
        if (cookie.startsWith(name + '=')) {
          return cookie.substring(name.length + 1);
        }
      }
      return '';
    },
    async fetchData(column, gene) {
      try {
        const csrfToken = this.getCsrfToken();
        const response = await fetch('/api/selected-data', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken,
          },
          body: JSON.stringify({ column, gene }),
        });
        const result = await response.json();
        if (result.status === 'success') {
          EventBus.emit('plotDataReady', result.plot);
        } else {
          console.error('Error fetching data:', result.message);
        }
      } catch (error) {
        console.error('Error in fetchData:', error);
      }
    },
    createPlot() {
      const plotElement = this.$refs.plot;
      if (!plotElement) {
        console.error('Plot element is not available');
        return;
      }

      try {
        const plotData = JSON.parse(this.plotData);
        Plotly.newPlot(plotElement, plotData.data, plotData.layout);
        EventBus.emit('plotCreated'); // Emit the event after the plot is created
      } catch (error) {
        console.error('Error creating plot:', error);
      }
    },
  },
};
</script>

<style scoped>
.plot-container {
  max-width: 1300px;
  margin: 0 auto;
  padding: 20px;
  border: 1px solid #ddd;
  border-radius: 8px;
  background-color: #fff;
  box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
  margin-bottom: 20px; /* Add some space between plot containers */
}

h2 {
  text-align: center;
  margin-bottom: 20px;
}
</style>