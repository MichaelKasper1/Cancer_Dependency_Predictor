<template>
  <div class="tcga-data-upload">
    <div class="columns">
      <!-- Column 1: Choose Model -->
      <div class="column">
        <h3>Choose Model</h3>
        <div class="input-group">
          <label>
            <input type="radio" value="DeepDEP" v-model="selectedModel">
            <a href="https://pubmed.ncbi.nlm.nih.gov/34417181/" target="_blank">DeepDEP</a>
          </label>
          <p>Chiu YC, et al. Sci Adv. 2021</p>
          
          <div class="spacer"></div>
          
          <label>
            <input type="radio" value="ElasticNetModels" v-model="selectedModel">
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
            v-model="selectedOption2"
            :items="filteredOptions2"
            label="Select an Option"
            clearable
          ></v-autocomplete>
        </div>
        <div class="input-group">
          <label for="dropdown3" class="dropdown-label">Gene Alteration 2 (Optional)</label>
          <v-autocomplete
            v-model="selectedOption3"
            :items="filteredOptions3"
            label="Select an Option"
            clearable
          ></v-autocomplete>
        </div>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, computed, onMounted } from 'vue';

export default defineComponent({
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
    submit() {
      const payload = {
        selectedModel: this.selectedModel,
        selectedOption1: this.selectedOption1,
        selectedOption2: this.selectedOption2,
        selectedOption3: this.selectedOption3,
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
        })
        .catch(error => {
          console.error('Error submitting data:', error);
        });
    }
  },
  mounted() {
    this.fetchData();
  }
});
</script>

<style scoped>
.tcga-data-upload {
  text-align: center;
  margin: 20px;
}

.columns {
  display: flex;
  justify-content: space-around;
  margin-bottom: 20px;
  flex-wrap: wrap; /* Allow columns to wrap */
}

.column {
  flex: 1;
  margin: 0 10px;
  text-align: center; /* Center contents within the column */
}

.input-group {
  margin: 20px 0;
}

.spacer {
  height: 20px; /* Add space between model options */
}

button, .custom-file-upload {
  padding: 10px 20px;
  background-color: #42b983;
  color: white;
  border: none;
  cursor: pointer;
  margin: 6px; /* Add margin to buttons */
}

button:hover, .custom-file-upload:hover {
  background-color: #369f6e;
}

input[type="file"] {
  display: none;
}

label {
  margin: 0 10px;
}

.error-message {
  color: red;
  margin-top: 10px;
}

.delete-button {
  background: none;
  border: none;
  color: red;
  cursor: pointer;
  font-size: 1em;
  margin-left: 3px; /* Reduced margin */
  padding: 2px; /* Added padding to make the box smaller */
}

.delete-button:hover {
  color: darkred;
}

/* Modal styles */
.modal {
  display: flex;
  justify-content: center;
  align-items: center;
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.5);
  z-index: 1000;
}

.modal-content {
  background-color: white;
  padding: 20px;
  border-radius: 5px;
  max-width: 500px;
  width: 90%;
  text-align: left;
  position: relative;
}

.close {
  position: absolute;
  top: 10px;
  right: 10px;
  font-size: 1.5em;
  cursor: pointer;
}

.button-link {
  color: #551A8B; /* Replace with the color of the buttons */
  text-decoration: none;
}

.button-link:hover {
  text-decoration: underline;
}

/* Media query for screens narrower than 745px */
@media (max-width: 745px) {
  .columns {
    flex-direction: column; /* Stack columns vertically */
  }

  .column {
    margin-bottom: 20px; /* Add space between stacked columns */
  }
}

.dropdown-label {
  display: block;
  margin-bottom: 5px;
  color: grey;
}

.dropdown-select {
  width: 100%;
  padding: 10px;
  box-sizing: border-box;
}

.dropdown-search {
  width: 100%;
  padding: 10px;
  margin-top: 10px;
  box-sizing: border-box;
}
</style>