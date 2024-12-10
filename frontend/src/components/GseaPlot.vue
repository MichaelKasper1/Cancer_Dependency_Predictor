<template>
  <div v-if="plotStarted" class="plot-container">
    <div ref="plotElement"></div>
    <!-- <div v-else-if="resultsReady">
      <p>Please select a term for a gene set enrichment plot.</p>
    </div> -->
  </div>
</template>

<script>
import { ref, onMounted, onBeforeUnmount } from 'vue';
import EventBus from '../utils/eventBus';
import Plotly from 'plotly.js-dist';

export default {
  name: 'GseaPlot',
  setup() {
    const plotData = ref(null);
    const plotElement = ref(null);
    const plotStarted = ref(false);
    const csrfToken = ref('');

    const fetchCsrfToken = async () => {
      try {
        const response = await fetch('/api/get-csrf-token', {
          method: 'GET',
          credentials: 'include',
        });
        const data = await response.json();
        csrfToken.value = data.csrfToken;
      } catch (error) {
        console.error('Failed to fetch CSRF token:', error);
      }
    };

    const handleRowSelected = async (data) => {
      plotStarted.value = true;
      console.log('Row data received in GseaPlot:', data);
      console.log('Column for plot', data.column);
      try {
        const payload = {
          column: data.column,
          pathway: data.row.Pathway
        };
        console.log('Payload to be sent:', payload);  // Log the payload

        const response = await fetch('/api/create-gsea-plot', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken.value,
          },
          body: JSON.stringify(payload),
        });

        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }

        const responseData = await response.json();
        console.log('Response data from backend:', responseData);

        if (responseData.status === 'success') {
          const plotData = responseData.plot;
          if (plotElement.value) {
            try {
              const plotJson = JSON.parse(plotData);
              Plotly.newPlot(plotElement.value, plotJson.data, plotJson.layout);
              plotStarted.value = true;
            } catch (error) {
              console.error('Error displaying plot:', error);
            }
          } else {
            console.error('Plot element not found');
          }
        } else {
          console.error('Error fetching GSEA data:', responseData.message);
        }
      } catch (error) {
        console.error('Error fetching GSEA data:', error);
      }
    };

    onMounted(() => {
      fetchCsrfToken();
      EventBus.on('rowSelected', handleRowSelected);
    });

    onBeforeUnmount(() => {
      EventBus.off('rowSelected', handleRowSelected);
    });

    return {
      plotData,
      plotStarted,
      plotElement
    };
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