from dash import html, dcc, Dash, Input, Output, State
import data_entry_style as style
import pandas as pd
phone_name = pd.read_csv("phone_name.csv")
services = pd.read_csv("services.csv")
# Layout for the data entry page (Transaction)
transaction_layoutt = html.Div(
    [
        dcc.Dropdown(
            id='phone-names',
            options=[{'label': name, 'value': name} for name in phone_name['names'].unique()],
            placeholder='Select Phone Name',
            style=style.dropdown_style
        ),
        dcc.Dropdown(
            id='services',
            options=[{'label': service, 'value': service} for service in services['service'].unique()],
            placeholder='Select Service',
            style=style.dropdown_style
        ),
        dcc.Input(id='name', type='text', placeholder='Name', style=style.input_style),
        dcc.Input(id='amount', type='text', placeholder='Amount', style=style.input_style),
        dcc.Dropdown(
            id='status',
            options=[
                {'label': 'Paid', 'value': 'True'},
                {'label': 'Unpaid', 'value': 'False'}
            ],
            placeholder='Select Payment Status',
            style=style.dropdown_style
        ),
        html.Button('Submit', id='submit-button', style=style.button_style),
        html.Div(id='submission-message', style=style.message_style),
    ]
)

def transaction_layout():
    return transaction_layoutt