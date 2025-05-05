from dash import html, dcc, Input, Output, callback_context
import data_entry_style as style
import pandas as pd
from components.records import records_layout
from components.transaction_layout import transaction_layout
from components.service import service_layout,register_service_callbacks, load_services
from components.dashboard import dashboard_layout
phone_name = pd.read_csv("phone_name.csv")
services = pd.read_csv("services.csv")

# Tabs layout
tabs_layout = html.Div([
    html.H1("Welcome Admin"),
    dcc.Tabs(id="main", value='transaction', children=[
        dcc.Tab(label='Transaction', value='transaction', style=style.nav_inner_button_style),
        dcc.Tab(label='Service', value='service', style=style.nav_inner_button_style),
        dcc.Tab(label='Dashboard', value='dashboard', style=style.nav_inner_button_style),
        dcc.Tab(label='Records', value='records', style=style.nav_inner_button_style),
        dcc.Tab(label='Debt', value='debt', style=style.nav_inner_button_style),
        dcc.Tab(label='Logout', value='logout', style=style.nav_inner_button_style)
    ], style=style.nav_button_style),
    dcc.Store(id='records-store', data=[]),  # Placeholder for records-store
    dcc.Store(id='services-store', data=load_services()),  # Add a dcc.Store for services
    dcc.Store(id= "dashboard-store", data={}),  # Placeholder for dashboard-store
    dcc.Store(id='tabs-data-store', data={}),  # Add a dcc.Store component
    html.Div(id='tabs-content', style={**style.page_style}),  # Content area for tabs
])

# Callback for tabs


def register_callbacks(app):
    # Callback to update the data in the store based on the selected tab
    @app.callback(
        Output('tabs-data-store', 'data'),
        Input('main', 'value'),
        prevent_initial_call=True
    )
    def update_store(tab):
        # Store the selected tab's layout identifier in the store
        if tab == 'transaction':
            return {'layout': 'transaction'}
        elif tab == 'service':
            return {'layout': 'service'}
        elif tab == 'dashboard':
            return {'layout': 'dashboard'}
        elif tab == 'records':
            return {'layout': 'records'}
        elif tab == 'debt':
            return {'layout': 'debt'}
        elif tab == 'logout':
            return {'layout': 'logout'}
        return {'layout': 'default'}

    # Callback to update the tabs-content based on the store data
    @app.callback(
        Output('tabs-content', 'children'),
        [Input('tabs-data-store', 'data'), Input('records-store', 'data')],
        prevent_initial_call=True
    )
    def update_tabs_content(tab_data,records_data):
        print(f"Received data: {tab_data}")  # Debugging
        if not tab_data:
            return html.Div("Error: No data received from tabs-data-store.")

        layout = tab_data.get('layout', 'default')
        print(f"Selected layout: {layout}")  # Debugging

        try: 
            if layout == 'transaction':
                return transaction_layout
            elif layout == 'service':
                return service_layout()
            elif layout == 'dashboard':
                return dashboard_layout()
            elif layout == 'records':
                return records_layout()
            elif layout == 'debt':
                return records_layout(paid=False)
            elif layout == 'logout':
                return html.Div("You have logged out.")
            return html.Div("Welcome! Please select an option from the navigation bar.")
        except Exception as e:
            print(f"Error in update_tabs_content: {e}")  # Debugging
            return html.Div(f"An error occurred: {str(e)}")