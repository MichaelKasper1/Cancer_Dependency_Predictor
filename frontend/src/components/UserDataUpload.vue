<template>
  <div class="user-datas-input">
    <div class="columns">
      <!-- Column 1: Choose Model -->
      <div class="column">
        <h3>Choose Model</h3>
        <div class="input-group">
          <label for="model-deepdep">
            <input id="model-deepdep" type="radio" value="DeepDEP" v-model="selectedModel">
            <a href="https://pubmed.ncbi.nlm.nih.gov/34417181/" target="_blank">DeepDEP</a>
          </label>
          <p>Chiu YC, et al. Sci Adv. 2021</p>
          
          <div class="spacer"></div>
          
          <label for="model-elasticnet">
            <input id="model-elasticnet" type="radio" value="ElasticNetModels" v-model="selectedModel">
            <a href="https://pubmed.ncbi.nlm.nih.gov/39009815/" target="_blank">Elastic Net Models</a>
          </label>
          <p>Shi X, et al. Nat Cancer. 2024</p>
        </div>
      </div>

      <!-- Column 2: Upload Gene Data -->
      <div class="column">
        <h3>Upload Gene Expression Data</h3>
        <div class="input-group">
          <a href="#" class="button-link" @click.prevent="openModal">Data format requirements</a>
        </div>
        <div class="input-group">
          <button class="button" @click="triggerFileUpload">Upload Data</button>
          <input id="file-upload" type="file" accept=".txt, .csv" @change="handleFileUpload" style="display: none;">
        </div>
        <div class="input-group">
          <button class="button" @click="useExample">Use Example Data</button>
        </div>
        <p v-if="uploadedFileName">
            {{ uploadedFileName }}
            <button class="delete-button" @click="deleteFile">x</button>
        </p>
          <p v-if="fileError" class="error-message">{{ fileError }}</p>
      </div>

      <!-- Column 3: Describe Data -->
      <div class="column">
        <h3>Describe Data</h3>
        <div class="input-group">
          <p>Is your data log transformed?</p>
          <label for="log-no">
            <input id="log-no" type="radio" value="not-log" v-model="logTransformed"> No
          </label>
          <label for="log-yes">
            <input id="log-yes" type="radio" value="log" v-model="logTransformed"> Yes
          </label>
        </div>
        <div class="input-group">
          <p>Is your data from cell lines or tumors?</p>
          <label for="data-tumor">
            <input id="data-tumor" type="radio" value="tumor" v-model="dataSource" :disabled="selectedModel === 'ElasticNetModels'"> Tumor
          </label>
          <label for="data-cell-line">
            <input id="data-cell-line" type="radio" value="cell-line" v-model="dataSource"> Cell Line
          </label>
          <div v-if="selectedModel === 'ElasticNetModels'">Tumor predictions only available for DeepDEP.</div>
        </div>
        <div class="input-group">
          <p>Is your data a normalized expression unit?</p>
          <label for="unit-tpm">
            <input id="unit-tpm" type="radio" value="TPM" v-model="expressionUnit"> TPM
          </label>
          <label for="unit-fpkm">
            <input id="unit-fpkm" type="radio" value="FPKM" v-model="expressionUnit"> FPKM
          </label>
        </div>
      </div>

      <!-- Column 4: Select Gene Set -->
      <div class="column">
        <h3>Select Gene Set</h3>
        <div class="input-group">
          <label for="gene-set" class="gene-set-label">Select gene set of interest for results</label>
          <v-autocomplete
            id="gene-set"
            v-model="selectedGeneSet"
            :items="filteredGeneSets"
            label="Select a Gene Set"
            clearable
          ></v-autocomplete>
        </div>
      </div>

    </div>

    <!-- Submit button -->
    <div class="input-group">
      <button @click="submit">Submit</button>
    </div>

    <!-- Modal -->
    <div v-if="showModal" class="modal" @click.self="closeModal">
      <div class="modal-content">
        <span class="close" @click="closeModal">&times;</span>
        <h2>Data Requirements</h2>
        <p>Your data should be in a .txt or .csv format with the following columns:</p>
        <ul>
          <li>Column 1: Gene symbols</li>
          <li>Column 2: Numeric values for gene expression</li>
          <!-- Add more requirements as needed -->
        </ul>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent } from 'vue';
import { ref, onMounted, onBeforeUnmount, computed } from 'vue';
import { VAutocomplete } from 'vuetify/components'; // Import VAutocomplete
// @ts-ignore
import EventBus from '../utils/eventBus';

export default defineComponent({
  components: {
    VAutocomplete, // Register VAutocomplete
  },
  data() {
    return {
      selectedModel: 'DeepDEP',
      logTransformed: 'not-log',
      dataSource: 'tumor',
      expressionUnit: 'TPM',
      selectedGeneSet: 'default-gene-set',
      columnNames: [] as string[],
      searchQuery: '',
      filteredGeneSets: [] as string[],
      file: null as File | null,
      fileError: '',
      uploadedFileName: '',
      errorMessage: '',
      showModal: false,
      csrfToken: '',
    };
  },
  methods: {
    async fetchCsrfToken() {
      fetch('/api/get-csrf-token', {
        method: 'GET',
        credentials: 'include',
      })
        .then(response => response.json())
        .then(data => {
          this.csrfToken = data.csrfToken;
        })
        .catch(error => {
          console.error('Failed to fetch CSRF token:', error);
        });
    },
    filterGeneSets() {
      const query = this.searchQuery.toLowerCase(); // Ensure searchQuery is a string
      this.filteredGeneSets = this.columnNames.filter(geneSet => geneSet.toLowerCase().includes(query));
    },
    submit() {
      if (!this.file) {
        this.fileError = 'Please upload a file before submitting.';
        return;
      }

      const formData = new FormData();
      formData.append('selectedModel', this.selectedModel);
      formData.append('logTransformed', this.logTransformed);
      formData.append('dataSource', this.dataSource);
      formData.append('expressionUnit', this.expressionUnit);
      formData.append('selectedGeneSet', this.selectedGeneSet);
      formData.append('file', this.file);

      fetch('/api/process-data', {
        method: 'POST',
        body: formData,
        headers: {
          'X-CSRFToken': this.csrfToken // Corrected to this.csrfToken
        }
      })
      .then(response => response.json())
      .then(data => {
        console.log('Response from backend:', data);
        if (data.status === 'success') {
          EventBus.emit('dataProcessed', data); // Emit the event using EventBus
        } else {
          console.error('Error:', data.error);
        }
      })
      .catch(error => {
        console.error('Error uploading file:', error);
      });
    },
    useExample() {
      fetch('/api/get-example-file')
        .then(response => {
          if (!response.ok) {
            throw new Error('Network response was not ok');
          }
          return response.json();
        })
        .then(data => {
          const geneSymbols = data.Gene || [];
          const cclA = data.CCL_A || [];
          const cclB = data.CCL_B || [];
          const cclC = data.CCL_C || [];

          if (geneSymbols.length === 0 || cclA.length === 0 || cclB.length === 0 || cclC.length === 0) {
            throw new Error('Invalid data format');
          }

          const exampleContent = `Gene,CCL_A,CCL_B,CCL_C\n${geneSymbols.map((gene: string, index: number) => `${gene},${cclA[index]},${cclB[index]},${cclC[index]}`).join('\n')}`;
          const blob = new Blob([exampleContent], { type: 'text/plain' });
          const exampleFile = new File([blob], 'example_data.txt', { type: 'text/plain' });

          // Set the file data property to the mock file object
          this.file = exampleFile;
          this.uploadedFileName = exampleFile.name;
          this.fileError = '';
        })
        .catch(error => {
          this.errorMessage = 'Failed to load example file.';
          console.error('There was a problem with the fetch operation:', error);
        });
    },
    triggerFileUpload() {
      const fileUploadElement = document.getElementById('file-upload');
      if (fileUploadElement) {
        fileUploadElement.click();
      }
    },
    fetchColumnNames() {
      fetch('/api/get-column-names')
        .then(response => {
          if (!response.ok) {
            throw new Error('Network response was not ok');
          }
          return response.json();
        })
        .then(data => {
          this.columnNames = data.columnNames;
          this.filteredGeneSets = this.columnNames; // Ensure filteredGeneSets is populated
        })
        .catch(error => {
          this.errorMessage = 'Failed to load column names.';
        });
    },
    resetBackendData() {
      fetch('/api/reset-backend-data', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': this.csrfToken,
        },
        body: JSON.stringify({
          selectedModel: this.selectedModel,
          logTransformed: this.logTransformed,
          dataSource: this.dataSource,
          expressionUnit: this.expressionUnit,
          selectedGeneSet: this.selectedGeneSet,
        }),
        credentials: 'include',
      });
    },
    handleFileUpload(event: Event) {
      // @ts-ignore
      const file = event.target.files[0]; 
      if (file) {
        this.validateFile(file)
          .then(isValid => {
            if (isValid) {
              this.file = file; // Store the file in the data property
              this.uploadedFileName = file.name; // Update the uploaded file name
              this.fileError = ''; // Clear any previous error messages
              console.log('File uploaded:', file);
            } else {
              this.file = null;
              this.uploadedFileName = '';
            }
          })
          .catch(error => {
            this.fileError = error.message;
            this.file = null;
            this.uploadedFileName = '';
          });
      }
    },
    validateFile(file: File): Promise<boolean> {
      return new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.onload = (e) => {
          const content = e.target?.result as string;
          const lines = content.split('\n');

          // Ensure file has more than 2 rows
          if (lines.length < 2) {
            reject(new Error('File is too short. Must include more than one row.'));
            return;
          }

          // Ensure the data has at least 2 columns
          const header = lines[0].split(/\t|,/);
          if (header.length < 2) {
            reject(new Error('File must have at least 2 columns. One for a gene symbol, at least one for expression values.'));
            return;
          }

          // Ensure the first column has strings for the data and print warning if not
          const firstRow = lines[1].split(/\t|,/);
          if (!isNaN(Number(firstRow[0]))) {
            reject(new Error('First column should contain gene symbols. If not, please ensure the gene symbols are in the first column.'));
            return;
          }

          // Ensure that the second column has numbers for the data other than the first row or they can at least be coerced to numbers
          const secondRow = lines[1].split(/\t|,/);
          if (isNaN(Number(secondRow[1]))) {
            reject(new Error('Second column must contain numeric values for gene expression.'));
            return;
          }

          // Add other user input data checks here

          resolve(true);
        };

        reader.onerror = () => {
          reject(new Error('Error reading file.'));
        };

        reader.readAsText(file);
      });
    },
    openModal() {
      this.showModal = true;
    },
    closeModal() {
      this.showModal = false;
    },
    deleteFile() {
      this.file = null;
      this.uploadedFileName = '';
      this.resetBackendData();
    }
  },
  watch: {
    searchQuery() {
      this.filterGeneSets();
    },
    selectedModel(newVal) {
      if (newVal === 'ElasticNetModels') {
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
    this.fetchColumnNames();
    this.fetchCsrfToken();
    this.filteredGeneSets = this.columnNames;
  },
  setup() {
    interface TableRow {
      [key: string]: any;
    }
    const tableData = ref<TableRow[]>([]);
    interface TableHeader {
      text: string;
      value: string;
    }
    const headers = ref<TableHeader[]>([]);
    const currentPage = ref(1);
    const rowsPerPage = ref(10);
    const searchQuery = ref('');
    const resultsReady = ref(false);
    const sortKey = ref('');
    const sortOrder = ref<'asc' | 'desc'>('asc');
    const selectedColumn = ref('');
    const selectedGene = ref('');

    const nonSelectableColumns = [
      "gene",
      "Prediction performance (Corr)",
      "Prediction Percentile TCGA",
      "Prediction DepMap percentile (CERES; n=278)",
      "Predicted DepMap range (CERES; n=278)",
      "Real DepMap percentile (CCLE; n=278)",
      "Real DepMap range (CCLE; n=278)",
      "Prediction range (TCGA; n=8238)",
      "Real DepMap range (Chronos; n=996)",
      "Ensembl gene ID",
      "Entrez gene ID",
      "Synonym",
      "Cancer syndrome",
      "Tissue type",
      "Molecular genetics",
      "Role in cancer",
      "Mutation types",
      "Translocation partner",
      "Other syndrome"
    ];

    const handleDataProcessed = (data: any) => {
      if (data?.result?.length) {
        tableData.value = data.result;

        // Generate headers directly from the data
        headers.value = Object.keys(tableData.value[0]).map(key => ({
          text: key,
          value: key
        }));

        resultsReady.value = true;
        console.log('Results are ready and the table is rendered.');
      }
    };

    onMounted(() => {
      EventBus.on('dataProcessed', handleDataProcessed);
    });

    onBeforeUnmount(() => {
      EventBus.off('dataProcessed', handleDataProcessed);
    });

    const totalPages = computed(() => Math.ceil(filteredData.value.length / rowsPerPage.value));

    const paginatedData = computed(() => {
      const start = (currentPage.value - 1) * rowsPerPage.value;
      const end = start + rowsPerPage.value;
      return sortedData.value.slice(start, end);
    });

    const filteredData = computed(() => {
      return tableData.value.filter(row => {
        return Object.values(row).some(value =>
          String(value).toLowerCase().includes(searchQuery.value.toLowerCase())
        );
      });
    });

    const sortedData = computed(() => {
      return filteredData.value.slice().sort((a, b) => {
        const aValue = a[sortKey.value];
        const bValue = b[sortKey.value];
        if (aValue === bValue) return 0;
        const order = sortOrder.value === 'asc' ? 1 : -1;
        return (aValue > bValue ? 1 : -1) * order;
      });
    });

    const sortTable = (key: string) => {
      if (sortKey.value === key) {
        sortOrder.value = sortOrder.value === 'asc' ? 'desc' : 'asc';
      } else {
        sortKey.value = key;
        sortOrder.value = 'asc';
      }
    };

    const selectColumnOrGene = (key: string, gene: string) => {
      if (!nonSelectableColumns.includes(key)) {
        if (key !== 'gene') {
          selectedColumn.value = key;
        }
        selectedGene.value = gene;

        EventBus.emit('newColumnOrGeneSelected', { column: selectedColumn.value, gene: selectedGene.value });
      }
    };

    const nextPage = () => {
      if (currentPage.value < totalPages.value) {
        currentPage.value++;
      }
    };

    const prevPage = () => {
      if (currentPage.value > 1) {
        currentPage.value--;
      }
    };

    const saveData = () => {
      const csvContent = [
        headers.value.map(header => header.text).join(','),
        ...tableData.value.map(row => headers.value.map(header => row[header.value]).join(','))
      ].join('\n');

      const dataUri = 'data:text/csv;charset=utf-8,' + encodeURIComponent(csvContent);
      const exportFileDefaultName = 'data.csv';

      const linkElement = document.createElement('a');
      linkElement.setAttribute('href', dataUri);
      linkElement.setAttribute('download', exportFileDefaultName);
      linkElement.click();
    };

    return {
      tableData,
      headers,
      currentPage,
      rowsPerPage,
      totalPages,
      paginatedData,
      nextPage,
      prevPage,
      searchQuery,
      filteredData,
      saveData,
      resultsReady,
      sortKey,
      sortOrder,
      sortTable,
      selectedColumn,
      selectedGene,
      selectColumnOrGene,
    };
  }
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

.table-container {
  max-width: 1300px;
  margin: 0 auto;
  padding: 20px;
  border: 1px solid #ddd;
  border-radius: 8px;
  background-color: #fff;
  box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
  margin-bottom: 20px;
}

h2 {
  text-align: center;
  margin-bottom: 20px;
}

.table-controls {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

input[type="text"] {
  padding: 6px;
  border: 1px solid #ddd;
  border-radius: 4px;
  width: 70%;
}

button, .custom-file-upload {
  padding: 10px 20px;
  background-color: #42b983;
  color: white;
  border: none;
  cursor: pointer;
}

button:hover, .custom-file-upload:hover {
  background-color: #369f6e;
}

button:disabled {
  background-color: #ccc;
  cursor: not-allowed;
}

.table-wrapper {
  overflow-x: auto;
}

table {
  width: 100%;
  border-collapse: collapse;
  margin-bottom: 20px;
}

th, td {
  border: 1px solid #ddd;
  padding: 8px;
  text-align: left;
  cursor: pointer;
}

th {
  background-color: #f2f2f2;
}

.pagination {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.highlighted {
  background-color: rgba(54, 159, 110, 0.3);
}

.gene-set-label {
  display: block;
  margin-bottom: 5px;
  color: grey;
}

.gene-set-select {
  width: 100%;
  padding: 10px;
  box-sizing: border-box;
}

.gene-set-search {
  width: 100%;
  padding: 10px;
  margin-top: 10px;
  box-sizing: border-box;
}
</style>