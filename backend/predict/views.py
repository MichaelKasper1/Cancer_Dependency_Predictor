# Load required libraries for processing data
import pandas as pd
import plotly.graph_objs as go # type: ignore

# load django libraries
from pymongo import MongoClient # type: ignore
from django.http import JsonResponse
# from rest_framework.decorators import api_view # type: ignore
from django.views.decorators.http import require_http_methods

# load custom functions for application
# from .preprocess import preprocess
# from .predict_samples import predict_samples
# from .annotate_table import annotate_table
# from .waterfallPlot import create_waterfall_plot
# from .gsea import perform_gsea_django
# from .gseaPlot import create_gsea_plot_logic
# from .densityPlot import create_density_plot_logic
# from .barPlot import create_bar_plot_logic
# from .barsubPlot import create_bar_sub_plot_logic
# from .networkPlot import create_network_plot_logic
# from .networkPlot import create_network_data

# Set up logging
import logging
logger = logging.getLogger(__name__)
logging.getLogger('pymongo').setLevel(logging.WARNING)

# function to load data from MongoDB
client = MongoClient('mongodb://localhost:27017/', username='michael_kasper', password='password', authSource='admin', authMechanism='SCRAM-SHA-1')
db = client['mongodb']

def load_mongo_data(collection_name):
    collection = db[collection_name]
    data_records = collection.find({}, {'_id': 0, 'source_file': 0})
    return pd.DataFrame(list(data_records))

# example data for example submit button
example_exp_file = load_mongo_data('exp_file')

# data for preprocessing
ccle_exp_for_missing_value_6016 = load_mongo_data('ccle_exp_for_missing_value_6016')
crispr_gene_fingerprint_cgp = load_mongo_data('crispr_gene_fingerprint_cgp')
fingerprint = load_mongo_data('fingerprint')
gene_annotations = load_mongo_data('gene_annotations')
C2_cp = load_mongo_data('C2_cp')
hallmark = load_mongo_data('hallmark')
ccle_exp_with_gene_alias_DeepDep = load_mongo_data('ccle_exp_with_gene_alias_DeepDep')

# data first used in table 1. The annotation file is above in the preprocessing section. The predicted dependency data are also used throughout the app.
ccl_predicted_data_model_10xCV_paper = load_mongo_data('ccl_predicted_data_model_10xCV_paper')
GeneEffect_18Q2_278CCLs = load_mongo_data('GeneEffect_18Q2_278CCLs')
tcga_pred = load_mongo_data('tcga_pred')

# additional data for figure 5 (and 6 and 7 and 8)
ccle_23q4_chronos_996 = load_mongo_data('ccle_23q4_chronos_996')
tcga_clinicalData = load_mongo_data('tcga_clinicalData')

# additional data for figure 6 and 7
cell_info = load_mongo_data('cell_info_21Q3_PrimaryTypeFixed')

print('Logs will appear here.')
print()
print()
print('Data loaded from MongoDB.')
print()
print()

@require_http_methods(["GET"])
def get_column_names(request):
    print('get_column_names function called')
    global C2_cp, hallmark
    column_names = list(C2_cp.columns) + list(hallmark.columns)  # Combine column names
    logger.info(f'Column names: {column_names}')
    return JsonResponse({'columnNames': column_names})

@require_http_methods(["POST"])
def reset_backend_data(request):
    if request.method == 'POST':
        print('reset_backend_data function called')

        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error'}, status=400)