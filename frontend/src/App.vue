<template>
  <div id="app">
    <nav>
      <div class="nav-left">
        <router-link to="/" class="app-title">Cancer Dependency Predictor</router-link>
      </div>
      <div class="nav-right">
        <router-link to="/">Home</router-link>
        <router-link to="/predict-gene-dependencies">Gene Dependency Predictor</router-link>
        <router-link to="/tcga">TCGA Dependency Explorer</router-link>
        <router-link to="/about">About</router-link>
      </div>
    </nav>
    <router-view/>
    <footer>
      <div class="footer-content">
        <img src="/cancercenterlogo.png" alt="Cancer Center Logo" class="footer-logo">
        <p>
          <a href="/" class="footer-link">Gene Dependency Web Server</a> - Kasper et al. Manuscript in review.
          <br>
          Version: Dec. 2024
        </p>
        <img src="/pitt_logo.png" alt="Pitt Logo" class="footer-logo">
      </div>
    </footer>
  </div>
</template>

<script>
export default {
  name: 'App'
}
</script>

<style>
/* Ensure no unwanted white space */
html, body {
  margin: 0;
  padding: 0;
  width: 100%;
  height: 100%;
  box-sizing: border-box;
}

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

.footer-content {
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 10px;
  background-color: #f8f8f8;
  text-align: center;
  height: 60px; /* Set a fixed height for the footer */
  position: fixed;
  bottom: 0;
  width: 100%;
  box-shadow: 0 -2px 5px rgba(0, 0, 0, 0.1); /* Add a subtle shadow for better separation */
}

.footer-logo {
  height: 40px; /* Set a fixed height for the logos */
  margin: 0 20px; /* Increase margin to add more space between the logos and the text */
}

.footer-link {
  color: #42b983;
  text-decoration: none;
}

.footer-link:hover {
  text-decoration: underline;
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