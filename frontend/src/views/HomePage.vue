<template>
  <div>
    <h1>Cancer Dependency Predictor</h1>
    <p class="intro-text">Welcome to the Cancer Dependency Predictor, a user-friendly tool to generate and explore machine learning predictions of cancer gene dependencies.<br><br>
      Source code for the website can be found on <a href="https://github.com/MichaelKasper1/Cancer_Dependency_Predictor" target="_blank">Github</a>.<br>
      This project is free to use and licensed under the <a href="https://opensource.org/licenses/MIT" target="_blank">MIT License</a>.</p>
    <div class="columns">
      <div class="column">
        <h2>Gene dependency prediction and prioritization</h2>
        <p>Predict gene dependencies of cancer samples using gene expression data and modern machine learning models. Explore enriched gene sets and other analysis. Currently models available are from <a href="https://pubmed.ncbi.nlm.nih.gov/34417181/" target="_blank">Chiu YC, et al. Sci Adv. 2021</a> and <a href="https://pubmed.ncbi.nlm.nih.gov/39009815/" target="_blank">Shi X, et al. Nat Cancer. 2024</a>.</p>
        <router-link to="/predict-gene-dependencies">
          <button>Go to gene dependency predictor</button>
        </router-link>
      </div>
      <div class="column">
        <h2>TCGA Dependency Explorer</h2>
        <p>Explore gene dependency predictions across pan-cancer samples from TCGA in relation to gene mutations, aberrant expressions, and overall survival rates. The module identifies significantly intensified gene dependencies in tumors with specific alterations, either across all cancers or within specific cancer types. Additionally, it evaluates the relevance of gene dependencies to patients’ overall survival.</p>
        <router-link to="/tcga">
          <button>Go to TCGA dependency explorer</button>
        </router-link>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'HomePage'
}
</script>

<style scoped>

.intro-text {
  margin-top: 20px;
  font-size: 1.2em;
  color: #333;
}

.columns {
  display: flex;
  justify-content: space-around;
  margin-top: 40px;
  flex-wrap: wrap; /* Allow columns to wrap on smaller screens */
}

.column {
  flex: 1;
  margin: 0 20px;
  text-align: center;
  min-width: 250px; /* Ensure columns don't get too narrow */
}

button {
  padding: 20px 40px;
  background-color: #42b983; /* Vibrant green */
  color: white;
  border: none;
  cursor: pointer;
  font-size: 1.2em;
  margin-top: 20px;
}

button:hover {
  background-color: #369f6e; /* Slightly darker green for hover effect */
}

@media (max-width: 430px) {
  .columns {
    flex-direction: column; /* Stack columns vertically */
    align-items: center; /* Center the columns */
  }

  .column {
    margin: 20px 0; /* Add margin to separate stacked columns */
  }
}

</style>