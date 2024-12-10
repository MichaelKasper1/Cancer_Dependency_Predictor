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

      <!-- Column 2: Additional Dropdowns -->
      <div class="column">
        <h3>Additional Options</h3>
        <div class="input-group">
          <label for="dropdown1" class="dropdown-label">Dropdown 1</label>
          <select id="dropdown1" v-model="selectedOption1" class="dropdown-select">
            <option value="" disabled selected>Select an Option</option>
            <option v-for="option in filteredOptions1" :key="option" :value="option">
              {{ option }}
            </option>
          </select>
          <input type="text" v-model="searchQuery1" placeholder="Search Options" class="dropdown-search" @input="filterOptions1">
        </div>
        <div class="input-group">
          <label for="dropdown2" class="dropdown-label">Dropdown 2</label>
          <select id="dropdown2" v-model="selectedOption2" class="dropdown-select">
            <option value="" disabled selected>Select an Option</option>
            <option v-for="option in filteredOptions2" :key="option" :value="option">
              {{ option }}
            </option>
          </select>
          <input type="text" v-model="searchQuery2" placeholder="Search Options" class="dropdown-search" @input="filterOptions2">
        </div>
        <div class="input-group">
          <label for="dropdown3" class="dropdown-label">Dropdown 3</label>
          <select id="dropdown3" v-model="selectedOption3" class="dropdown-select">
            <option value="" disabled selected>Select an Option</option>
            <option v-for="option in filteredOptions3" :key="option" :value="option">
              {{ option }}
            </option>
          </select>
          <input type="text" v-model="searchQuery3" placeholder="Search Options" class="dropdown-search" @input="filterOptions3">
        </div>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, computed } from 'vue';

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
      options1: ['Option 1A', 'Option 1B', 'Option 1C'], // Placeholder options
      options2: ['Option 2A', 'Option 2B', 'Option 2C'], // Placeholder options
      options3: ['Option 3A', 'Option 3B', 'Option 3C'], // Placeholder options
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
    filterOptions1() {
      this.filteredOptions1;
    },
    filterOptions2() {
      this.filteredOptions2;
    },
    filterOptions3() {
      this.filteredOptions3;
    }
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