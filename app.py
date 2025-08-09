import pandas as pd
import plotly.express as px
from dash import Dash, dcc, html, Input, Output
import json

# Load the dataset
data = pd.read_json("assets/Amazon dataset.json", lines=True)
data['Order Date'] = pd.to_datetime(data['Order Date'])

# Load GeoJSON for India's states
with open("assets/india_states.geojson", "r") as geojson_file:
    india_states = json.load(geojson_file)

# Initialize the Dash app
app = Dash(__name__)

# Define the layout with added metrics and modal for popup graphs
app.layout = html.Div([
    html.Div([
        html.H1("Amazon Sales Dashboard", className="dashboard-header"),
    ]),

    # Total Sales, Total Profit, and Total Customers
    html.Div([
        html.Div([
            html.H4(f"Total Sales: ${data['Sales'].sum():,.2f}", className="metric-box"),
        ], className="metric-box"),
        html.Div([
            html.H4(f"Total Profit: ${data['Profit'].sum():,.2f}", className="metric-box"),
        ], className="metric-box"),
        html.Div([
            html.H4(f"Total Customers: {data['Customer ID'].nunique()}", className="metric-box"),
        ], className="metric-box"),
    ], className="metric-container"),

    # Filters
    html.Div([
        html.Div([
            html.Label("Filter by Year"),
            dcc.Dropdown(
                id="year_filter",
                options=[{"label": year, "value": year} for year in data["Order Date"].dt.year.unique()],
                value=None,
                placeholder="Select a year",
                className="dropdown"
            ),
        ], style={'width': '30%', 'display': 'inline-block'}),
        html.Div([
            html.Label("Filter by State"),
            dcc.Dropdown(
                id="state_filter",
                options=[{"label": state, "value": state} for state in data["State"].unique()],
                value=None,
                placeholder="Select a state",
                className="dropdown"
            ),
        ], style={'width': '30%', 'display': 'inline-block'}),
        html.Div([
            html.Label("Filter by Sub-Category"),
            dcc.Dropdown(
                id="subcategory_filter",
                options=[{"label": subcat, "value": subcat} for subcat in data["Sub-Category"].unique()],
                value=None,
                placeholder="Select a sub-category",
                className="dropdown"
            ),
        ], style={'width': '30%', 'display': 'inline-block'}),
    ], className="filter-section"),

    # Graphs
    html.Div([
        dcc.Graph(id="profit_by_category", className="fade-in", config={"displayModeBar": False}),
        dcc.Graph(id="top_profited_products", className="fade-in", config={"displayModeBar": False}),
        dcc.Graph(id="sales_by_region", className="fade-in", config={"displayModeBar": False}),
        dcc.Graph(id="yearly_sales_trends", className="fade-in", config={"displayModeBar": False}),
        dcc.Graph(id="profit_by_month", className="fade-in", config={"displayModeBar": False}),
        dcc.Graph(id="quantity_by_category", className="fade-in", config={"displayModeBar": False}),
        dcc.Graph(id="profit_by_state", className="fade-in", config={"displayModeBar": False}),
        html.Button("Open Profit by Category", id="open-modal-button", n_clicks=0),
    ], className="graph-container"),

    # Modal for Popup Graph
    html.Div(id="modal", className="modal", children=[
        html.Div(className="modal-content", children=[
            html.Span("×", className="close", id="close-modal"),
            dcc.Graph(id="profit_by_category_modal", className="fade-in", config={"displayModeBar": False}),
        ])
    ])
])


# Callbacks for interactivity
@app.callback(
    [
        Output("profit_by_category", "figure"),
        Output("top_profited_products", "figure"),
        Output("sales_by_region", "figure"),
        Output("yearly_sales_trends", "figure"),
        Output("profit_by_month", "figure"),
        Output("quantity_by_category", "figure"),
        Output("profit_by_state", "figure"),
        Output("profit_by_category_modal", "figure"),
        Output("modal", "style"),
    ],
    [
        Input("year_filter", "value"),
        Input("state_filter", "value"),
        Input("subcategory_filter", "value"),
        Input("open-modal-button", "n_clicks"),
        Input("close-modal", "n_clicks"),
    ]
)
def update_charts(selected_year, selected_state, selected_subcategory, open_modal, close_modal):
    # Set default values to 0 if None
    open_modal = open_modal or 0  # If None, set to 0
    close_modal = close_modal or 0  # If None, set to 0

    # Determine whether the modal should be open or closed
    modal_display = {"display": "none"}  # Default is to hide the modal

    # Handle modal opening
    if open_modal > 0:
        modal_display = {"display": "block"}  # Show modal when the button is clicked

    # Handle modal closing
    if close_modal > 0:
        modal_display = {"display": "none"}  # Hide modal when the close button is clicked

    # Filter the data based on user inputs
    filtered_data = data
    if selected_year:
        filtered_data = filtered_data[filtered_data["Order Date"].dt.year == selected_year]
    if selected_state:
        filtered_data = filtered_data[filtered_data["State"] == selected_state]
    if selected_subcategory:
        filtered_data = filtered_data[filtered_data["Sub-Category"] == selected_subcategory]

    # Profit by Category
    profit_by_category = filtered_data.groupby("Category")["Profit"].sum().reset_index()
    fig1 = px.bar(profit_by_category, x="Category", y="Profit", title="Profit by Category", color="Category")

    # Top Profited Products
    top_profited_products = filtered_data.groupby("Product Name")["Profit"].sum().nlargest(10).reset_index()
    fig2 = px.bar(top_profited_products, x="Product Name", y="Profit", title="Top Profited Products", color="Profit")

    # Sales by Region
    sales_by_region = filtered_data.groupby("Region")["Sales"].sum().reset_index()
    fig3 = px.pie(sales_by_region, values="Sales", names="Region", title="Sales by Region")

    # Yearly Sales Trends
    yearly_sales = filtered_data.groupby(filtered_data["Order Date"].dt.year)["Sales"].sum().reset_index()
    yearly_sales.columns = ["Year", "Sales"]
    fig4 = px.line(yearly_sales, x="Year", y="Sales", title="Yearly Sales Trends")

    # Profit by Month
    profit_by_month = filtered_data.groupby(filtered_data["Order Date"].dt.month)["Profit"].sum().reset_index()
    profit_by_month.columns = ["Month", "Profit"]
    fig5 = px.bar(profit_by_month, x="Month", y="Profit", title="Profit by Month", color="Profit")

    # Quantity by Category
    quantity_by_category = filtered_data.groupby("Category")["Quantity"].sum().reset_index()
    fig6 = px.bar(quantity_by_category, x="Category", y="Quantity", title="Quantity by Category", color="Quantity")

    # Profit by State (Choropleth Map)
    profit_by_state = filtered_data.groupby("State")["Profit"].sum().reset_index()
    fig7 = px.choropleth(
        profit_by_state,
        geojson=india_states,
        locations="State",
        featureidkey="properties.NAME_1",  # Replace with the correct key for your GeoJSON file
        color="Profit",
        title="Profit by State",
        color_continuous_scale="Viridis"
    )
    fig7.update_geos(fitbounds="locations", visible=False)

    # Modal Graph
    fig_modal = px.bar(profit_by_category, x="Category", y="Profit", title="Profit by Category (Popup)",
                       color="Category")

    return fig1, fig2, fig3, fig4, fig5, fig6, fig7, fig_modal, modal_display


# Run the app
if __name__ == "__main__":
    app.run(debug=True)
