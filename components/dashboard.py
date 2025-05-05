from dash import html, dcc, Dash, Input, Output, State
import dash_bootstrap_components as dbc
import plotly.express as px
from sqlalchemy import func, extract
from db import get_db_connection_with_sqlachemy, Record  # Assuming Record is your database model
import pandas as pd

import data_entry_style as style
app = Dash(__name__)

def get_data():
    session = get_db_connection_with_sqlachemy()
    df = pd.read_sql("SELECT * FROM records", session.bind)
    df["amount"] = df["amount"].astype(float)
    
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df["month"] = df["timestamp"].dt.month
    df["month_name"] = df["timestamp"].dt.strftime("%b")
    return df

def make_bar_chart(df, x, y, title):
    fig = px.bar(df, x=x, y=y, title=title)
    fig.update_traces(marker_color=style.font_color)
    fig.update_layout(
        paper_bgcolor="rgba(0, 0, 0, 0)",
        plot_bgcolor="rgba(0, 0, 0, 0)",
    )
    return fig

def make_line_chart(df, x, y, title):
    fig = px.line(df, x=x, y=y, title=title,color_discrete_sequence=[style.font_color])
    fig.update_traces(marker_color=style.font_color)
    fig.update_layout(
        paper_bgcolor="rgba(0, 0, 0, 0)",
        plot_bgcolor="rgba(0, 0, 0, 0)",
    )
    return fig
# Fetch data from the database
df = get_data()
# Function to create a card columns
def card_column(title, value, monetary=True):
    """
        Return a card that shows dashbaord metrics
        
        Args:
            title (str): The title of the card.
            value (float): The value to be displayed in the card.
            monetary (bool): If True, format the value as currency.
    """
    if monetary:
        value = f"#{value:,.2f}"
    return dbc.Col([
        dbc.Card([
            dbc.CardBody([
                html.H2(title, className="card-title",style={"color": style.background_color}),
                html.H4(value, className="card-text",style={"color": style.background_color}),
            ])
        ])
    ], className="card_col")
# dropdown options
month_options = [{"label": month, "value": month} for month in df["month_name"].unique()]
status_options = [{"label": "Paid", "value": "True"}, {"label": "Unpaid", "value": "False"}]
service_options = [{"label": service, "value": service} for service in df["service"].unique()]

# Layout for dropdowns
dropdowns = html.Div([
    dbc.Row([
        dbc.Col([
            dcc.Dropdown(
                id="month-dropdown",
                options=month_options,
                placeholder="Select Month",
                clearable=True,
            )
        ], width=4, className="db_dropdown"),
        dbc.Col([
            dcc.Dropdown(
                id="status-dropdown",
                options=status_options,
                placeholder="Select Paid Status",
                clearable=True,
            )
        ], width=4,className="db_dropdown"),
        dbc.Col([
            dcc.Dropdown(
                id="service-dropdown",
                options=service_options,
                placeholder="Select Service",
                clearable=True,
            )
        ], width=4,className="db_dropdown"),
    ], className="mb-4 row"),
])
def dashboard_layout():
    # Fetch total revenue
    total_revenue =df["amount"].sum()

    # Fetch total debt (unpaid transactions)
    total_debt = df[df["status"] == "False"]["amount"].sum()

    # Fetch total transactions
    total_transactions = len(df) or 0

    # Fetch total unpaid transactions
    total_unpaid_transactions = df[df["status"] == "False"].shape[0] 
    
        
    card_layout = html.Div([
        dbc.Row([
            card_column("Total Revenue", total_revenue, monetary=True),
            card_column("Total Debt", total_debt, monetary=True),
            card_column("Total Transactions", total_transactions, monetary=False),
            card_column("Unpaid Transactions", total_unpaid_transactions, monetary=False),
        ], className="card_row",id="card-layout",),  
        
    ])
    
    renenue_section = html.Div([
        dbc.Row([
            dbc.Col([
                dcc.Graph(id="service_revenue", figure=make_bar_chart(df, "service", "amount", "Service Revenue")),
                ]),
            dbc.Col([
                dcc.Graph(id="phone_revenue", figure=make_bar_chart(df, "phone_name", "amount", "Phone Revenue")),
            ])
        ],className="row")
    ])


    dashboard_schema = html.Div([
        dropdowns,
        card_layout,
        dcc.Graph(
            id='line-chart',
            figure=make_line_chart(df, 'timestamp', 'amount', 'Revenue Timeline')
        ),
        renenue_section,
    ])
    return dashboard_schema
    
def register_dashboard_callbacks(app):
    # Callback to update cards and charts based on dropdown filters
    @app.callback(
        [
            Output("card-layout", "children"),
            Output("line-chart", "figure"),
            Output("service_revenue", "figure"),
            Output("phone_revenue", "figure"),
        ],
        [
            Input("month-dropdown", "value"),
            Input("status-dropdown", "value"),
            Input("service-dropdown", "value"),
        ],
        prevent_initial_call=True
    )
    def update_dashboard(selected_month, selected_status, selected_service):
        # Filter data based on dropdown selections
        filtered_df = df.copy()
        if selected_month: 
            filtered_df = filtered_df[filtered_df["month_name"] == selected_month]
        if selected_status:
            filtered_df = filtered_df[filtered_df["status"] == selected_status]
        if selected_service:
            filtered_df = filtered_df[filtered_df["service"] == selected_service]

        # Calculate metrics
        total_revenue = filtered_df["amount"].sum()
        total_debt = filtered_df[filtered_df["status"] == "False"]["amount"].sum()
        total_transactions = len(filtered_df)
        total_unpaid_transactions = filtered_df[filtered_df["status"] == "False"].shape[0]

        # Create cards
        cards = dbc.Row([
            card_column("Total Revenue", total_revenue, monetary=True),
            card_column("Total Debt", total_debt, monetary=True),
            card_column("Total Transactions", total_transactions, monetary=False),
            card_column("Unpaid Transactions", total_unpaid_transactions, monetary=False),
        ], className="card_row")

        # Update charts
        line_chart = make_line_chart(filtered_df, 'timestamp', 'amount', 'Daily Revenue')
        service_revenue_chart = make_bar_chart(filtered_df, "service", "amount", "Service Revenue")
        phone_revenue_chart = make_bar_chart(filtered_df, "phone_name", "amount", "Phone Revenue")

        return cards, line_chart, service_revenue_chart, phone_revenue_chart

    