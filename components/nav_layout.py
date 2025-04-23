from dash import html, dcc, Input, Output, callback_context
import data_entry_style as style
import data_entry_style as style
import pandas as pd
from components.records import records_layout
from components.transaction_layout import transaction_layout
from components.service import service_layout

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
    html.Div(id='tabs-content', style=style.page_style),
])

# Callback for tabs
def register_callbacks(app):
    @app.callback(
        Output('tabs-content', 'children'),
        Input('main', 'value')
    )
    def display_page(tab):
        if tab == 'transaction':
            return transaction_layout
        elif tab == 'service':
            return service_layout
        elif tab == 'dashboard':
            return html.Div("Dashboard Page")
        elif tab == 'records':
            return records_layout()
        elif tab == 'debt':
            return records_layout(paid=False)
        elif tab == 'logout':
            return html.Div("You have logged out.")
        return html.Div("Welcome! Please select an option from the navigation bar.")
