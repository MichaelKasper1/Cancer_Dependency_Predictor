import plotly.graph_objects as go
import pandas as pd
import json
import plotly

def create_waterfall_plot(data, column):
    df = pd.DataFrame(data)
    fig = go.Figure(go.Waterfall(
        x=df['gene'],
        y=df[column],
        measure=['absolute'] * len(df)  # Set measure to 'absolute' for each entry
    ))
    fig.update_layout(
        title={
            'text': '<b>Waterfall Plot of Predicted Gene Dependency Scores</b>',
            'x': 0.5,  # Center the title
            'xanchor': 'center'
        },
        xaxis=dict(
            title=dict(
                text='Gene',
                standoff=10  # Set standoff distance for x-axis title
            ),
            automargin=True  # Ensure the x-axis title is centered
        ),
        yaxis=dict(
            title=dict(
                text=column,
                standoff=10  # Set standoff distance for y-axis title
            ),
            range=[df[column].min(), df[column].max()],  # Ensure the y-axis accommodates negative values
            showgrid=False,  # Remove grid lines from y-axis
            automargin=True  # Ensure the y-axis title is centered
        ),
        plot_bgcolor='white',  # Set plot background color to white
        paper_bgcolor='white'  # Set paper background color to white
    )
    return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)