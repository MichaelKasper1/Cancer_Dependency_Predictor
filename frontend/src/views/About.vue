<template>
  <div class="about">
    <h1>About Gene Dependency Web Server</h1>
    <p>This web application provides tools for predicting gene dependencies...</p>
    <!-- Add more content about your application here -->
  </div>
</template>

<script lang="ts">
import { defineComponent } from 'vue';

export default defineComponent({
  name: 'About',
});
</script>

<style scoped>
.about {
  text-align: center;
  margin-top: 120px; /* Adjust to ensure content is not hidden behind the fixed nav bar */
}

@media (max-width: 695px) {
  .about {
    margin-top: 140px; /* Adjust margin for smaller screens */
  }
}
</style>