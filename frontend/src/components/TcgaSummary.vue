<template>
  <div class="tcga-summary">
    <h3>Sample Group</h3>
    <table v-if="distTable && distTable.length">
      <thead>
        <tr>
          <th>Group</th>
          <th>Count</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="(row, index) in distTable" :key="index">
          <td>{{ row.groupNames }}</td>
          <td>{{ row.n }}</td>
        </tr>
      </tbody>
    </table>
    <pre v-else>{{ sampleGroup }}</pre>
  </div>
</template>

<script lang="ts">
import { defineComponent, PropType } from 'vue';

export default defineComponent({
  name: 'TcgaSummary',
  props: {
    sampleGroup: {
      type: String,
      required: true
    }
  },
  computed: {
    distTable() {
      try {
        return JSON.parse(this.sampleGroup);
      } catch (e) {
        console.error('Failed to parse sampleGroup JSON:', e);
        return null;
      }
    }
  }
});
</script>

<style scoped>
.tcga-summary {
  margin: 20px;
}

pre {
  background-color: #f2f2f2;
  padding: 10px;
  border: 1px solid #ddd;
  overflow-x: auto;
}

table {
  width: 100%;
  border-collapse: collapse;
}

th, td {
  border: 1px solid #ddd;
  padding: 8px;
}

th {
  background-color: #f2f2f2;
}
</style>