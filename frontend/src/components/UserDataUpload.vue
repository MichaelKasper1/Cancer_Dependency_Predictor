<template>
  <div class="user-data-input">
    <div class="columns">
      <!-- Column 1: Choose Model -->
      <div class="column">
        <h3>Choose Model</h3>
        <div class="input-group">
          <label>
            <input type="radio" value="DeepDEP" v-model="selectedModel">
            <a href="https://pubmed.ncbi.nlm.nih.gov/34417181/" target="_blank"> DeepDEP</a>
          </label>
          <p>Chiu YC, et al. Sci Adv. 2021</p>
          
          <div class="spacer"></div>
          
          <label>
            <input type="radio" value="Elastic Net Models" v-model="selectedModel">
            <a href="https://pubmed.ncbi.nlm.nih.gov/39009815/" target="_blank"> Elastic Net Models</a>
          </label>
          <p>Shi X, et al. Nat Cancer. 2024</p>
        </div>
      </div>

      <!-- Column 2: Upload Data -->
      <div class="column">
        <h3>Upload Data</h3>
        <div class="input-group">
          <label for="file-upload" class="custom-file-upload">
            Upload Data (TXT, CSV)
          </label>
          <input id="file-upload" type="file" accept=".txt, .csv" @change="handleFileUpload">
          <p v-if="uploadedFileName"><br>{{ uploadedFileName }}</p>
          <p v-if="fileError" class="error-message">{{ fileError }}</p>
        </div>
        <div class="input-group">
          <button @click="submitExample">Use Example Data</button>
        </div>
      </div>

      <!-- Column 3: Describe Data -->
      <div class="column">
        <h3>Describe Data</h3>
        <div class="input-group">
          <p>Is your data log transformed?</p>
          <label>
            <input type="radio" value="log" v-model="logTransformed"> Yes
          </label>
          <label>
            <input type="radio" value="not-log" v-model="logTransformed"> No
          </label>
        </div>
        <div class="input-group">
          <p>Is your data from a cell line or a tumor?</p>
          <label>
            <input type="radio" value="tumor" v-model="dataSource" :disabled="selectedModel === 'Elastic Net Models'"> Tumor
          </label>
          <label>
            <input type="radio" value="cell-line" v-model="dataSource"> Cell Line
          </label>
          <div v-if="selectedModel === 'Elastic Net Models'">Tumor predictions only available for DeepDEP.</div>
        </div>
        <div class="input-group">
          <p>Is your data stored as a normalized expression unit?</p>
          <label>
            <input type="radio" value="TPM" v-model="expressionUnit"> TPM
          </label>
          <label>
            <input type="radio" value="FPKM" v-model="expressionUnit"> FPKM
          </label>
        </div>
      </div>

      <!-- Column 4: Select Gene Set -->
      <div class="column">
        <h3>Select Gene Set</h3>
        <div class="input-group">
          <label for="gene-set">Select a Gene Set:</label>
          <select id="gene-set" v-model="selectedGeneSet" style="width: 200px;">
            <option value="" disabled selected>Select a Gene Set</option>
            <option value="default-gene-set">Default 1298 Cancer associated genes</option>
            <option v-for="geneSet in columnNames" :key="geneSet" :value="geneSet">
              {{ geneSet }}
            </option>
          </select>
        </div>
      </div>
    </div>

    <!-- Submit button -->
    <div class="input-group">
      <button @click="submitForm">Submit</button>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent } from 'vue';

export default defineComponent({
  data() {
    return {
      selectedModel: 'DeepDEP',
      logTransformed: 'not-log',
      dataSource: 'Tumor',
      expressionUnit: 'TPM',
      selectedGeneSet: '',
      columnNames: [], // This will be populated from the backend
      fileError: '',
      exampleData: '', // This will be populated from the backend
      uploadedFileName: '',
      errorMessage: '',
    };
  },
  methods: {
    submitForm() {
      // Handle form submission
    },
    // handleFileUpload(event: Event) {
    //   const file = (event.target as HTMLInputElement).files?.[0];
    //   if (!file) return;

    //   const reader = new FileReader();
    //   reader.onload = (e) => {
    //     const content = e.target?.result as string;
    //     const lines = content.split('\n');

    //     // Ensure file has more than 2 rows
    //     if (lines.length < 2) {
    //       this.fileError = 'File is too short. Must include more than one row.';
    //       return;
    //     }

    //     // Ensure the data has at least 2 columns
    //     const header = lines[0].split(/\t|,/);
    //     if (header.length < 2) {
    //       this.fileError = 'File must have at least 2 columns. One for a gene symbol, at least one for expression values.';
    //       return;
    //     }

    //     // Ensure the first column has strings for the data
    //     const firstRow = lines[1].split(/\t|,/);
    //     if (!isNaN(Number(firstRow[0]))) {
    //       console.warn('First column should contain gene symbols. Please ensure the gene symbols are in the first column.');
    //     }

    //     // Ensure the second column has numbers for the data
    //     const secondRow = lines[1].split(/\t|,/);
    //     if (isNaN(Number(secondRow[1]))) {
    //       this.fileError = 'Second column must contain numeric values for gene expression.';
    //       return;
    //     }

    //     this.fileError = ''; // Clear any previous errors
    //     this.uploadedFileName = file.name;
    //     // Process the file content
    //   };

    //   reader.readAsText(file);
    // },
    submitExample() {
      // Populate the upload data with example data
      this.uploadedFileName = 'example_data.txt';
      this.fileError = '';
    },
    resetBackendData() {
      fetch('/api/reset-backend-data', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          selectedModel: this.selectedModel,
          logTransformed: this.logTransformed,
          dataSource: this.dataSource,
          expressionUnit: this.expressionUnit,
          selectedGeneSet: this.selectedGeneSet,
        }),
      });
      // Hide other components
    },
  },
  watch: {
    selectedModel(newVal) {
      if (newVal === 'Elastic Net Models') {
        this.dataSource = 'cell-line';
        // Display message and disable Tumor option
      }
      this.resetBackendData();
    },
    dataSource(newVal, oldVal) {
      if (newVal !== oldVal) {
        this.resetBackendData();
      }
    },
    selectedGeneSet(newVal, oldVal) {
      if (newVal !== oldVal) {
        this.resetBackendData();
      }
    },
    logTransformed(newVal, oldVal) {
      if (newVal !== oldVal) {
        this.resetBackendData();
      }
    },
    expressionUnit(newVal, oldVal) {
      if (newVal !== oldVal) {
        this.resetBackendData();
      }
    },
  },
  mounted() {
    // Fetch column names and example data from the backend
    fetch('/api/get-column-names')
      .then(response => response.json())
      .then(data => {
        console.log("Column names:", data.columnNames);
        this.columnNames = data.columnNames;
        this.exampleData = data.exampleData;
      });
  },
});
</script>

<style scoped>
.user-data-input {
  text-align: center;
  margin: 20px;
}

.columns {
  display: flex;
  justify-content: space-around;
  margin-bottom: 20px;
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
</style>