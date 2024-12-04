<template>
  <div class="home">
    <h1>Gene Dependency Web Server</h1>
    <p class="intro-text">Welcome to the Gene Dependency Web Server. Use the tools below to explore gene dependencies and understand their implications in various cancers.</p>
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

@media(max-width: 695px) {
  .home {
    margin-top: 160px; /* Adjust margin for smaller screens */
  }
}
</style>