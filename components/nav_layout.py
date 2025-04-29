from dash import html, dcc, Input, Output, callback_context
import data_entry_style as style
import pandas as pd
from components.records import records_layout
from components.transaction_layout import transaction_layout
from components.service import service_layout,register_service_callbacks

phone_name = pd.read_csv("phone_name.csv")
services = pd.read_csv("services.csv")

# Tabs layout
tabs_layout = html.Div([
    html.H1("Welcome to the Dashboard"),
    dcc.Tabs(id="main", value='transaction', children=[
        dcc.Tab(label='Transaction', value='transaction', style=style.nav_inner_button_style),
        dcc.Tab(label='Service', value='service', style=style.nav_inner_button_style),
        dcc.Tab(label='Dashboard', value='dashboard', style=style.nav_inner_button_style),
        dcc.Tab(label='Records', value='records', style=style.nav_inner_button_style),
        dcc.Tab(label='Debt', value='debt', style=style.nav_inner_button_style),
        dcc.Tab(label='Logout', value='logout', style=style.nav_inner_button_style)
    ], style=style.nav_button_style),
    html.Div(id='tabs-content', style={**style.page_style,"overflowY": "scroll"}),  # Content area for tabs
])

# Callback for tabs


def register_callbacks(app):
    # register_service_callbacks(app)  # Register service callbacks
    @app.callback(
        Output('tabs-content', 'children', allow_duplicate=True),
        Input('main', 'value'),
        prevent_initial_call=True
    )
    def display_page(tab):
        if tab == 'transaction':
            return transaction_layout
        elif tab == 'service':
            return service_layout()  # Call the function to register service callbacks
        elif tab == 'dashboard':
            return html.Div("Dashboard Page")
        elif tab == 'records':
            return records_layout()
        elif tab == 'debt':
            return records_layout(paid=False)
        elif tab == 'logout':
            return html.Div("You have logged out.")
        return html.Div("Welcome! Please select an option from the navigation bar.")
