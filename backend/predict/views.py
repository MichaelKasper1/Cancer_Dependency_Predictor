# Load required libraries for processing data
import pandas as pd
import plotly.graph_objs as go # type: ignore

# load django libraries
from pymongo import MongoClient # type: ignore
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_http_methods
from django.core.cache import cache
import json

# load custom functions for application
from .preprocess import preprocess
from .predict_samples import predict_samples
from .process_elastic_net import process_elastic_net
from .annotate_table import annotate_table
from .annotate_EN_table import annotate_EN_table
from .waterfallPlot import create_waterfall_plot
from .gsea import perform_gsea_django
from .gseaPlot import create_gsea_plot_logic
from .densityPlot import create_density_plot_logic
from .barPlot import create_bar_plot_logic
from .barsubPlot import create_bar_sub_plot_logic
from .networkPlot import create_network_plot_logic
from .networkPlot import create_network_data
from .predict_elastic_net import predict_elastic_net

# Set up logging
import logging
logger = logging.getLogger(__name__)
logging.getLogger('pymongo').setLevel(logging.WARNING)

# function to get csrf token when needed
@ensure_csrf_cookie
def get_csrf_token(request):
    return JsonResponse({'csrfToken': request.META.get('CSRF_COOKIE')})

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

# elastic net model data
medians_CCLE21Q1 = load_mongo_data('medians_CCLE21Q1')
EN_gene_alias = load_mongo_data('gene_aliases')
model_performances_EN = load_mongo_data('model_performances_EN')
ccle_21q1_expression = load_mongo_data('ccle_21q1_expression')
GeneEffect_21q1 = load_mongo_data('GeneEffect_21q1')

# data first used in table 1. The annotation file is above in the preprocessing section. The predicted dependency data are also used throughout the app.
ccl_predicted_data_model_10xCV_paper = load_mongo_data('ccl_predicted_data_model_10xCV_paper')
GeneEffect_18Q2_278CCLs = load_mongo_data('GeneEffect_18Q2_278CCLs')
tcga_pred = load_mongo_data('tcga_pred')

# additional data for figure 5 (and 6 and 7 and 8)
ccle_23q4_chronos_996 = load_mongo_data('ccle_23q4_chronos_996')
tcga_clinicalData = load_mongo_data('tcga_clinicalData')

# additional data for figure 6 and 7
cell_info = load_mongo_data('cell_info_21Q3_PrimaryTypeFixed')

# used for caching user chosen information
global_data = {}

@require_http_methods(["GET"])
def get_column_names(request):
    global C2_cp, hallmark
    column_names = list(C2_cp.columns) + list(hallmark.columns)  # Combine column names
    return JsonResponse({'columnNames': column_names})

@require_http_methods(["GET"])
def get_example_file(request):
    global example_exp_file
    return JsonResponse(example_exp_file.to_dict(orient='list'), safe=False)

@require_http_methods(["POST"])
def reset_backend_data(request):
    if request.method == 'POST':

        # ensure that the variables are empty

        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error'}, status=400)

@require_http_methods(["POST"])
def process_data(request):
    if request.method == 'POST':
        data = request.POST
        file = request.FILES.get('file')
        selected_model = data.get('selectedModel')
        log_transformed = data.get('logTransformed')
        data_source = data.get('dataSource')
        expression_unit = data.get('expressionUnit')
        selected_gene_set = data.get('selectedGeneSet')

        # example file
        global example_exp_file

        # For preprocessing DeepDEP
        global C2_cp
        global hallmark
        global ccle_exp_for_missing_value_6016
        global crispr_gene_fingerprint_cgp
        global fingerprint
        global ccle_exp_with_gene_alias_DeepDep

        # For elastic net
        global medians_CCLE21Q1
        global EN_gene_alias
        global model_performances_EN
        global GeneEffect_21q1
        global ccle_21q1_expression

        # for table 1 annotations
        global ccl_predicted_data_model_10xCV_paper
        global GeneEffect_18Q2_278CCLs
        global tcga_pred
        global gene_annotations

        # save data source and log_transformed to cache
        cache.set('data_source', data_source, timeout=1800)  # 30 minutes
        cache.set('log_transformed', log_transformed, timeout=1800)  # 30 minutes

        if log_transformed is None or data_source is None or selected_gene_set is None:
            logger.error("Missing required parameters")
            return JsonResponse({'error': 'Missing required parameters'}, status=400)

        try:
            # Determine the delimiter for reading user uploaded file
            delimiter = ','  # Default to comma
            first_line = file.readline().decode('utf-8')
            if '\t' in first_line:
                delimiter = '\t'
            file.seek(0)  # Reset file pointer to the beginning

            # Read the uploaded file into a DataFrame
            df = pd.read_csv(file, delimiter=delimiter)
        except Exception as e:
            logger.error("Error reading file: %s", str(e))
            return JsonResponse({'error': str(e)}, status=500)
        
        # ensure the first column is named 'Gene'
        df = df.rename(columns={df.columns[0]: "Gene"})

        if selected_model == 'DeepDEP':
            try:
                # Call the preprocess function
                df, fingerprint_df = preprocess(df, log_transformed, selected_gene_set, expression_unit, ccle_exp_for_missing_value_6016, crispr_gene_fingerprint_cgp, hallmark, C2_cp, fingerprint, ccle_exp_with_gene_alias_DeepDep)

                # Call the predict_samples function
                result_df = predict_samples(df, fingerprint_df)

                # Call the table annotations function. First ensure data is accessible.
                result_df = annotate_table(result_df, gene_annotations, data_source, ccl_predicted_data_model_10xCV_paper, GeneEffect_18Q2_278CCLs, tcga_pred)

                # Convert the result DataFrame to a JSON-serializable format
                result_json = result_df.to_dict(orient='records')

                # Store the result in the cache
                cache.set('result_json', json.dumps(result_json), timeout=1800)  # 30 minutes
                # also store result under slightly different variable name
                cache.set('results_json', json.dumps(result_json), timeout=1800)  # 30 minutes

                # Return the result as JSON
                return JsonResponse({'status': 'success', 'result': result_json})
            except Exception as e:
                logger.error("Error processing data for DeepDEP: %s", str(e))
                return JsonResponse({'error': str(e)}, status=500)
        else:
            try:
                result_df = None
                # call the function for elastic net model prediction
                result_df = process_elastic_net(df, log_transformed, expression_unit, medians_CCLE21Q1, EN_gene_alias)

                # with the result_df, call predict_elastic_net function
                predictions_df = predict_elastic_net(result_df)

                # transpose the predictions_df
                predictions_df = predictions_df.T

                # call annotate_table function for elastic net models
                result_df = annotate_EN_table(predictions_df, gene_annotations, model_performances_EN, ccle_21q1_expression, GeneEffect_21q1)

                # Convert the result DataFrame to a JSON-serializable format
                result_json = result_df.to_dict(orient='records')

                # Store the result in the cache
                cache.set('result_json', json.dumps(result_json), timeout=1800)  # 30 minutes
                # also store result under slightly different variable name
                cache.set('results_json', json.dumps(result_json), timeout=1800)  # 30 minutes


                return JsonResponse({'status': 'success', 'result': result_json})
            except Exception as e:
                logger.error("Error processing data for elastic net: %s", str(e))
                return JsonResponse({'error': str(e)}, status=500)
            
@require_http_methods(["POST"])
def selected_data(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            column = data.get('column')
            gene = data.get('gene')

            # save column and gene to cache
            cache.set('Column', column, None)  # 30 minutes
            cache.set('Gene', gene, None)  # 30 minutes

            # Retrieve the result from the cache
            results_json = cache.get('results_json')
            if results_json is None:
                logger.error("No data found in cache")
                return JsonResponse({'status': 'error', 'message': 'No data found in cache'}, status=400)

            # Convert JSON string back to DataFrame
            result_df = pd.DataFrame(json.loads(results_json))

            # Check if the specified column exists
            if column not in result_df.columns:
                logger.error("Specified column '%s' not found in result DataFrame", column)
                return JsonResponse({'status': 'error', 'message': f"Column '{column}' not found"}, status=400)

            # Filter the DataFrame based on the selected column only
            filtered_df = result_df[['gene', column]]

            # Create the Plotly figure
            plot_json = create_waterfall_plot(filtered_df.to_dict(orient='records'), column)

            return JsonResponse({'status': 'success', 'plot': plot_json})
        except json.JSONDecodeError:
            logger.error("Invalid JSON in request body")
            return JsonResponse({'status': 'error', 'message': 'Invalid JSON'}, status=400)
        except Exception as e:
            logger.error("Error in selected_data: %s", str(e))
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

@require_http_methods(["POST"])
def gsea_data(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            column = data.get('column')
            gene = data.get('gene')

            logger.info("Received POST data: column=%s, gene=%s", column, gene)

            # Retrieve the result from the cache
            results_json = cache.get('results_json')
            if results_json is None:
                logger.error("No data found in cache")
                return JsonResponse({'status': 'error', 'message': 'No data found in cache'}, status=400)

            # Convert JSON string back to DataFrame
            result_df = pd.DataFrame(json.loads(results_json))

            # Check if the specified column exists
            if column not in result_df.columns:
                logger.error("Specified column '%s' not found in result DataFrame", column)
                return JsonResponse({'status': 'error', 'message': f"Column '{column}' not found"}, status=400)

            # Get table data using perform_gsea_django for GSEA, pass the gene and column
            gsea_table_data = perform_gsea_django(request, result_df[['gene', column]])

            # Return the GSEA table data as JSON
            return JsonResponse({'status': 'success', 'gsea_table': gsea_table_data})
        except json.JSONDecodeError:
            logger.error("Invalid JSON in request body")
            return JsonResponse({'status': 'error', 'message': 'Invalid JSON'}, status=400)
        except Exception as e:
            logger.error("Error in gsea_data: %s", str(e))
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
        
# returns plotly for gsea plot
@require_http_methods(["POST"])
def create_gsea_plot(request):
    if request.method == 'POST':
        try:
            body = json.loads(request.body)
            pathway_name = body.get('pathway')

            if pathway_name is None:
                logger.error("Pathway name not provided in request body")
                return JsonResponse({'status': 'error', 'message': 'Pathway name not provided in request body'}, status=400)

            # Retrieve the JSON string for 'column' and convert it back to a pandas DataFrame or Series
            column_json = cache.get('column_gsea', None)
            gene_column = cache.get('gene_column', None)

            # Call the separated logic function
            plot_json = create_gsea_plot_logic(pathway_name, column_json, gene_column)

            return JsonResponse({'status': 'success', 'plot': plot_json})
        except json.JSONDecodeError:
            logger.error("Invalid JSON in request body")
            return JsonResponse({'status': 'error', 'message': 'Invalid JSON'}, status=400)
        except Exception as e:
            logger.error("Error in create_gsea_plot: %s", str(e))
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    else:
        logger.error("Invalid request method: %s", request.method)
        return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)

# code for density plot
def create_density_plot(request):
    try:
        column = cache.get('Column')
        gene = cache.get('Gene')
        results_json = cache.get('results_json')
        data_source = cache.get('data_source')
        result_df = pd.DataFrame(json.loads(results_json))

        global ccl_predicted_data_model_10xCV_paper
        global GeneEffect_18Q2_278CCLs
        global ccle_23q4_chronos_996
        global tcga_pred

        fig = create_density_plot_logic(result_df, gene, column, data_source, ccl_predicted_data_model_10xCV_paper, GeneEffect_18Q2_278CCLs, ccle_23q4_chronos_996, tcga_pred)
        plot_json = fig.to_json()

        # ensure that the plot_json exists
        if plot_json is None:
            logger.error("Error creating density plot")
            return JsonResponse({'status': 'error', 'message': 'Error creating density plot'}, status=500)

        return JsonResponse({'status': 'success', 'plot': plot_json})
    except Exception as e:
        logger.error("Error in create_density_plot: %s", str(e))
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

# code for bar plot
def create_bar_plot(request):
    try:
        column = cache.get('Column')
        gene = cache.get('Gene')
        results_json = cache.get('results_json')
        data_source = cache.get('data_source')
        result_df = pd.DataFrame(json.loads(results_json))

        global ccl_predicted_data_model_10xCV_paper
        global cell_info
        global ccle_23q4_chronos_996
        global GeneEffect_18Q2_278CCLs
        global tcga_pred
        global tcga_clinicalData

        fig = create_bar_plot_logic(result_df, gene, column, data_source, GeneEffect_18Q2_278CCLs, ccl_predicted_data_model_10xCV_paper, cell_info, ccle_23q4_chronos_996, tcga_pred, tcga_clinicalData)
        plot_json = fig.to_json()

        return JsonResponse({'status': 'success', 'plot': plot_json})
    except Exception as e:
        logger.error("Error in create_bar_plot: %s", str(e))
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

# code for cancer subtype plot
def create_bar_sub_plot(request):
    try:
        column = cache.get('Column')
        gene = cache.get('Gene')
        results_json = cache.get('results_json')
        data_source = cache.get('data_source')
        
        # Decode the request body
        request_body = request.body.decode('utf-8')
        pancan_type = json.loads(request_body).get('pancan_type', 'Lung')  # Default to "Lung" if not provided
        
        result_df = pd.DataFrame(json.loads(results_json))

        global subtype_gene
        global subtype_column
        global ccl_predicted_data_model_10xCV_paper
        global cell_info
        global ccle_23q4_chronos_996
        global GeneEffect_18Q2_278CCLs

        if gene is None:
            gene = subtype_gene

        if column is None:
            column = subtype_column

        subtype_gene = gene
        subtype_column = column

        fig = create_bar_sub_plot_logic(result_df, gene, column, data_source, GeneEffect_18Q2_278CCLs, ccl_predicted_data_model_10xCV_paper, cell_info, ccle_23q4_chronos_996, pancan_type)
        # Check if fig is an instance of go.Figure
        if isinstance(fig, go.Figure):
            plot_json = fig.to_json()
            return JsonResponse({'status': 'success', 'plot': plot_json})
        else:
            return JsonResponse({'status': 'message', 'message': fig['message']})
    except Exception as e:
        logger.error("Error in create_bar_sub_plot: %s", str(e))
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

# code for network
def create_network_plot(request):
    try:
        column = cache.get('Column')
        gene = cache.get('Gene')
        data_source = cache.get('data_source')

        global ccle_23q4_chronos_996
        global tcga_pred
        global tcga_clinicalData
        global cell_info

        fig = create_network_plot_logic(gene, column, data_source, ccle_23q4_chronos_996, cell_info, tcga_pred, tcga_clinicalData)

        plot_json = fig.to_json()

        return JsonResponse({'status': 'success', 'plot': plot_json})
    except Exception as e:
        logger.error("Error in create_network_plot: %s", str(e))
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    
# Function to download network data as CSV
def download_network(request):
    try:
        gene = cache.get('Gene')
        data_source = cache.get('data_source')

        global ccle_23q4_chronos_996
        global tcga_pred
        global tcga_clinicalData
        global cell_info

        # Assuming `ccle_23q4_chronos_996` is your DataFrame with data
        network_data = create_network_data(gene, data_source, ccle_23q4_chronos_996, cell_info, tcga_pred, tcga_clinicalData)

        # Create DataFrame from network data
        network_df = pd.DataFrame(network_data)

        # Create the HTTP response with CSV content
        response = HttpResponse(network_df.to_csv(index=False), content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="network_data.csv"'
        return response
    except Exception as e:
        logger.error("Error in download_network: %s", str(e))
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)