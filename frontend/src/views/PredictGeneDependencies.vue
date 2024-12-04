<template>
  <div class="predict">
    <h1>Predict Gene Dependencies</h1>
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
.predict {
  text-align: center;
  margin-top: 120px; /* Adjust to ensure content is not hidden behind the fixed nav bar */
}

@media(max-width: 695px) {
  .predict {
    margin-top: 160px; /* Adjust margin for smaller screens */
  }
}
</style>