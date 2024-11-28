<template>
  <div class="user-data-input">
    <!-- <h2>User Data Input</h2> -->
    
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
          <p v-if="errorMessage" class="error-message">{{ errorMessage }}</p>
        </div>
        <div class="input-group">
          <button @click="submitExample">Submit Example</button>
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
            <input type="radio" value="tumor" v-model="dataSource"> Tumor
          </label>
          <label>
            <input type="radio" value="cell-line" v-model="dataSource"> Cell Line
          </label>
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

<script>
import EventBus from '../utils/eventBus';

export default {
  data() {
    return {
      file: null,
      uploadedFileName: '',
      selectedGeneSet: 'default-gene-set',
      logTransformed: 'log', // Default to Yes
      dataSource: 'tumor', // Default to tumor
      expressionUnit: 'TPM', // Default to TPM
      selectedModel: 'DeepDEP', // Default to DeepDEP
      columnNames: [],
      errorMessage: '' // Add an error message property
    };
  },
  methods: {
    fetchColumnNames() {
      fetch('/api/column-names/')
        .then(response => {
          if (!response.ok) {
            throw new Error('Network response was not ok');
          }
          return response.json();
        })
        .then(data => {
          console.log('Fetched data:', data); // Log the fetched data
          this.columnNames = data.column_names;
          console.log('Updated columnNames:', this.columnNames); // Log the updated columnNames
        })
        .catch(error => {
          console.error('Error fetching column names:', error);
        });
    },
    handleFileUpload(event) {
      const file = event.target.files[0];
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
    validateFile(file) {
      return new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.onload = (e) => {
          const content = e.target.result;
          const lines = content.split('\n');

          // ensure file has more than 2 rows
          if (lines.length < 2) {
            reject(new Error('File is too short. Must include more than one row.'));
            return;
          }

          // add a check to make sure the data uploaded has atleast 2 columns
          const header = lines[0].split(/\t|,/);
          if (header.length < 2) {
            reject(new Error('File must have at least 2 columns. One for a gene symbol, atleast one for expression values.'));
            return;
          }
          
          // ensure the first column has strings for the data and print warning if not
          const firstRow = lines[1].split(/\t|,/);
          if (isNaN(firstRow[0])) {
            console.warn('First column should contain gene symbols. If not, please ensure the gene symbols are in the first column.');
          }

          // ensure that the second column has numbers for the data other than the first row or they can atleast be coerced to numbers
          const secondRow = lines[1].split(/\t|,/);
          if (isNaN(secondRow[1])) {
            reject(new Error('Second column must contain numeric values for gene expression.'));
            return;
          }

          // add other user input data checks here

          resolve(true);
        };

        reader.onerror = () => {
          reject(new Error('Error reading file.'));
        };

        reader.readAsText(file);
      });
    },
    getCookie(name) {
      let cookieValue = null;
      if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
          const cookie = cookies[i].trim();
          if (cookie.substring(0, name.length + 1) === (name + '=')) {
            cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
            break;
          }
        }
      }
      return cookieValue;
    },
    submitForm() {
      if (!this.file) {
        this.errorMessage = 'No file selected or file is invalid.';
        return;
      }

      const formData = new FormData();
      formData.append('selectedGeneSet', this.selectedGeneSet);
      formData.append('logTransformed', this.logTransformed);
      formData.append('dataSource', this.dataSource);
      formData.append('expressionUnit', this.expressionUnit);
      formData.append('selectedModel', this.selectedModel);
      formData.append('file', this.file);

      const csrftoken = this.getCookie('csrftoken');

      fetch('/api/process-data/', {
        method: 'POST',
        body: formData,
        headers: {
          'X-CSRFToken': csrftoken
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
    submitExample() {
      const formData = new FormData();
      formData.append('selectedGeneSet', this.selectedGeneSet);
      formData.append('logTransformed', this.logTransformed);
      formData.append('dataSource', this.dataSource);
      formData.append('expressionUnit', this.expressionUnit);
      formData.append('selectedModel', this.selectedModel);
      formData.append('example', true);

      const csrftoken = this.getCookie('csrftoken');

      fetch('/api/process-data/', {
        method: 'POST',
        body: formData,
        headers: {
          'X-CSRFToken': csrftoken
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
    }
  },
  created() {
    this.fetchColumnNames();
  }
};
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