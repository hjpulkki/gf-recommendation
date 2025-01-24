import dash
from dash import html, dcc, Input, Output, State
import math
import gf_selection  # Assuming this is your custom module

# Initialize the app
app = dash.Dash(__name__)
app.title = "Dive Gradient Factor Calculator"

# Styles
markdown_style = {"whiteSpace": "pre-line", "padding": "20px"}
input_style = {"marginRight": "10px", "marginBottom": "10px"}

# Define the app layout
app.layout = html.Div([
    # Initial Inputs
    dcc.Markdown("""
    # Dive Gradient Factor Calculator
    Enter the initial parameters for your dive below to begin the calculation.
    """, style=markdown_style),

    html.Div([
        html.Label("Depth in meters (D):"),
        dcc.Input(id="depth", type="number", value=30, style=input_style),

        html.Label("Bottom time in minutes (T):"),
        dcc.Input(id="time", type="number", value=50, style=input_style),

        html.Label("Oxygen percentage (O₂%):"),
        dcc.Input(id="o2_percentage", type="number", value=34, style=input_style),

        html.Button("Calculate", id="initial-calculate-button", n_clicks=0, style={"marginBottom": "20px"}),
    ], id="initial-inputs", style={"marginBottom": "20px"}),

    html.Hr(),

    html.Div(id="initial-results"),

    html.Hr(),

    html.Div([
        html.Label("Accepted rate of decompression sickness (pdcs):"),
        dcc.Input(id="pdcs", type="number", value=0.02, step=0.01, style=input_style),
        html.Button("Next", id="pdcs-next-button", n_clicks=0),
    ], id="pdcs-question", style={"display": "none"}),
    html.Div(id="pdcs-results"),

    html.Hr(),
    html.Div([
        html.Label("Helium percentage (He%):"),
        dcc.Input(id="he_percentage", type="number", value=0, style=input_style),
        html.Button("Next", id="he-next-button", n_clicks=0),
    ], id="he-question", style={"display": "none"}),
    html.Div(id="he-results"),

    html.Div([
        html.Label("Surface time in hours:"),
        dcc.Input(id="surface_time", type="number", value=10, style=input_style),
        html.Button("Next", id="surface-next-button", n_clicks=0),
    ], id="surface-time-question", style={"display": "none"}),
    html.Div(id="surface-time-results"),

    html.Div([
        html.Label("Personal adjustment:"),
        dcc.Input(id="personal_adjustment", type="number", value=0, style=input_style),
        html.Button("Calculate Results", id="final-calculate-button", n_clicks=0),
    ], id="personal-adjustment-question", style={"display": "none"}),
    html.Div(id="personal-adjustment-results"),

    html.Hr(),

    # Final results
    html.Div(id="final-results")
])


# Callback for initial calculation
@app.callback(
    Output("initial-results", "children"),
    Output("pdcs-question", "style"),
    Input("initial-calculate-button", "n_clicks"),
    State("depth", "value"),
    State("time", "value"),
    State("o2_percentage", "value")
)
def calculate_initial_results(n_clicks, D, T, o2_percentage):
    if n_clicks == 0:
        return "", {"display": "none"}

    # Perform initial calculations
    prt = (D / 10 + 1) * math.sqrt(T)
    P_inert_gas = (D / 10 + 1) * (1 - o2_percentage / 100)
    EAD = (P_inert_gas / 0.79 - 1) * 10

    initial_results = f"""
    ## Initial Results
    - Pressure Root Time (PRT): {prt:.1f}
    - Equivalent Air Depth (EAD): {EAD:.1f} meters
    """

    return dcc.Markdown(initial_results, style=markdown_style), {"display": "block"}


# Callback for PDCS question and results
@app.callback(
    Output("pdcs-results", "children"),
    Output("he-question", "style"),
    Input("pdcs-next-button", "n_clicks"),
    State("pdcs", "value")
)
def calculate_pdcs_results(n_clicks, pdcs):
    if n_clicks == 0:
        return "", {"display": "none"}

    pdcs_results = f"""
    - Accepted Rate of Decompression Sickness (pdcs): {pdcs}
    """

    return dcc.Markdown(pdcs_results, style=markdown_style), {"display": "block"}


# Callback for helium percentage question and results
@app.callback(
    Output("he-results", "children"),
    Output("surface-time-question", "style"),
    Input("he-next-button", "n_clicks"),
    State("he_percentage", "value")
)
def calculate_he_results(n_clicks, he_percentage):
    if n_clicks == 0:
        return "", {"display": "none"}

    he_results = f"""
    ## Helium Results
    - Helium Percentage (He%): {he_percentage}%
    """

    return dcc.Markdown(he_results, style=markdown_style), {"display": "block"}


# Callback for surface time question and results
@app.callback(
    Output("surface-time-results", "children"),
    Output("personal-adjustment-question", "style"),
    Input("surface-next-button", "n_clicks"),
    State("surface_time", "value")
)
def calculate_surface_time_results(n_clicks, surface_time):
    if n_clicks == 0:
        return "", {"display": "none"}

    surface_time_results = f"""
    ## Surface Time Results
    - Surface Time: {surface_time} hours
    """

    return dcc.Markdown(surface_time_results, style=markdown_style), {"display": "block"}


# Callback for personal adjustment and final results
@app.callback(
    Output("personal-adjustment-results", "children"),
    Output("final-results", "children"),
    Input("final-calculate-button", "n_clicks"),
    State("depth", "value"),
    State("time", "value"),
    State("o2_percentage", "value"),
    State("pdcs", "value"),
    State("he_percentage", "value"),
    State("surface_time", "value"),
    State("personal_adjustment", "value")
)
def calculate_personal_adjustment_and_final_results(n_clicks, D, T, o2_percentage, pdcs, he_percentage, surface_time, personal_adjustment):
    if n_clicks == 0:
        return "", ""

    # Perform additional calculations
    P_inert_gas = (D / 10 + 1) * (1 - o2_percentage / 100)
    EAD = (P_inert_gas / 0.79 - 1) * 10
    TDT = gf_selection.get_standair_tdt(EAD, T, pdcs)
    tdt_text = gf_selection.standair_plot(EAD, T, pdcs)
    gf_high = gf_selection.fit_gf_to_tdt(T, EAD, TDT, he=he_percentage)
    gf_high -= max(37 - surface_time * 60 / 5, 0)
    gf_high += personal_adjustment

    personal_adjustment_results = f"""
    ## Personal Adjustment Results
    - Personal Adjustment: {personal_adjustment}
    """

    final_results = f"""
    ## Final Results
    - Total Decompression Time (TDT): {TDT}
    - Adjusted GF High: {gf_high:.1f}

    **TDT Analysis:**
    {tdt_text}
    """

    return dcc.Markdown(personal_adjustment_results, style=markdown_style), dcc.Markdown(final_results, style=markdown_style)


# Run the app
if __name__ == "__main__":
    app.run_server(debug=True)
