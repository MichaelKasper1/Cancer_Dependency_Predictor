<template>
  <div id="app">
    <nav>
      <div class="nav-left">
        <router-link to="/" class="app-title">Gene Dependency Web Server</router-link>
      </div>
      <div class="nav-right">
        <router-link to="/">Home</router-link>
        <router-link to="/predict-gene-dependencies">Predict Gene Dependencies</router-link>
        <router-link to="/tcga">TCGA Translational Dependency Tool</router-link>
      </div>
    </nav>
    <router-view/>
    <footer>
      <p>Footer content here</p>
    </footer>
  </div>
</template>

<script>
export default {
  name: 'App'
}
</script>

<style>
nav {
  background-color: #42b983;
  padding: 10px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  position: fixed;
  top: 0;
  width: 100%;
  z-index: 1000; /* Ensure the nav bar is above other content */
  box-sizing: border-box; /* Include padding in the element's total width and height */
}

.nav-left {
  display: flex;
  align-items: center;
}

.app-title {
  font-size: 1.5em;
  color: white;
  margin-right: 20px;
  text-decoration: none;
}

.nav-right {
  display: flex;
  align-items: center;
  padding-right: 20px; /* Add padding to the right side */
}

nav a {
  color: white;
  text-decoration: none;
  padding: 10px;
}

nav a:hover {
  background-color: #369f6e;
}

footer {
  background-color: white;
  padding: 10px;
  text-align: center;
  position: fixed;
  width: 100%;
  bottom: 0;
}

#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
  margin-top: 60px; /* Add margin to avoid content being hidden behind the fixed nav bar */
}
</style>