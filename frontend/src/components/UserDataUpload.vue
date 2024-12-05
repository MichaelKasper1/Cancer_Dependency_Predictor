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
          <a href="#" class="button-link" @click.prevent="openModal">Data format requirements</a>
        </div>
        <div class="input-group">
          <button class="button" @click="triggerFileUpload">Upload Data</button>
          <input id="file-upload" type="file" accept=".txt, .csv" @change="handleFileUpload" style="display: none;">
          <p v-if="uploadedFileName">
            <br>{{ uploadedFileName }}
            <button class="delete-button" @click="deleteFile">x</button>
          </p>
          <p v-if="fileError" class="error-message">{{ fileError }}</p>
        </div>
        <div class="input-group">
          <button class="button" @click="useExample">Use Example Data</button>
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

export default defineComponent({
  data() {
    return {
      selectedModel: 'DeepDEP',
      logTransformed: 'log',
      dataSource: 'tumor',
      expressionUnit: 'TPM',
      selectedGeneSet: 'default-gene-set',
      columnNames: [], // This will be populated from the backend
      file: null as File | null,
      fileError: '',
      uploadedFileName: '',
      errorMessage: '',
      showModal: false, // State to control the modal visibility
    };
  },
  methods: {
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

      fetch('/api/preprocess', {
        method: 'POST',
        body: formData,
      })
        .then(response => {
          if (!response.ok) {
            throw new Error('Network response was not ok');
          }
          return response.json();
        })
        .then(data => {
          console.log('Preprocess successful:', data);
        })
        .catch(error => {
          this.errorMessage = 'Failed to preprocess data.';
          console.error('There was a problem with the fetch operation:', error);
        });
    },
    useExample() {
      // Populate the upload data with example data
      this.uploadedFileName = 'example_data.txt';
      this.fileError = '';
    },
    triggerFileUpload() {
      document.getElementById('file-upload').click();
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
        })
        .catch(error => {
          this.errorMessage = 'Failed to load column names.';
        });
    },
    fetchExampleFile() {
      fetch('/api/get-example-file')
        .then(response => {
          if (!response.ok) {
            throw new Error('Network response was not ok');
          }
          return response.json();
        })
        .then(data => {
          const exampleContent = `GeneSymbol,ExpressionValue\n${data.GeneSymbol.join('\n')}\n${data.ExpressionValue.join('\n')}`;
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
    },
    handleFileUpload(event: Event) {
      const input = event.target as HTMLInputElement;
      const file = input.files ? input.files[0] : null;
      if (file) {
        this.validateFile(file)
          .then(isValid => {
            if (isValid) {
              this.file = file; // Store the file in the data property
              this.uploadedFileName = file.name; // Update the uploaded file name
              this.errorMessage = ''; // Clear any previous error messages
              console.log('File uploaded:', file);
            } else {
              this.file = null;
              this.uploadedFileName = '';
            }
          })
          .catch(error => {
            this.errorMessage = error.message;
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
    this.fetchColumnNames();  // Call the fetch method on mount
    this.fetchExampleFile();  // Fetch the example file on mount
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
</style>