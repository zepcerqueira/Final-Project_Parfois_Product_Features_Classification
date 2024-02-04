from dash import Dash, html, dcc, callback, Output, Input
from dash.exceptions import PreventUpdate
from dash import callback_context
import dash_bootstrap_components as dbc
import subprocess

app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

buttons_info = [
    {"label": "Production Stage Check", "color": "secondary", "script_path": "studio_folder_checker.py"},
    {"label": "Web Site Download", "color": "secondary", "script_path": "web_img_collector.py"},
    {"label": "Downloaded Images Check", "color": "secondary", "script_path": "downloaded_images_check.py"}
]

buttons = html.Div([
    dbc.Button(button["label"], color=button["color"], id=f'button-{i}', className="m-5")
    for i, button in enumerate(buttons_info)
], className="m-5")

output_area = dcc.Textarea(id='output-area', value='', style={'width': '100%', 'height': 300}, readOnly=True)


app.layout = html.Div(style={'backgroundColor': 'gray'}, children=[
    html.H1(children='PARFOIS - Human Detection App', style={'textAlign': 'center'}),

    html.P(
        "How to use:",
        style={"font-weight": "bold", "color": "blue", "backgroundColor": "lightgray", "textAlign": "center", "fontSize": 20}
    ),

    html.P(
        "Production Stage Check:",
        style={"font-weight": "bold", "color": "blue", "fontSize": 16}
    ),
    html.P(
        "Allow the user to search for a specific folder and run the model detection machine "
        "based on the previous uploaded XLS reference call file. It then updates that file based "
        "on model feature detection for every reference.",
        style={"color": "blue", "fontSize": 14}
    ),

    html.P(
        "Web site Check:",
        style={"font-weight": "bold", "color": "blue", "fontSize": 16}
    ),
    html.P(
        "It checks the web site for every reference in the XLS reference call file and updates that "
        "file based on the presence of a model in every picture linked to that reference/product.",
        style={"color": "blue", "fontSize": 14}
    ),

    html.P(
        "Machine Training:",
        style={"font-weight": "bold", "color": "blue", "fontSize": 16}
    ),
    html.P(
        'It returns the results of the selected buttons. In the case of "Production Stage Check" or '
        '"Web Site Check," it returns the updated XLS file, showing yes or no for the presence of a '
        'model. If the user selects "Machine Training", it returns the values for the training performance.',
        style={"color": "blue", "fontSize": 14}
    ),

    html.Div(buttons),

    output_area
])

def run_script(script_path):
    try:
        result = subprocess.run(['python', script_path], check=True, text=True, capture_output=True)
        output_value = f"Script executed successfully!\n\n{result.stdout}\n{result.stderr}"
        return output_value
    except subprocess.CalledProcessError as e:
        output_value = f"Error in script:\n{e.output}"
        return output_value

@app.callback(
    [Output('output-area', 'value')],
    [Input(f'button-{i}', 'n_clicks') for i in range(len(buttons_info))]
)
def handle_button_click(*args):
    ctx = callback_context
    if not ctx.triggered_id:
        raise PreventUpdate

    button_index = int(ctx.triggered_id.split('-')[-1])
    script_path = buttons_info[button_index]["script_path"]

    output_value = run_script(script_path)
    return [output_value]

if __name__ == "__main__":
    app.run(debug=True)