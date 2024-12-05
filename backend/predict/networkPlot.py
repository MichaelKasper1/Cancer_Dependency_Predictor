import pandas as pd
import networkx as nx  # type: ignore
import plotly.graph_objs as go

import pandas as pd
import networkx as nx  # type: ignore
import plotly.graph_objs as go

def create_network_plot_logic(gene, column, data_source, depmap_data, cell_info, tcga_predictions=None, tcga_clinicalData=None):
    num_cell_line_neighbors = 10
    num_gene_neighbors = 10
    num_total_rows = depmap_data.shape[0]

    # Merge depmap_data with cell_info to include stripped_cell_line_name
    depmap_data = depmap_data.merge(cell_info[['DepMap_ID', 'stripped_cell_line_name']], left_on='DepMapID', right_on='DepMap_ID', how='left')
    depmap_data.set_index('DepMapID', inplace=True)

    G = nx.Graph()
    
    if data_source == "cell-line":
        if gene not in depmap_data.columns:
            raise KeyError(f"Gene '{gene}' not found in depmap_data columns.")
        
        gene_pred = pd.to_numeric(depmap_data[gene], errors='coerce').dropna()

        # Sort and get the top `num_cell_line_neighbors` closest cell lines to the selected gene
        order_idx = gene_pred.argsort()[:num_cell_line_neighbors]
        top_cell_lines = order_idx[:min(num_cell_line_neighbors, len(order_idx))]

        # Add the selected gene
        G.add_node(gene, size=30, color='blue', shape='diamond')
        
        # Add top cell line neighbors to the graph
        for cell_line_idx in top_cell_lines:
            if cell_line_idx >= num_total_rows:
                continue  # Skip out-of-bounds indices
            
            cell_line = depmap_data.index[cell_line_idx]  # Use index to refer to the cell line name
            cell_line_name = depmap_data.loc[cell_line, 'stripped_cell_line_name']  # Get the stripped cell line name
            
            # Add the cell line as a node
            G.add_node(cell_line_name, size=10, color='peachpuff', shape='dot')
            G.add_edge(gene, cell_line_name, color='black', length=150)
            
            # Get the 10 closest genes for the current cell line
            cell_line_pred = pd.to_numeric(depmap_data.iloc[cell_line_idx, 1:], errors='coerce').dropna()
            gene_order_idx = cell_line_pred.argsort()[:num_gene_neighbors]
            
            for gene_idx in gene_order_idx:
                if gene_idx >= depmap_data.shape[1]:  # Make sure the gene index is within bounds
                    continue
                
                gene_name = depmap_data.columns[gene_idx]  # Get gene name from columns
                
                if gene_name not in G:  # Add the gene node only if it's not already present
                    G.add_node(gene_name, size=10, color='skyblue', shape='diamond')
                G.add_edge(cell_line_name, gene_name, color='gray', length=200)

    elif data_source == "tumor":
        if tcga_predictions is None or tcga_clinicalData is None:
            raise ValueError("tcga_predictions and tcga_clinicalData must be provided for tumor data source.")
        
        try:
            gene_index = tcga_predictions.index[tcga_predictions.iloc[:, 0] == gene].tolist()[0]
        except IndexError:
            raise KeyError(f"Gene '{gene}' not found in tcga_predictions.")
        
        gene_pred = pd.to_numeric(tcga_predictions.iloc[gene_index, 1:], errors='coerce').dropna()
        order_idx = gene_pred.argsort()[:num_cell_line_neighbors]
        top_samples = order_idx[:min(num_cell_line_neighbors, len(order_idx))]

        # Add the selected gene
        G.add_node(gene, size=30, color='blue', shape='diamond')
        
        # Add top tumor sample neighbors to the graph
        for sample_idx in top_samples:
            sample_name = tcga_clinicalData.iloc[sample_idx, 0]  # Get the sample name
            
            # Add the sample as a node
            G.add_node(sample_name, size=10, color='peachpuff', shape='dot')
            G.add_edge(gene, sample_name, color='black', length=150)
            
            # Get the 10 closest genes for the current sample
            sample_pred = pd.to_numeric(tcga_predictions.iloc[:, sample_idx + 1], errors='coerce').dropna()
            gene_order_idx = sample_pred.argsort()[:num_gene_neighbors]
            
            for gene_idx in gene_order_idx:
                if gene_idx >= tcga_predictions.shape[0]:  # Make sure the gene index is within bounds
                    continue
                
                gene_name = tcga_predictions.iloc[gene_idx, 0]  # Get gene name from the first column
                
                if gene_name not in G:  # Add the gene node only if it's not already present
                    G.add_node(gene_name, size=10, color='skyblue', shape='diamond')
                G.add_edge(sample_name, gene_name, color='gray', length=200)

    else:
        raise ValueError(f"Invalid data source: {data_source}.")

    # Use spring layout to position nodes
    pos = nx.spring_layout(G)

    # Edge trace for the graph
    edge_trace = go.Scatter(
        x=[],
        y=[],
        line=dict(width=0.5, color='black'),
        hoverinfo='none',
        mode='lines',
        showlegend=False
    )

    # Add the edges to the edge trace
    for edge in G.edges():
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        edge_trace['x'] += (x0, x1, None)
        edge_trace['y'] += (y0, y1, None)

    # Node traces for the selected gene, genes, and cell lines/tumor samples
    selected_gene_trace = go.Scatter(
        x=[], y=[], text=[], mode='markers+text',
        hoverinfo='text', name='Selected gene',
        marker=dict(symbol='diamond', size=40, color='blue', showscale=False),
    )

    gene_trace = go.Scatter(
        x=[], y=[], text=[], mode='markers+text',
        hoverinfo='text', name='Gene',
        marker=dict(symbol='diamond', size=20, color='skyblue', showscale=False),
    )

    cell_line_trace = go.Scatter(
        x=[], y=[], text=[], mode='markers+text',
        hoverinfo='text', name='Cell line' if data_source == "cell-line" else 'Tumor',
        marker=dict(symbol='circle', size=20, color='peachpuff', showscale=False),
    )

    # Add node positions to the appropriate traces
    for node in G.nodes(data=True):
        x, y = pos[node[0]]
        if node[1]['color'] == 'blue':
            selected_gene_trace['x'] += (x,)
            selected_gene_trace['y'] += (y,)
            selected_gene_trace['text'] += (node[0],)
        elif node[1]['color'] == 'skyblue':
            gene_trace['x'] += (x,)
            gene_trace['y'] += (y,)
            gene_trace['text'] += (node[0],)
        else:
            cell_line_trace['x'] += (x,)
            cell_line_trace['y'] += (y,)
            cell_line_trace['text'] += (node[0],)

    # Create the figure with Plotly
    fig = go.Figure(data=[edge_trace, selected_gene_trace, gene_trace, cell_line_trace],
                    layout=go.Layout(
                        title={
                            'text': f"<b>Network for {gene}</b>",
                            'x': 0.5,
                            'xanchor': 'center'
                        },
                        titlefont_size=16,
                        showlegend=True,
                        hovermode='closest',
                        legend=dict(x=1, y=0.5),
                        margin=dict(b=0, l=0, r=0, t=40),
                        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                        plot_bgcolor='white'
                    ))

    return fig
    
def create_network_data(gene, data_source, depmap_data, cell_info, tcga_predictions=None, tcga_clinicalData=None):
    num_cell_line_neighbors = 10  # Number of cell lines to connect to the selected gene
    num_gene_neighbors = 10  # Number of genes to connect to each cell line/tumor sample
    network_data = []

    # Merge depmap_data with cell_info to include stripped_cell_line_name
    depmap_data = depmap_data.merge(cell_info[['DepMap_ID', 'stripped_cell_line_name']], left_on='DepMapID', right_on='DepMap_ID', how='left')
    depmap_data.set_index('DepMapID', inplace=True)

    if data_source == "cell-line":
        if gene not in depmap_data.columns:
            raise KeyError(f"Gene '{gene}' not found in depmap_data columns.")
        
        gene_pred = pd.to_numeric(depmap_data[gene], errors='coerce')  # Ensure numeric
        order_idx = gene_pred.argsort()[:num_cell_line_neighbors]
        top_cell_lines = order_idx[:min(num_cell_line_neighbors, len(order_idx))]

        for cell_line_idx in top_cell_lines:
            cell_line = depmap_data.index[cell_line_idx]
            cell_line_name = depmap_data.loc[cell_line, 'DepMapID']

            # Collect network data
            network_data.append({'source': gene, 'target': cell_line_name, 'type': 'cell_line'})

            # Get the 10 closest genes for the current cell line
            cell_line_pred = pd.to_numeric(depmap_data.iloc[cell_line_idx, 1:], errors='coerce').dropna()
            gene_order_idx = cell_line_pred.argsort()[:num_gene_neighbors]

            for gene_idx in gene_order_idx:
                if gene_idx < depmap_data.shape[1]:
                    gene_name = depmap_data.columns[gene_idx]
                    network_data.append({'source': cell_line_name, 'target': gene_name, 'type': 'gene'})

    elif data_source == "tumor":
        if tcga_predictions is None or tcga_clinicalData is None:
            raise ValueError("tcga_predictions and tcga_clinicalData must be provided for tumor data source.")
        
        try:
            gene_index = tcga_predictions.index[tcga_predictions.iloc[:, 0] == gene].tolist()[0]
        except IndexError:
            raise KeyError(f"Gene '{gene}' not found in tcga_predictions.")
        
        gene_pred = pd.to_numeric(tcga_predictions.iloc[gene_index, 1:], errors='coerce')  # Ensure numeric
        order_idx = gene_pred.argsort()[:num_cell_line_neighbors]
        top_samples = order_idx[:min(num_cell_line_neighbors, len(order_idx))]

        for sample_idx in top_samples:
            sample_name = tcga_clinicalData.iloc[sample_idx, 0]  # Get the sample name

            # Collect network data
            network_data.append({'source': gene, 'target': sample_name, 'type': 'tumor'})

            # Get the 10 closest genes for the current sample
            sample_pred = pd.to_numeric(tcga_predictions.iloc[:, sample_idx + 1], errors='coerce').dropna()
            gene_order_idx = sample_pred.argsort()[:num_gene_neighbors]

            for gene_idx in gene_order_idx:
                if gene_idx < tcga_predictions.shape[0]:
                    gene_name = tcga_predictions.iloc[gene_idx, 0]
                    network_data.append({'source': sample_name, 'target': gene_name, 'type': 'gene'})

    else:
        raise ValueError(f"Invalid data source: {data_source}.")

    return network_data