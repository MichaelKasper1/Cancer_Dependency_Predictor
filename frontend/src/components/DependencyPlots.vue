<template>
  <div v-if="plots">
    <div class="plot-container">
      <div ref="densityPlotElement"></div>
    </div>
    <div class="plot-container">
      <div ref="barPlotElement"></div>
    </div>
    <div class="plot-container">
      <label v-if="showCancerTypeSelect" for="cancerTypeSelect">Select Cancer Type: </label>
      <select v-if="showCancerTypeSelect" id="cancerTypeSelect" v-model="selectedCancerType" @change="handleCancerTypeChange">
        <option v-for="type in cancerTypes" :key="type" :value="type">{{ type }}</option>
      </select>
      <div ref="barSubPlotElement" v-if="!message"></div>
      <div v-if="message">{{ message }}</div>
    </div>
    <div class="plot-container">
      <div ref="networkPlotElement"></div>
      <button @click="downloadNetworkData">Download Network Data</button> <!-- Download button -->
    </div>
  </div>
</template>

<script>
import { ref, onMounted, onBeforeUnmount, nextTick } from 'vue';
import EventBus from '../utils/eventBus';
import Plotly from 'plotly.js-dist';

export default {
  name: 'DependencyPlots',
  setup() {
    const plots = ref(false);
    const densityPlotElement = ref(null);
    const barPlotElement = ref(null);
    const barSubPlotElement = ref(null);
    const networkPlotElement = ref(null);
    const selectedCancerType = ref('Lung');
    const cancerTypes = ref(['Lung', 'Bladder', 'Kidney', 'Breast', 'Pancreatic', 'Myeloma', 'Brain', 'Sarcoma', 'Ovarian', 'Leukemia', 'Colon/Colorectal', 'Skin', 'Lymphoma', 'Bone', 'Gastric', 'Thyroid', 'Neuroblastoma', 'Rhabdoid', 'Others', 'Endometrial/Uterine', 'Head and Neck', 'Bile Duct', 'Esophageal', 'Liver', 'Cervical', 'Eye', 'Liposarcoma', 'Prostate']);
    const showCancerTypeSelect = ref(false);
    const message = ref('Plot of predicted dependency scores of the selected gene across different cancer subtypes by choice available for cell line data only.');

    const getCsrfToken = () => {
      const meta = document.querySelector('meta[name="csrf-token"]');
      return meta ? meta.getAttribute('content') : '';
    };

    const fetchPlotData = async (url, plotElement, cancerType = null) => {
      try {
        const csrfToken = getCsrfToken();
        const body = cancerType ? JSON.stringify({ pancan_type: cancerType }) : null;
        const response = await fetch(url, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken,
          },
          body: body,
        });

        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }

        const responseData = await response.json();
        console.log('Response data from backend:', responseData);

        if (responseData.status === 'success') {
          const plotData = responseData.plot;
          if (plotElement) {
            try {
              const plotJson = JSON.parse(plotData);
              Plotly.newPlot(plotElement, plotJson.data, plotJson.layout);
              showCancerTypeSelect.value = true;
              message.value = '';
            } catch (error) {
              console.error('Error displaying plot:', error);
            }
          } else {
            console.error('Plot element not found');
          }
        } else if (responseData.status === 'message') {
          showCancerTypeSelect.value = false;
          message.value = responseData.message;
        } else {
          console.error('Error fetching plot data:', responseData.message);
        }
      } catch (error) {
        console.error('Error fetching plot data:', error);
      }
    };

    const handleRowSelected = async () => {
      plots.value = true;

      await nextTick(); // Ensure DOM is updated before fetching plot data

      await fetchPlotData('/api/create-density-plot', densityPlotElement.value);
      await fetchPlotData('/api/create-bar-plot', barPlotElement.value);
      await fetchPlotData('/api/create-bar-sub-plot', barSubPlotElement.value, selectedCancerType.value);
      await fetchPlotData('/api/create-network-plot', networkPlotElement.value);
    };

    const handleCancerTypeChange = async () => {
      await fetchPlotData('/api/create-bar-sub-plot', barSubPlotElement.value, selectedCancerType.value);
    };

    // New method to download network data
    const downloadNetworkData = async () => {
      try {
        const response = await fetch('/api/download-network', {
          method: 'GET',
          headers: {
            'X-CSRFToken': getCsrfToken(),
          },
        });

        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }

        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.style.display = 'none';
        a.href = url;
        a.download = 'network_data.csv';
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
      } catch (error) {
        console.error('Error downloading network data:', error);
      }
    };

    onMounted(() => {
      EventBus.on('plotCreated', handleRowSelected);
      EventBus.on('dataSourceChanged', (newDataSource) => {
        showCancerTypeSelect.value = newDataSource === 'cell-line';
      });
    });

    onBeforeUnmount(() => {
      EventBus.off('plotCreated', handleRowSelected);
      EventBus.off('dataSourceChanged');
    });

    return {
      plots,
      densityPlotElement,
      barPlotElement,
      barSubPlotElement,
      networkPlotElement,
      selectedCancerType,
      cancerTypes,
      showCancerTypeSelect,
      message,
      handleCancerTypeChange,
      downloadNetworkData, // Include the new method
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