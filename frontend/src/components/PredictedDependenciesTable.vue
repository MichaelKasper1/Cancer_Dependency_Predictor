<template>
  <div v-if="resultsReady" class="table-container">
    <h2>Predicted Gene Dependencies</h2>
    <div class="table-controls">
      <input type="text" v-model="searchQuery" placeholder="Search..." />
      <button @click="saveData" class="download-button">
        <i class="fas fa-arrow-down"></i>
      </button>
    </div>
    <div class="table-wrapper">
      <table>
        <thead>
          <tr>
            <th v-for="header in headers" :key="header.value" @click="sortTable(header.value)">
              {{ header.text }}
              <span v-if="sortKey === header.value">
                <i :class="sortOrder === 'asc' ? 'fas fa-sort-up' : 'fas fa-sort-down'"></i>
              </span>
            </th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="row in paginatedData" :key="row.id">
            <td v-for="header in headers" :key="header.value" 
                :class="{ highlighted: header.value === selectedColumn || row.gene === selectedGene }" 
                @click="selectColumnOrGene(header.value, row.gene)">
              {{ row[header.value] }}
            </td>
          </tr>
        </tbody>
      </table>
    </div>
    <div class="pagination">
      <button @click="prevPage" :disabled="currentPage === 1">Previous</button>
      <span>Page {{ currentPage }} of {{ totalPages }}</span>
      <button @click="nextPage" :disabled="currentPage === totalPages">Next</button>
    </div>
  </div>
</template>

<script lang="ts">
import { ref, onMounted, onBeforeUnmount, computed } from 'vue';
import EventBus from '../utils/eventBus';

interface TableRow {
  [key: string]: any;
  id: number;
  gene: string;
}

interface TableHeader {
  text: string;
  value: string;
}

export default {
  name: 'PredictedDependenciesTable',
  setup() {
    const tableData = ref<TableRow[]>([]);
    const headers = ref<TableHeader[]>([]);
    const currentPage = ref(1);
    const rowsPerPage = ref(10);
    const searchQuery = ref('');
    const resultsReady = ref(false);
    const sortKey = ref('');
    const sortOrder = ref<'asc' | 'desc'>('asc');
    const selectedColumn = ref('');
    const selectedGene = ref('');

    const nonSelectableColumns = [
      "gene",
      "Prediction performance (Corr)",
      "Prediction Percentile TCGA",
      "Prediction DepMap percentile (CERES; n=278)",
      "Predicted DepMap range (CERES; n=278)",
      "Real DepMap percentile (CCLE; n=278)",
      "Real DepMap range (CCLE; n=278)",
      "Prediction range (TCGA; n=8238)",
      "Real DepMap range (Chronos; n=996)",
      "Ensembl gene ID",
      "Entrez gene ID",
      "Synonym",
      "Cancer syndrome",
      "Tissue type",
      "Molecular genetics",
      "Role in cancer",
      "Mutation types",
      "Translocation partner",
      "Other syndrome"
    ];

    const handleDataProcessed = (data: any) => {
      console.log('Data processed event received in PredictedDependenciesTable component.');
      if (data?.result?.length) {
        tableData.value = data.result;

        // Generate headers directly from the data
        headers.value = Object.keys(tableData.value[0]).map(key => ({
          text: key,
          value: key
        }));

        resultsReady.value = true;
        console.log('Results are ready and the table is rendered.');
      }
    };

    onMounted(() => {
      EventBus.on('dataProcessed', handleDataProcessed);
    });

    onBeforeUnmount(() => {
      EventBus.off('dataProcessed', handleDataProcessed);
    });

    const totalPages = computed(() => Math.ceil(filteredData.value.length / rowsPerPage.value));

    const paginatedData = computed(() => {
      const start = (currentPage.value - 1) * rowsPerPage.value;
      const end = start + rowsPerPage.value;
      return sortedData.value.slice(start, end);
    });

    const filteredData = computed(() => {
      return tableData.value.filter(row => {
        return Object.values(row).some(value =>
          String(value).toLowerCase().includes(searchQuery.value.toLowerCase())
        );
      });
    });

    const sortedData = computed(() => {
      return filteredData.value.slice().sort((a, b) => {
        const aValue = a[sortKey.value];
        const bValue = b[sortKey.value];
        if (aValue === bValue) return 0;
        const order = sortOrder.value === 'asc' ? 1 : -1;
        return (aValue > bValue ? 1 : -1) * order;
      });
    });

    const sortTable = (key: string) => {
      if (sortKey.value === key) {
        sortOrder.value = sortOrder.value === 'asc' ? 'desc' : 'asc';
      } else {
        sortKey.value = key;
        sortOrder.value = 'asc';
      }
    };

    const selectColumnOrGene = (key: string, gene: string) => {
      if (!nonSelectableColumns.includes(key)) {
        if (key !== 'gene') {
          selectedColumn.value = key;
        }
        selectedGene.value = gene;

        EventBus.emit('newColumnOrGeneSelected', { column: selectedColumn.value, gene: selectedGene.value });
      }
    };

    const nextPage = () => {
      if (currentPage.value < totalPages.value) {
        currentPage.value++;
      }
    };

    const prevPage = () => {
      if (currentPage.value > 1) {
        currentPage.value--;
      }
    };

    const saveData = () => {
      const csvContent = [
        headers.value.map(header => header.text).join(','),
        ...tableData.value.map(row => headers.value.map(header => row[header.value]).join(','))
      ].join('\n');

      const dataUri = 'data:text/csv;charset=utf-8,' + encodeURIComponent(csvContent);
      const exportFileDefaultName = 'data.csv';

      const linkElement = document.createElement('a');
      linkElement.setAttribute('href', dataUri);
      linkElement.setAttribute('download', exportFileDefaultName);
      linkElement.click();
    };

    return {
      tableData,
      headers,
      currentPage,
      rowsPerPage,
      totalPages,
      paginatedData,
      nextPage,
      prevPage,
      searchQuery,
      filteredData,
      saveData,
      resultsReady,
      sortKey,
      sortOrder,
      sortTable,
      selectedColumn,
      selectedGene,
      selectColumnOrGene,
    };
  }
};
</script>

<style scoped>
.table-container {
  max-width: 1300px;
  margin: 0 auto;
  padding: 20px;
  border: 1px solid #ddd;
  border-radius: 8px;
  background-color: #fff;
  box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
  margin-bottom: 20px;
}

h2 {
  text-align: center;
  margin-bottom: 20px;
}

.table-controls {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

input[type="text"] {
  padding: 6px;
  border: 1px solid #ddd;
  border-radius: 4px;
  width: 70%;
}

button, .custom-file-upload {
  padding: 10px 20px;
  background-color: #42b983;
  color: white;
  border: none;
  cursor: pointer;
}

button:hover, .custom-file-upload:hover {
  background-color: #369f6e;
}

button:disabled {
  background-color: #ccc;
  cursor: not-allowed;
}

.table-wrapper {
  overflow-x: auto;
}

table {
  width: 100%;
  border-collapse: collapse;
  margin-bottom: 20px;
}

th, td {
  border: 1px solid #ddd;
  padding: 8px;
  text-align: left;
  cursor: pointer;
}

th {
  background-color: #f2f2f2;
}

.pagination {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.highlighted {
  background-color: rgba(54, 159, 110, 0.3);
}
</style>