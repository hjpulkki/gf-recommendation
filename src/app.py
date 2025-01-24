import dash
from dash import html, dcc, Input, Output, State
import math
import gf_selection  # Assuming this is your custom module

# Initialize the app
app = dash.Dash(
    __name__,
    external_stylesheets=[
        "https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha3/dist/css/bootstrap.min.css"
    ],
)
app.title = "Dive Gradient Factor Calculator"

# Layout
app.layout = html.Div(
    [
        dcc.Markdown(
            """
            # Dive Gradient Factor Calculator
            This app provides a tool for calculating Gradient Factor (GF) recommendations for your planned dive. It accounts for various parameters affecting decompression and risk. Arrows ↓ and ↑ are used to indicate whether a factor decreases (↓) or increases (↑) certain risks or considerations.
            """,
            className="card",
        ),
        html.Div(
            [
                html.Label("Depth in meters (D):"),
                dcc.Input(id="depth", type="number", value=30),
                html.Label("Bottom time in minutes (T):"),
                dcc.Input(id="time", type="number", value=50),
                html.Label("Oxygen percentage (O₂%):"),
                dcc.Input(id="o2_percentage", type="number", value=34),
                html.Button("Next", id="initial-calculate-button", n_clicks=0),
            ],
            className="card",
        ),
        html.Div(id="initial-results", className="card"),
        html.Div(
            [
                html.Label("Accepted rate of decompression sickness (pdcs):"),
                dcc.Input(id="pdcs", type="number", value=0.02, step=0.01),
                html.Div(html.Button("Next", id="pdcs-next-button", n_clicks=0)),
            ],
            id="pdcs-question",
            className="card",
            style={"display": "none"},
        ),
        html.Div(id="pdcs-results", className="card"),
        html.Div(
            [
                html.Label("Helium percentage (He%):"),
                dcc.Input(id="he_percentage", type="number", value=0),
                html.Button("Next", id="he-next-button", n_clicks=0),
            ],
            id="he-question",
            className="card",
            style={"display": "none"},
        ),
        html.Div(id="he-results", className="card"),
        html.Div(
            [
                html.Label("Surface time in hours:"),
                dcc.Input(id="surface_time", type="number", value=10),
                html.Button("Next", id="surface-next-button", n_clicks=0),
            ],
            id="surface-time-question",
            className="card",
            style={"display": "none"},
        ),
        html.Div(id="surface-time-results", className="card"),
        html.Div(
            [
                html.Label("Personal adjustment:"),
                dcc.Input(id="personal_adjustment", type="number", value=0),
                html.Button("Next", id="final-calculate-button", n_clicks=0),
            ],
            id="personal-adjustment-question",
            className="card",
            style={"display": "none"},
        ),

        
        html.Div(id="personal-adjustment-results", className="card"),
        html.Div(id="during-dive", className="card"),
        html.Div(id="final-results", className="card"),        
        html.Div(id="references", className="card"),

        dcc.Store(id="ead", data=-1),
        dcc.Store(id="tdt", data=-1),
        dcc.Store(id="gf_high", data=-1),
        dcc.Store(id="gf_high_he", data=-1),
        dcc.Store(id="gf_high_surface_time", data=-1),
        dcc.Store(id="gf_high_personal_adjustment", data=-1),
    ]
)

# Callback for initial calculation
@app.callback(
    Output("initial-results", "children"),
    Output("references", "children"),
    Output("pdcs-question", "style"),
    Output("ead", "data"),
    Input("initial-calculate-button", "n_clicks"),
    State("depth", "value"),
    State("time", "value"),
    State("o2_percentage", "value")
)
def calculate_initial_results(n_clicks, D, T, o2_percentage):
    if n_clicks == 0:
        return "", "", {"display": "none"}, 30

    # Perform initial calculations
    prt = (D / 10 + 1) * math.sqrt(T)
    P_inert_gas = (D / 10 + 1) * (1 - o2_percentage / 100)
    EAD = (P_inert_gas / 0.79 - 1) * 10

    initial_results = f"""
    As the first step we will calculate Pressure Root Time (PRT) for your dive, which is pressure at the bottom (in bar) multiplied by the square root of bottom time (in minutes). PRT can be thought of a measure of nitrogen load.

    Pressure Root Time (PRT) for your dive is {prt:.1f}.
    
    According to research, the ZHL-16C decompression algorithm may need adjustment if the PRT exceeds 25. [6] This value can be directly used to choose your GF with either [analysis in this repository](https://nbviewer.org/github/hjpulkki/gf-recommendation/blob/main/notebooks/PRT_and_GF.ipynb) or by using a graph from Fraedrich [2] also mentioned in the [Theoretical diver blog](https://thetheoreticaldiver.org/wordpress/index.php/2019/06/16/setting-gradient-factors-based-on-published-probability-of-dcs/).

    We can also calculate the equivalent air depth (EAD). It can be used to plan a dive with similar nitrogen load and decompression obligation to be approximated using the StandardAir model. [7]

    Equivalent Air Depth (EAD): {EAD:.1f} meters
    
    ---
    ### ↓ Adjust Gradient Factors Based on PRT
    When unadjusted, the ZHL-16C decompression model may produce dive profiles with insufficient Total Decompression Time (TDT). The StandardAir model enables us to determine the appropriate TDT based on experimental dives conducted by the U.S. Navy. [6][7] The model can be used to estimate the probability of the decompression sickness, or to calculate Total Decompression Time (TDT) for a given dive plan and selected accepted rate of DCS.
    """

    references = """
    # References
    [1] Mitchell, Simon J. "Decompression illness: a comprehensive overview." Diving and Hyperbaric Medicine 54.1Suppl (2024): 1.

    [2] Fraedrich, Doug. "Evidence-Based Study on the Setting of High Gradient Factor." (2024).

    [3] Spisni, Enzo, et al. "A comparative evaluation of two decompression procedures for technical diving using inflammatory responses: compartmental versus ratio deco." Diving and Hyperbaric Medicine 47.1 (2017): 9.

    [4] De Ridder, Sven, et al. "Selecting optimal air diving gradient factors for Belgian military divers: more conservative settings are not necessarily safer." Diving and Hyperbaric Medicine 53.3 (2023): 251.

    [5] Angelini, S. "Dive computer decompression models and algorithms: philosophical and practical views." Underw Technol 35.2 (2018): 51-61.

    [6] Fraedrich, Doug. "Validation of algorithms used in commercial off-the-shelf dive computer." Diving and Hyperbaric Medicine 48.4 (2018): 252.

    [7] Van Liew, H. D., and E. T. Flynn. A simple probabilistic model for estimating the risk of standard air dives. NEDU TR 04-42, Navy Experimental Diving Unit, 2004.

    [8] Doolette, David J., Keith A. Gault, and Wayne A. Gerth. "Decompression from He-N₂-O₂ (trimix) bounce dives is not more efficient than from He-O₂ (heliox) bounce dives." Navy Experimental Diving Unit, Panama City (2015).

    [9] Blatteau JE, Hugon M, Gardette B. "Deep stops during decompression from 50 to 100 msw didn’t reduce bubble formation in man." In: Bennett PB, Wienke BR, Mitchell SJ, editors. Decompression and the Deep Stop. Undersea and Hyperbaric Medical Society Workshop; 2008 Jun 24-25; Salt Lake City (UT). Durham (NC): Undersea and Hyperbaric Medical Society; 2009. p. 195-206.

    [10] Doolette, D. (2019, May 29). Gradient Factors in a Post-Deep Stops World. https://indepthmag.com/gradient-factors-in-a-post-deep-stops-world/
    """

    return dcc.Markdown(initial_results), dcc.Markdown(references), {"display": "block"}, EAD


# Callback for PDCS question and results
@app.callback(
    Output("pdcs-results", "children"),
    Output("he-question", "style"),
    Output("tdt", "data"),
    Output("gf_high", "data"),
    Input("pdcs-next-button", "n_clicks"),
    State("pdcs", "value"),
    State("time", "value"),
    Input("ead", "data"),
)
def calculate_pdcs_results(n_clicks, pdcs, T, EAD):
    if n_clicks == 0:
        return "", {"display": "none"}, -1, -1

    TDT = gf_selection.get_standair_tdt(EAD, T, pdcs)
    fig = gf_selection.standair_plot(EAD, T, pdcs)

    gf_high = gf_selection.fit_gf_to_tdt(T, EAD, TDT)

    pdcs_results = f"""
    According to the StandardAir model [7], the Total Decompression Time (TDT) for this dive should be {TDT:.0f} minutes with probability of Decompression Sickness (DCS) being {100*pdcs:.1f}%.

    Now if we plan the same dive Bulhmann ZHL-16C, it would be reasonable to expect similar total decompression time. However, especially for longer dives these decompression times can be [much shorter](https://nbviewer.org/github/hjpulkki/gf-recommendation/blob/main/notebooks/PRT_and_GF.ipynb) [6]. To keep the risk level similar to more shallow dives, we can choose GF high so that ZHL-16C gives the same Total Decompression Time as StandardAir.

    For a total decompression time of {TDT:.0f} minutes (on 21/0), the Gradient Factors can be set to {gf_high}/{gf_high}.

    ---

    ### ↑ Adjust for Helium Percentage
    Current research indicates that helium does not significantly alter decompression obligations. [8] However, dive computers that account for helium may introduce additional conservatism. To mitigate this, you can adjust the GF High values accordingly.

    """

    content = html.Div(
        [
            dcc.Markdown(pdcs_results, style={"flex": "1", "padding": "10px"}),  # Markdown on the left
            dcc.Graph(figure=fig, style={"flex": "1", "padding": "10px"}),       # Graph on the right
        ],
        style={"display": "flex", "flexDirection": "row", "gap": "20px"}        # Flexbox container
    )

    return content, {"display": "block"}, TDT,  gf_high


# Callback for helium percentage question and results
@app.callback(
    Output("he-results", "children"),
    Output("surface-time-question", "style"),
    Output("gf_high_he", "data"),
    Input("he-next-button", "n_clicks"),
    State("time", "value"),
    State("ead", "data"),
    Input("tdt", "data"),
    State("he_percentage", "value"),
)
def calculate_he_results(n_clicks, T, EAD, TDT, he_percentage):
    if n_clicks == 0:
        return "", {"display": "none"}, -1

    gf_high = gf_selection.fit_gf_to_tdt(T, EAD, TDT, he=he_percentage/100)

    he_results = f"""
    For a total decompression time of {TDT:.0f} minutes (on 21/{he_percentage}), the Gradient Factors can be set to {gf_high}/{gf_high}.

    ---

    ### ↓ Surface Time Adjustment
    Angelini recommends reducing Gradient Factors for surface intervals shorter than 3 hours. [5] For a second dive, they suggest subtracting 15 points from the GF High and adding 1 point back every 12 minutes. However, a [comparison with PADI dive tables](https://nbviewer.org/github/hjpulkki/gf-recommendation/blob/main/notebooks/Repetative-dives-analysis.ipynb) indicates a stronger effect: for dives between 20 m and 40 m with bottom times at the no-decompression limit, you should subtract 37 points and add 1 point back every 5 minutes.

    """

    return dcc.Markdown(he_results), {"display": "block"}, gf_high


# Callback for surface time question and results
@app.callback(
    Output("surface-time-results", "children"),
    Output("personal-adjustment-question", "style"),
    Output("gf_high_surface_time", "data"),
    Input("surface-next-button", "n_clicks"),
    State("surface_time", "value"),
    State("gf_high_he", "data")
)
def calculate_surface_time_results(n_clicks, surface_time, gf_high):
    if n_clicks == 0:
        return "", {"display": "none"}, -1

    gf_high = gf_high - max(37 - surface_time * 60 / 5, 0)

    surface_time_results = f"""
    Updated GF High is {gf_high}

    ---

    ### Personal adjustments

    ↑ Are you planning to exercise within 24 hours before diving? Some studies suggest this may decrease the likelihood of decompression sickness (DCS). [1]

    ↑ Have you implemented other pre-dive interventions [1], such as:
    - Oxygen breathing
    - Exogenous nitric oxide administration
    - Whole-body vibration
    - Sauna use
    - Dark chocolate ingestion
    - Bouncing on a mini trampoline
    """

    return dcc.Markdown(surface_time_results), {"display": "block"}, gf_high

# Callback for personal adjustment and final results
@app.callback(
    Output("personal-adjustment-results", "children"),
    Output("final-results", "children"),
    Output("during-dive", "children"),
    Input("initial-calculate-button", "n_clicks"),
    Input("pdcs-next-button", "n_clicks"),
    Input("he-next-button", "n_clicks"),
    Input("surface-next-button", "n_clicks"),
    Input("final-calculate-button", "n_clicks"),
    State("depth", "value"),
    State("time", "value"),
    State("o2_percentage", "value"),
    State("pdcs", "value"),
    State("he_percentage", "value"),
    State("surface_time", "value"),
    State("personal_adjustment", "value")
)
def calculate_personal_adjustment_and_final_results(n_clicks, n_clicks2, n_clicks3, n_clicks4, n_clicks5, D, T, o2_percentage, pdcs, he_percentage, surface_time, personal_adjustment):
    final_results = ""
    low_gradient_info = ""
    during_dive = ""
    if n_clicks2 > 0:
        P_inert_gas = (D / 10 + 1) * (1 - o2_percentage / 100)
        EAD = (P_inert_gas / 0.79 - 1) * 10
        TDT = gf_selection.get_standair_tdt(EAD, T, pdcs)
        gf_high = gf_selection.fit_gf_to_tdt(T, EAD, TDT, he=he_percentage)
        gf_high -= max(37 - surface_time * 60 / 5, 0)
        gf_high += personal_adjustment
        _, fig = gf_selection.get_gf_tdt(T, D, gf_high, he_percentage, o2_percentage, plot_figure=True)
        final_results = [dcc.Markdown("""# Current plan"""), dcc.Graph(figure=fig)]
    
    if n_clicks5 > 0:
        low_gradient_info = dcc.Markdown("""
        ---
        ### Low Gradient Factor

        The purpose of the low gradient factor (GF low) is to create deep stops similar to bubble models. However, studies show that these stops are not beneficial. [1][3][9] 

        It is recommended to set GF low to at least 55% [6], or equal to GF high [4]. Additionally, GF low can be adjusted to counteract how ZH-L16c "b" coefficients deviate from modern algorithms developed by the U.S. Navy. One suggestion is to set GF low to 83% of GF high. [10] The value could be [further adjusted](https://thetheoreticaldiver.org/wordpress/index.php/2019/06/16/short-comment-on-doolettes-gradient-factors-in-a-post-deep-stops-world/) for extremely deep dives.
        
        """)
        during_dive = dcc.Markdown("""
        # Considerations During the Dive

        ↓ Are you feeling cold?  
        Pay particular attention if you are cold during decompression but not during the bottom phase, as this can impact DCS risk. [1]

        ↓ How well hydrated are you?  
        Proper hydration can reduce the risk of DCS, but avoid overhydration due to its own complications. [1]

        ↓ Did you engage in exercise at depth?  
        Exercise during the bottom phase of a dive can increase the risk of DCS. [1]

        ↓ Would you like to perform a safety stop after mandatory decompression stops?  
        Safety stops have greater significance during decompression dives compared to no-decompression dives. [5]

        ↓ Are you actually making critical decisions based on a Jupyter Notebook?
         """)

    return low_gradient_info, final_results, during_dive


# Run the app
if __name__ == "__main__":
    app.run_server(debug=True)
