from dash import html, dcc, Input, Output
from dash.dash_table import DataTable
import data_entry_style as style
from db import get_db_connection_with_sqlachemy, Record

# Fetch transaction records from the database
def fetch_records(paid=None):
    """
    Fetch transaction records from the database using SQLAlchemy.
    Optionally filter by the 'paid' status.
    
    Args:
        paid (bool or None): If True, fetch only paid records.
                             If False, fetch only unpaid records.
                             If None, fetch all records.
                             
    Returns:
        list: A list of dictionaries representing the records.
    """
    session = get_db_connection_with_sqlachemy()
    try:
        # Base query
        query = session.query(Record)
        
        # Apply filter if 'paid' is specified
        if paid is not None:
            query = query.filter(Record.status == str(paid))  # Assuming 'status' is stored as a string
        
        # Sort by timestamp in descending order
        query = query.order_by(Record.timestamp.desc())
        # Execute query and fetch results
        records = query.all()

        # Convert the records into a list of dictionaries
        data = [
            {
                "timestamp": record.timestamp,
                "phone_name": record.phone_name,
                "service": record.service,
                "name": record.name,
                "amount": record.amount,
                "status": record.status,
            }
            for record in records
        ]
        return data
    finally:
        session.remove()  # Clean up the session# Layout for the Records tab

def records_layout(paid=None):
    """
    Generate the layout for the Records tab.
    
    Args:
        paid (bool or None): If True, fetch only paid records.
                             If False, fetch only unpaid records.
                             If None, fetch all records.
                             
    Returns:
        html.Div: The layout for the Records tab.
    """
    data = fetch_records(paid=paid)
    columns = [
        {"name": "Timestamp", "id": "timestamp"},
        {"name": "Phone Name", "id": "phone_name"},
        {"name": "Service", "id": "service"},
        {"name": "Name", "id": "name"},
        {"name": "Amount", "id": "amount"},
        {"name": "Status", "id": "status"},
    ]
    table = DataTable(
        id='records-table',
        columns=columns,
        data=data,
        style_table={'overflowX': 'auto'},
        style_cell={
            'textAlign': 'left',
            'padding': '10px',
            'border': '1px solid #ddd',
        },
        style_header={
            'backgroundColor': '#f4f4f4',
            'fontWeight': 'bold',
        },
        page_size=10,
    )
    return html.Div(
        [
            html.H2("Transaction Records", style={"textAlign": "center", "marginBottom": "20px"}),
            table,
        ],
        style={"padding": "20px"}
    )

# Tabs layout
tabs_layout = html.Div([
    html.H1("Welcome to the Dashboard"),
    dcc.Tabs(id="main", value='transaction', children=[
        dcc.Tab(label='Transaction', value='transaction'),
        dcc.Tab(label='Service', value='service'),
        dcc.Tab(label='Dashboard', value='dashboard'),
        dcc.Tab(label='Records', value='records'),
        dcc.Tab(label='Debt', value='debt'),
        dcc.Tab(label='Logout', value='logout')
    ]),
    html.Div(id='tabs-content', style=style.page_style),
])

