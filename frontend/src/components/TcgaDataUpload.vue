<template>
  <div class="tcga-data-upload">
    <div class="columns">
      <!-- Column 1: Choose Model -->
      <div class="column">
        <h3>Choose Model</h3>
        <div class="input-group">
          <label for="deepdep">
            <input type="radio" id="deepdep" value="DeepDEP" v-model="selectedModel">
            <a href="https://pubmed.ncbi.nlm.nih.gov/34417181/" target="_blank">DeepDEP</a>
          </label>
          <p>Chiu YC, et al. Sci Adv. 2021</p>
          
          <div class="spacer"></div>
          
          <label for="elasticnet">
            <input type="radio" id="elasticnet" value="ElasticNetModels" v-model="selectedModel">
            <a href="https://pubmed.ncbi.nlm.nih.gov/39009815/" target="_blank">Elastic Net Models</a>
          </label>
          <p>Shi X, et al. Nat Cancer. 2024</p>
        </div>
      </div>

      <!-- Column 2: Select TCGA Project -->
      <div class="column">
        <h3>Select TCGA Project</h3>
        <div class="input-group">
          <label for="dropdown1" class="dropdown-label">TCGA Project</label>
          <v-autocomplete
            id="dropdown1"
            v-model="selectedOption1"
            :items="filteredOptions1"
            label="Select an Option"
            clearable
          ></v-autocomplete>
        </div>
      </div>

      <!-- Column 3: Select Gene Alteration(s) of Interest -->
      <div class="column">
        <h3>Select Gene Alteration(s) of Interest</h3>
        <div class="input-group">
          <label for="dropdown2" class="dropdown-label">Gene Alteration 1</label>
          <v-autocomplete
            id="dropdown2"
            v-model="selectedOption2"
            :items="filteredOptions2"
            label="Select an Option"
            clearable
          ></v-autocomplete>
        </div>
        <div class="input-group">
          <label for="dropdown3" class="dropdown-label">Gene Alteration 2 (Optional)</label>
          <v-autocomplete
            id="dropdown3"
            v-model="selectedOption3"
            :items="filteredOptions3"
            label="Select an Option"
            clearable
          ></v-autocomplete>
        </div>
      </div>
    </div>

    <!-- TcgaSummary component -->
    <TcgaSummary
      v-if="selectedOption1 && selectedOption2 && distTable"
      :selectedModel="selectedModel"
      :selectedOption1="selectedOption1"
      :selectedOption2="selectedOption2"
      :selectedOption3="selectedOption3"
      :sampleGroup="distTable"
    />
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, computed, onMounted, watch } from 'vue';
import TcgaSummary from './TcgaSummary.vue';

export default defineComponent({
  components: {
    TcgaSummary
  },
  data() {
    return {
      selectedModel: 'DeepDEP',
      selectedOption1: '',
      selectedOption2: '',
      selectedOption3: '',
      searchQuery1: '',
      searchQuery2: '',
      searchQuery3: '',
      options1: [] as string[], // Placeholder options
      options2: [] as string[], // Placeholder options
      options3: [] as string[], // Placeholder options
      distTable: '' // Add this data property to store the distTable JSON
    };
  },
  computed: {
    filteredOptions1() {
      return this.options1.filter(option => option.toLowerCase().includes(this.searchQuery1.toLowerCase()));
    },
    filteredOptions2() {
      return this.options2.filter(option => option.toLowerCase().includes(this.searchQuery2.toLowerCase()));
    },
    filteredOptions3() {
      return this.options3.filter(option => option.toLowerCase().includes(this.searchQuery3.toLowerCase()));
    }
  },
  methods: {
    fetchData() {
      fetch('/api/get-column-names-tcga')
        .then(response => response.json())
        .then(data => {
          console.log('Fetched data:', data); // Print the fetched data to the console for debugging
          this.options1 = data.Cancer_types_tab3.map((item: { Cancer_types_tab3: string }) => item.Cancer_types_tab3);
          this.options2 = data.select_gene_tab3.map((item: { select_gene_tab3: string }) => item.select_gene_tab3);
          this.options3 = data.select_gene_tab3.map((item: { select_gene_tab3: string }) => item.select_gene_tab3);
        })
        .catch(error => {
          console.error('Error fetching data:', error);
        });
    },
    submitData() {
      if (!this.selectedOption1 || !this.selectedOption2) {
        console.log('Both TCGA project and Gene Alteration 1 must be selected.');
        return;
      }

      const payload = {
        selectedModel: this.selectedModel,
        selectedOption1: this.selectedOption1,
        selectedOption2: this.selectedOption2,
        selectedOption3: this.selectedOption3
      };

      fetch('/api/submit-data', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(payload),
      })
        .then(response => response.json())
        .then(data => {
          console.log('Response from backend:', data);
          if (data.status === 'success') {
            // Update the selected data with the response from the backend
            this.selectedModel = data.selectedModel;
            this.selectedOption1 = data.selectedOption1;
            this.selectedOption2 = data.selectedOption2;
            this.selectedOption3 = data.selectedOption3;
            this.distTable = data.distTable; // Update the distTable with the response data
          } else {
            console.error('Error:', data.message);
          }
        })
        .catch(error => {
          console.error('Error submitting data:', error);
        });
    }
  },
  mounted() {
    this.fetchData();
  },
  watch: {
    selectedOption1(newVal, oldVal) {
      if (newVal) {
        this.submitData();
      }
    },
    selectedOption2(newVal, oldVal) {
      if (newVal) {
        this.submitData();
      }
    }
  }
});
</script>

<style scoped>
.tcga-data-upload {
  margin: 20px;
}

.columns {
  display: flex;
  justify-content: space-between;
}

.column {
  flex: 1;
  margin: 10px;
}

.input-group {
  margin-bottom: 20px;
}

.dropdown-label {
  display: block;
  margin-bottom: 5px;
}

.spacer {
  height: 20px;
}
</style>