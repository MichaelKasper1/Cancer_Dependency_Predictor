<template>
  <div>
    <h2>Predict Gene Dependencies</h2>
    <UserDataUpload/>
    <!-- <PredictedDependenciesTable/>
    <WaterfallPlot/>
    <GseaTable/>
    <GseaPlot/>
    <DependencyPlots/> -->
  </div>
</template>

<script>
import UserDataUpload from '../components/UserDataUpload.vue';
// import PredictedDependenciesTable from './components/PredictedDependenciesTable.vue';
// import WaterfallPlot from './components/WaterfallPlot.vue';
// import GseaTable from './components/GseaTable.vue';
// import GseaPlot from './components/GseaPlot.vue';
// import DependencyPlots from './components/DependencyPlots.vue';

export default {
  name: 'PredictGeneDependencies',
  components: {
    UserDataUpload,
    // PredictedDependenciesTable,
    // WaterfallPlot,
    // GseaTable,
    // GseaPlot,
    // DependencyPlots,
  }
}
</script>

<style scoped>

</style>