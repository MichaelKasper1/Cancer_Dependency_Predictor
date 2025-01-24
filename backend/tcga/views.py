# data manipulation libaries
import pandas as pd
import plotly.graph_objs as go # type: ignore

# django libraries
from django.shortcuts import render
from pymongo import MongoClient # type: ignore
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

# load custom functions
from .sumTable import sumTable
from .chronosTable import chronosTable
from .geneEffect import geneEffect
from .survival import survival

# load the tcga data into the view from the mongoDB
def load_mongo_data(collection_name):
    collection = db[collection_name]
    data_records = collection.find({}, {'_id': 0, 'source_file': 0})
    return pd.DataFrame(list(data_records))

client = MongoClient('mongodb://localhost:27017/', username='michael_kasper', password='password', authSource='admin', authMechanism='SCRAM-SHA-1')
db = client['mongodb']

Cancer_types_tab3 = load_mongo_data('Cancer_types_tab3')
select_gene_tab3 = load_mongo_data('select_gene_tab3')
survival_data = load_mongo_data('survival_data')
tcga_clinicalData = load_mongo_data('tcga_clinicalData')
tcga_clinicalData_80 = load_mongo_data('tcga_clinicalData_80')
tcga_exp = load_mongo_data('tcga_exp')
tcga_mut = load_mongo_data('tcga_mut')
tcga_exp_sampleID = load_mongo_data('tcga_exp_sampleID')
tcga_mut_sampleID = load_mongo_data('tcga_mut_sampleID')

@require_http_methods(["GET"])
def get_column_names_tcga(request):
    global Cancer_types_tab3, select_gene_tab3

    # Convert the data to dictionaries
    cancer_types_data = Cancer_types_tab3.to_dict(orient='records')
    select_gene_data = select_gene_tab3.to_dict(orient='records')

    # Print the data to the console for debugging
    print("Cancer_types_tab3 head:\n", Cancer_types_tab3.head())
    print("select_gene_tab3 head:\n", select_gene_tab3.head())

    # Return the data as a JSON response
    return JsonResponse({
        'Cancer_types_tab3': cancer_types_data,
        'select_gene_tab3': select_gene_data,
    })

@csrf_exempt
@require_http_methods(["POST"])
def submit_data(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        selected_model = data.get('selectedModel')
        selected_option1 = data.get('selectedOption1')
        selected_option2 = data.get('selectedOption2')
        selected_option3 = data.get('selectedOption3')

        

        # Print the received data for debugging
        print("Received data:", data)

        # Process the data as needed
        # ...

        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=400)