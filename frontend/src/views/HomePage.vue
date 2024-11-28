<template>
  <div class="home">
    <h1>Gene Dependency Web Server</h1>
    <div class="columns">
      <div class="column">
        <h2>Predict Gene Dependencies</h2>
        <p>Use this tool to predict gene dependencies based on your data.</p>
        <router-link to="/predict-gene-dependencies">
          <button>Go to Predict Gene Dependencies</button>
        </router-link>
      </div>
      <div class="column">
        <h2>TCGA Translational Dependency Map</h2>
        <p>Explore the TCGA Translational Dependency Map to understand gene dependencies in various cancers.</p>
        <router-link to="/tcga">
          <button>Go to TCGA Translational Dependency Map</button>
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
.home {
  text-align: center;
  margin-top: 120px; /* Adjust to ensure content is not hidden behind the fixed nav bar */
}

.columns {
  display: flex;
  justify-content: space-around;
  margin-top: 40px;
}

.column {
  flex: 1;
  margin: 0 20px;
  text-align: center;
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
</style>