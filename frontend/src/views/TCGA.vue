<template>
    <div>
      <h2>TCGA Dependency Explorer</h2>
      <TcgaDataUpload/>
      <!-- <TcgaSummary/>
      <TcgaPlot/>
      <TcgaPlotSelected/>
      <TcgaSurvival/> -->
    </div>
  </template>
  
<script>
import TcgaDataUpload from '../components/TcgaDataUpload.vue';
// import TcgaSummary from '../components/TcgaSummary.vue';
// import TcgaPlot from '../components/TcgaPlot.vue';
// import TcgaPlotSelected from '../components/TcgaPlotSelected.vue';
// import TcgaSurvival from '../components/TcgaSurvival.vue';

  export default {
    name: 'TCGA',
    components: {
      TcgaDataUpload,
      // TcgaSummary,
      // TcgaPlot,
      // TcgaPlotSelected,
      // TcgaSurvival,
    }
  }
</script>

<style scoped>

</style>