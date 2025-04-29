from dash import html, dcc, Input, Output, ALL, callback_context, State
import dash
from dash.dash_table import DataTable
import data_entry_style as style
from db import get_db_connection_with_sqlachemy, Record
import dash_bootstrap_components as dbc
import pandas as pd

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
        session.remove()  # Clean up the session

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
    df = df.rename(columns={"phone_name": "Phone Name", "service": "Service", "name": "Client Name", "amount": "Amount", "status": "Status"})
    # Create a list of rows for the table
    table_rows = []
    for _, row in df.iterrows():
        row_cells = [
            html.Td(row[col]) for col in df.columns if col != "timestamp"
        ]
        if paid is False:
            # Add a button to the row if paid is False
            row_cells.append(
                html.Td(
                    html.Button(
                        "Mark as Paid",
                        id=str(row["id"]),  # Use a unique ID for each button
                    )
                )
            )
        table_rows.append(html.Tr(row_cells))

    # Create the table
    table_header = [html.Th(col) for col in df.columns if col != "timestamp"]
    if paid is False:
        table_header.append(html.Th("Action"))  # Add a header for the action column

    table = dbc.Table(
        [html.Thead(html.Tr(table_header)), html.Tbody(table_rows)],
        striped=True,
        hover=True,
        responsive=True,
        bordered=True,
        style={"marginTop": "20px", "backgroundColor": "rgb(232,231,171)"},
    )

    return html.Div(table)

# Callback to handle marking a record as paid
def register_record_callbacks(app):
    @app.callback(
        Output("tabs-content", "children"),
        Input("id", "n_clicks"),  # Listen for all buttons with this structure
        prevent_initial_call=True,
    )
    def mark_as_paid(n_clicks, button_ids):
        if not n_clicks or all(click is None for click in n_clicks):
            raise dash.PreventUpdate

        # Find the button that was clicked
        for i, click in enumerate(n_clicks):
            if click:
                record_id = int(button_ids[i]["index"])  # Extract the record ID from the button ID
                session = get_db_connection_with_sqlachemy()
                try:
                    # Update the record in the database
                    record = session.query(Record).filter(Record.id == record_id).first()
                    if record:
                        record.status = "True"  # Mark as paid
                        session.commit()
                finally:
                    session.remove()  # Clean up the session

        # Refresh the layout
        return records_layout(paid=False)