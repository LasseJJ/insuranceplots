import numpy as np
import plotly.graph_objects as go
from dash import Dash, dcc, html, Input, Output

# Define parameters
W0 = 100  # Initial endowment
L = 40  # Loss from accident
p_s = 0.5  # Probability of accident for high-risk agent (bad type)
p_g = 0.25  # Probability of accident for low-risk agent (good type)
alpha = 3  # Risk aversion parameter
share_high_risk = 0.5 # Proportion of high-risk individuals


# Define utility and contract functions
def utility(wealth_no_accident, wealth_accident, probability, alpha):
    return (1 - probability) * wealth_no_accident ** (1 - alpha) / (1 - alpha) + \
           probability * wealth_accident ** (1 - alpha) / (1 - alpha)


def indifference_curve(wealth_no_accident, utility_level, probability, alpha):
    return ((utility_level * (1 - alpha) - (1 - probability) * wealth_no_accident ** (1 - alpha)) / probability) ** (
            1 / (1 - alpha))


def contract_possibility_line(W0, L, probability):
    coverage = np.linspace(0, L, 100)
    premium = probability * coverage
    wealth_no_accident = W0 - premium
    wealth_accident = W0 - premium - (L - coverage)
    return wealth_no_accident, wealth_accident


def pooled_contract_line(W0, L, p_g, p_s, share_high_risk):
    expected_p = share_high_risk * p_s + (1 - share_high_risk) * p_g
    return contract_possibility_line(W0, L, expected_p)


# Generate initial data
x_vals = np.linspace(0, W0 + 50, W0 + 50)
init_utility_s = utility(W0, W0 - L, p_s, alpha)
init_utility_g = utility(W0, W0 - L, p_g, alpha)
max_utility_s = utility(W0 - p_g * L, W0 - p_s * L, 0, alpha)
max_utility_g = utility(W0 - p_g * L, W0 - p_s * L, 0, alpha)

indifference_curve_s = indifference_curve(x_vals, init_utility_s, p_s, alpha)
indifference_curve_g = indifference_curve(x_vals, init_utility_g, p_g, alpha)

contract_line_s_no_acc, contract_line_s_acc = contract_possibility_line(W0, L, p_s)
contract_line_g_no_acc, contract_line_g_acc = contract_possibility_line(W0, L, p_g)
pooled_line_no_acc, pooled_line_acc = pooled_contract_line(W0, L, p_g, p_s, share_high_risk)

full_insurance_s = (W0 - p_s * L, W0 - p_s * L)
full_insurance_g = (W0 - p_g * L, W0 - p_g * L)

# Initialize the Dash app
app = Dash(__name__)
server = app.server

# Static figure setup
fig = go.Figure()

# Contract Lines and Static Points
fig.add_trace(
    go.Scatter(x=contract_line_s_no_acc, y=contract_line_s_acc, mode='lines', name="Contract Line (High Risk)",
               line=dict(color='blue')))
fig.add_trace(go.Scatter(x=contract_line_g_no_acc, y=contract_line_g_acc, mode='lines', name="Contract Line (Low Risk)",
                         line=dict(color='purple')))
fig.add_trace(go.Scatter(x=pooled_line_no_acc, y=pooled_line_acc, mode='lines', name="Pooled Contract Line",
                         line=dict(color='blue', dash='dot')))
fig.add_trace(
    go.Scatter(x=[0, 150], y=[0, 150], mode='lines', name="Certainty Line", line=dict(color='gray', dash='dot')))
fig.add_trace(
    go.Scatter(x=[full_insurance_s[0]], y=[full_insurance_s[1]], mode='markers', name="Full Insurance (Bad Type)",
               marker=dict(color='red', size=10)))
fig.add_trace(
    go.Scatter(x=[full_insurance_g[0]], y=[full_insurance_g[1]], mode='markers', name="Full Insurance (Good Type)",
               marker=dict(color='green', size=10)))
fig.add_trace(go.Scatter(x=[W0], y=[W0 - L], mode='markers', name="A (No insurance)",
                         marker=dict(color='black', size=10)))

# Adding placeholders for indifference curves, which will be updated dynamically
fig.add_trace(go.Scatter(x=x_vals, y=indifference_curve_s, mode='lines', name="I_s (High Risk)",
                         line=dict(color='red', dash='dash')))
fig.add_trace(go.Scatter(x=x_vals, y=indifference_curve_g, mode='lines', name="I_g (Low Risk)",
                         line=dict(color='green', dash='dash')))

# Set fixed axis range and titles
fig.update_layout(
    xaxis=dict(title="Wealth Level (No Accident)", range=[50, 130]),
    yaxis=dict(title="Wealth Level (Accident)", range=[50, 130]),
    title="Insurance Contracts and Indifference Curves",
    legend=dict(x=0.8, y=1)
)

app.layout = html.Div([
    html.H1(""),
    dcc.Graph(
        id='insurance-plot',
        style={'height': '700px', 'width': '1000px'}  # Adjust these values as needed
    ),

    # Slider for High-Risk Utility Level with finer step size
    html.Label("High-Risk Utility Level"),
    dcc.Slider(
        id='s-slider',
        min=init_utility_s,
        max=max_utility_s + 0.5 * (max_utility_s - init_utility_s),
        value=init_utility_s,
        step=(max_utility_s + 0.5 * (max_utility_s - init_utility_s) - init_utility_s) / 100,  # Smaller step size
        updatemode='drag',
        marks=None  # Remove the legends
    ),

    # Slider for Low-Risk Utility Level with finer step size
    html.Label("Low-Risk Utility Level"),
    dcc.Slider(
        id='g-slider',
        min=init_utility_g,
        max=max_utility_g + 0.5 * (max_utility_g - init_utility_g),
        value=init_utility_g,
        step=(max_utility_g + 0.5 * (max_utility_g - init_utility_g) - init_utility_g) / 100,  # Smaller step size
        updatemode='drag',
        marks=None  # Remove the legends
    ),
])


# Callback to update the plot
@app.callback(
    Output('insurance-plot', 'figure'),
    Input('s-slider', 'value'),
    Input('g-slider', 'value')
)
def update_plot(new_utility_s, new_utility_g):
    # Update y-values of indifference curves
    updated_indifference_curve_s = indifference_curve(x_vals, new_utility_s, p_s, alpha)
    updated_indifference_curve_g = indifference_curve(x_vals, new_utility_g, p_g, alpha)

    # Update only the y data of the indifference curve traces
    fig.data[-2].y = updated_indifference_curve_s  # Updating High Risk Indifference Curve
    fig.data[-1].y = updated_indifference_curve_g  # Updating Low Risk Indifference Curve

    return fig


# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
