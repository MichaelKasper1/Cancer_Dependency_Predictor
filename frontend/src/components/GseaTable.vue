<template>
  <div v-if="resultsReady" class="table-container">
    <h2>GSEA Results</h2>
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
            <td v-for="header in headers" :key="header">{{ row[header] }}</td>
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

<script>
import { ref, onMounted, onBeforeUnmount, computed } from 'vue';
import EventBus from '../utils/eventBus';

export default {
  name: 'GseaDataTable',
  setup() {
    const tableData = ref([]);
    const headers = ref([]);
    const currentPage = ref(1);
    const rowsPerPage = ref(10);
    const searchQuery = ref('');
    const resultsReady = ref(false);
    const selectedRow = ref(null);
    const sortKey = ref('');
    const sortOrder = ref('asc');

    const getCsrfToken = () => {
      const name = 'csrftoken';
      const cookies = document.cookie.split(';');
      for (let cookie of cookies) {
        cookie = cookie.trim();
        if (cookie.startsWith(name + '=')) {
          return cookie.substring(name.length + 1);
        }
      }
      return '';
    };

    const fetchGseaData = async (column, gene) => {
      try {
        console.log('Fetching GSEA data with:', { column, gene });
        const csrfToken = getCsrfToken();
        const response = await fetch('/api/gsea-data', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken,
          },
          body: JSON.stringify({ column, gene }),
        });
        const data = await response.json();
        if (data.status === 'success') {
          tableData.value = data.gsea_table;
          headers.value = Object.keys(tableData.value[0]);
          resultsReady.value = true;
        } else {
          console.error('Error fetching GSEA data:', data.message);
        }
      } catch (error) {
        console.error('Error fetching GSEA data:', error);
      }
    };

    const handleNewSelection = ({ column, gene }) => {
      console.log('New column or gene selected:', column, gene);
      fetchGseaData(column, gene);
    };

    onMounted(() => {
      EventBus.on('newColumnOrGeneSelected', handleNewSelection);
    });

    onBeforeUnmount(() => {
      EventBus.off('newColumnOrGeneSelected', handleNewSelection);
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

    const sortTable = (key) => {
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
      const exportFileDefaultName = 'gsea_data.csv';

      const linkElement = document.createElement('a');
      linkElement.setAttribute('href', dataUri);
      linkElement.setAttribute('download', exportFileDefaultName);
      linkElement.click();
    };

    const selectRow = (row) => {
      selectedRow.value = row;
      console.log('Selected row:', row);
      EventBus.emit('rowSelected', { row });
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