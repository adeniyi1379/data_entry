from dash import html, dcc, Input, Output, ALL, callback_context, State
from dash.exceptions import PreventUpdate
import dash
from dash.dash_table import DataTable
import data_entry_style as style
from db import get_db_connection_with_sqlachemy, Record
import dash_bootstrap_components as dbc
import pandas as pd
import ast
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
                "id": record.id,
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
        session.remove()  # Clean up the session

def create_mark_as_paid_button(record_id):
    """
    Create a button to mark a record as paid.

    Args:
        record_id (int): The ID of the record.

    Returns:
        html.Button: A button element.
    """
    return dbc.Button(
        "Mark as Paid",
        id={"type": "mark-as-paid-button", "index": record_id},  # Use a dictionary for the ID
        color="success"
    )
    
def generate_table_rows(data, paid=None):
    """
    Generate table rows for the records.

    Args:
        data (list): List of dictionaries representing the records.
        paid (bool or None): If True, fetch only paid records.
                             If False, fetch only unpaid records.
                             If None, fetch all records.

    Returns:
        list: A list of HTML table rows.
    """
    rows = []
    for record in data:
        # Skip 'id' column in display but keep it for reference
        row_cells = [html.Td(record[col]) for col in record if col not in ["id"]]
        
        if paid is False:
            row_cells.append(
                html.Td(
                    create_mark_as_paid_button(record["id"])
                )
            )
        elif paid is not None:  # Add an empty cell for the "Action" column
            row_cells.append(html.Td(""))
        rows.append(html.Tr(row_cells))
    return rows


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
    df = pd.DataFrame(data)  # Convert data to a DataFrame for easier manipulation
    
    # Check if the DataFrame is empty and return a message if it is
    if df.empty:
        return html.Div("No records found.", style={"textAlign": "center", "marginTop": "20px"})
    ## Format the columns to a more readable format
    df = df.rename(columns={"timestamp": "Date","phone_name": "Phone Name", "service": "Service", "name": "Client Name", "amount": "Amount", "status": "Status"})
    
    df["Date"] = pd.to_datetime(df["Date"]).dt.strftime("%Y-%m-%d %H:%M:%S")  # Format the date
    # df["Amount"] = df["Amount"].apply(lambda x: f"${x:.2f}")  # Format the amount as currency
    
    df["Status"] = df["Status"].replace({"True": "Paid", "False": "Unpaid"})  # Replace status values
    # Generate table rows
    table_rows = generate_table_rows(data, paid=paid)
    
    table_header = [html.Th(col) for col in df.columns if col not in ["id", "status"]]
    if paid is False:
        table_header.append(html.Th("Action"))

    table_rows = generate_table_rows(data, paid=paid)
    
    table = dbc.Table(
        [html.Thead(html.Tr(table_header)), html.Tbody(table_rows)],
        striped=True,
        hover=True,
        responsive=True,
        color="warning",
        style={"marginTop": "20px", "backgroundColor": "rgb(232,231,171)"},
    )

    return html.Div([
        table
    ])  

# Callback to handle marking a record as paid
def register_record_callbacks(app):
    @app.callback(
        Output('records-store', 'data'),  # Update the stored data
        Input({'type': 'mark-as-paid-button', 'index': ALL}, 'n_clicks'),
        State('records-store', 'data'),
        prevent_initial_call=True
    )
    def mark_as_paid(button_clicks, stored_data):
        ctx = dash.callback_context
        if not ctx.triggered:
            raise PreventUpdate
            
        # Find which button was clicked
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]
        button_id = ast.literal_eval(button_id)  # Convert string to dict
        record_id = button_id['index']
        
        # Update the database
        session = get_db_connection_with_sqlachemy()
        try:
            record = session.query(Record).filter(Record.id == record_id).first()
            if record:
                record.status = "True"
                session.commit()
        finally:
            session.remove()
        
        # Return updated data (filtered to unpaid only)
        return fetch_records(paid=False)