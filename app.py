import dash
from dash import dcc, html, Dash, Input, Output, State
from flask import Flask, session, redirect, url_for
import os
import datetime
import pandas as pd
import sqlite3
from werkzeug.security import check_password_hash
from sqlalchemy.orm import sessionmaker
from threading import Lock
import dash_bootstrap_components as dbc

# import defined modules
import data_entry_style as style
from db import get_db_connection, get_db_connection_with_sqlachemy, Record
from components.nav_layout import  tabs_layout,register_callbacks
from components.transaction_layout import transaction_layout
from components.service import register_service_callbacks
from components.records import records_layout,register_record_callbacks
from components.login import login_layout
from components.dashboard import register_dashboard_callbacks

#initialize the Flask server
server = Flask(__name__)
server.secret_key = os.urandom(24)  # Set a secret key for session management

#initialize the Dash app
app = Dash(__name__, server=server, url_base_pathname='/',suppress_callback_exceptions=True,external_stylesheets=[dbc.themes.BOOTSTRAP, dbc.icons.BOOTSTRAP])
app.title = "Data Entry App"
#Phoen names and services
phone_name = pd.read_csv("phone_name.csv")
services = pd.read_csv("services.csv")

#layout of the app
app.layout = html.Div(
    [
        dcc.Location(id='url', refresh=False),
        html.Div(
            [
                html.Div(id='page-content',children=[html.Img(src="/assets/IMG_5261.PNG",style=style.logo_style)],  style=style.page_content_style),  # Navigation area
                html.Div(id='main_area',children=login_layout, style=style.main_area_style),  # Main content area
            ],
            style=style.main_container_style,  # Flexbox container
        ),
        
    ],
    style={'backgroundColor': 'rgb(232,231,171)'} 
)
#callback for login
@app.callback(
    [Output('main_area', 'children'),
    Output('login-message', 'children')],
    Input('login-button', 'n_clicks'),
    State('username', 'value'),
    State('password', 'value')
)
def login(n_clicks, username, password):
    if n_clicks:
        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
        conn.close()
        if user and check_password_hash(user['password'], password):
            session['logged_in'] = True
            session['username'] = user["username"]
            if user["role"] == "admin":
                # If the user is an admin, show the admin layout
                return [tabs_layout], "log in successful"
            else:
                return [html.H2("Record a new Sales",style={"color":"#125155",}),
                        transaction_layout], ""
        else:
            return login_layout, [dbc.Alert([html.I(className="bi bi-exclamation-triangle-fill me-2"),"Invalid Credentials"], color="danger", dismissable=True, style= {"width":"50%"})]
    # If the user is not logged in, show the login layout
    return login_layout, ''

db_lock = Lock()

# callback for data sunmission
@app.callback(
    [
        Output('submission_message', 'children'),
        Output('phone_names', 'value'),
        Output('services', 'value'),
        Output('client_name', 'value'),
        Output('amount', 'value'),
        Output('status', 'value')
    ],
    Input('submit-button', 'n_clicks'),
    State('phone_names', 'value'),
    State('services', 'value'),
    State('client_name', 'value'),
    State('amount', 'value'),
    State('status', 'value'),
    prevent_initial_call=True
)
def submit_data(n_clicks, phone_name, service, name, amount, status):
    if n_clicks:
        if not session.get('logged_in'):
            return 'You must be logged in to submit data.', None, None, None, None, None
        
        try:
            # Acquire the lock
            with db_lock:
                # Get the current timestamp
                timestamp = datetime.datetime.now()

                # Connect to the SQLite database
                db_session = get_db_connection_with_sqlachemy()

                # Create a new record in the database
                new_entry = Record(
                    phone_name=phone_name,
                    service=service,
                    name=name,
                    amount=float(amount),  # Ensure amount is a float
                    status=status,
                    timestamp=timestamp
                )
                db_session.add(new_entry)
                db_session.commit()

            # Return success message and reset all inputs
            return 'Data submitted successfully!', None, None, None, None, None
        except Exception as e:
            # Return error message and retain current input values
            return f'Error submitting data: {str(e)}', phone_name, service, name, amount, status
        finally:
            db_session.remove()  # Clean up the session
    return '', None, None, None, None, None

register_callbacks(app)
register_service_callbacks(app)
register_record_callbacks(app)
register_dashboard_callbacks(app)
#run app
if __name__ == '__main__':
    app.run(debug=False)