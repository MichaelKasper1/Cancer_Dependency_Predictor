<template>
    <div>
      <h2>TCGA Dependency Explorer</h2>
      <TcgaDataUpload/>
      <!-- The TCGA sample group summary table is a child of the TCGA data upload files. -->
      <!--<TcgaTable/>
      <TcgaPlotSelected/>
      <TcgaSurvival/> -->
    </div>
  </template>
  
<script>
import TcgaDataUpload from '../components/TcgaDataUpload.vue';
// import TcgaTable from '../components/TcgaTable.vue';
// import TcgaPlotSelected from '../components/TcgaPlotSelected.vue';
// import TcgaSurvival from '../components/TcgaSurvival.vue';

  export default {
    name: 'TCGA',
    components: {
      TcgaDataUpload,
      // TcgaSummary,
      // TcgaTable,
      // TcgaPlotSelected,
      // TcgaSurvival,
    }
  }
</script>

<style scoped>

</style>