<template>
  <div v-if="resultsReady" class="table-container">
    <h2>Comparison of Gene Effect Scores Between Groups</h2>
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
            <th v-for="header in headers" :key="header" @click="sortTable(header)">
              {{ header }}
              <span v-if="sortKey === header">
                <i :class="sortOrder === 'asc' ? 'fas fa-sort-up' : 'fas fa-sort-down'"></i>
              </span>
            </th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="row in paginatedData"
            :key="row.id"
            @click="selectRow(row)"
            :class="{ highlighted: row === selectedRow }"
          >
            <td v-for="header in headers" :key="header">
              <span v-if="header === 'entrezgene id'">
                <a :href="`https://www.ncbi.nlm.nih.gov/gene/${row[header]}`" target="_blank" class="entrez-link">{{ row[header] }}</a>
              </span>
              <span v-else>
                {{ row[header] }}
              </span>
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
    <TcgaPlotSelected
      v-if="plotData || survivalData"
      :boxplotData="plotData"
      :survivalData="survivalData"
    />
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, onMounted, computed } from 'vue';
import TcgaPlotSelected from './TcgaPlotSelected.vue';

interface TableRow {
  [key: string]: any;
  id: number;
}

export default defineComponent({
  name: 'TcgaTable',
  components: {
    TcgaPlotSelected
  },
  props: {
    tcgaTableJson: {
      type: String,
      required: true
    }
  },
  emits: ['tableUpdated'],
  setup(props, { emit }) {
    const tableData = ref<TableRow[]>([]);
    const headers = ref<string[]>([]);
    const currentPage = ref(1);
    const rowsPerPage = ref(10);
    const searchQuery = ref('');
    const resultsReady = ref(false);
    const selectedRow = ref<TableRow | null>(null);
    const sortKey = ref('');
    const sortOrder = ref<'asc' | 'desc'>('asc');
    const plotData = ref(null);
    const survivalData = ref(null);

    const parseTableData = () => {
      try {
        tableData.value = JSON.parse(props.tcgaTableJson);
        headers.value = Object.keys(tableData.value[0]);
        resultsReady.value = true;
        emit('tableUpdated');
      } catch (e) {
        console.error('Failed to parse tcgaTable JSON:', e);
      }
    };

    onMounted(() => {
      parseTableData();
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
        headers.value.join(','),
        ...tableData.value.map(row => headers.value.map(header => row[header]).join(','))
      ].join('\n');

      const dataUri = 'data:text/csv;charset=utf-8,' + encodeURIComponent(csvContent);
      const exportFileDefaultName = 'tcga_data.csv';

      const linkElement = document.createElement('a');
      linkElement.setAttribute('href', dataUri);
      linkElement.setAttribute('download', exportFileDefaultName);
      linkElement.click();
    };

    const selectRow = (row: TableRow) => {
      selectedRow.value = row;
      console.log('Selected row:', row);

      // Send the selected row to the backend
      fetch('/api/get-visualization-data', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ selectedGene: row.Gene }),
      })
        .then(response => response.json())
        .then(data => {
          if (data.status === 'success') {
            // console.log('Visualization data:', data);

            // Handle boxplot data
            try {
              const parsedBoxplotData = JSON.parse(data.tcga_boxplot);
              if (parsedBoxplotData && parsedBoxplotData.data && parsedBoxplotData.layout) {
                plotData.value = parsedBoxplotData;
              } else {
                console.error('Invalid tcga_boxplot format:', parsedBoxplotData);
                plotData.value = null;
              }
            } catch (error) {
              console.error('Error parsing tcga_boxplot:', error);
              plotData.value = null;
            }

            // Handle survival plot data
            try {
              const parsedSurvivalData = JSON.parse(data.survival);
              if (parsedSurvivalData && parsedSurvivalData.data && parsedSurvivalData.layout) {
                survivalData.value = parsedSurvivalData;
              } else {
                console.error('Invalid survival format:', parsedSurvivalData);
                survivalData.value = null;
              }
            } catch (error) {
              console.error('Error parsing survival:', error);
              survivalData.value = null;
            }
          } else {
            console.error('Error fetching visualization data:', data.message);
          }
        })
        .catch(error => {
          console.error('Error fetching visualization data:', error);
        });
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
      selectRow,
      selectedRow,
      plotData,
      survivalData
    };
  }
});
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

button.download-button {
  padding: 8px 16px;
  background-color: #42b983;
  color: white;
  border: none;
  cursor: pointer;
  font-size: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 4px;
}

button.download-button i {
  font-size: 20px;
  color: white;
}

button.download-button:hover {
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

button {
  padding: 10px 20px;
  background-color: #42b983;
  color: white;
  border: none;
  cursor: pointer;
}

button:hover {
  background-color: #369f6e;
}

button:disabled {
  background-color: #ccc;
  cursor: not-allowed;
}

.highlighted {
  background-color: rgba(54, 159, 110, 0.3);
}

.entrez-link {
  color: #8a2be2; /* Light purple color */
  text-decoration: none;
}

.entrez-link:hover {
  text-decoration: underline;
}
</style>