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

# import defined modules
import data_entry_style as style
from db import get_db_connection, get_db_connection_with_sqlachemy, Record
from components.nav_layout import  tabs_layout,register_callbacks
from components.transaction_layout import transaction_layout


#initialize the Flask server
server = Flask(__name__)
server.secret_key = os.urandom(24)  # Set a secret key for session management

#initialize the Dash app
app = Dash(__name__, server=server, url_base_pathname='/',suppress_callback_exceptions=True)

#Phoen names and services
phone_name = pd.read_csv("phone_name.csv")
services = pd.read_csv("services.csv")

#login page layout
login_layout = html.Div([
html.H2("Data entry form"),
dcc.Input(id='username', type='text', placeholder='Username', style=style.input_style),
dcc.Input(id='password', type='password', placeholder='Password', style=style.input_style),
html.Button('Login', id='login-button',style=style.login_button_style),
html.Div(id= "login-message")

], style=style.container_style),



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
    ]
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
            # session['role'] = user["role"]
            print(f"Username: {username}")
            print(f"Password: {password}")
            print(f"Stored Password (hashed): {user['password']}")
            return [tabs_layout], ""
        else:
            return login_layout, 'Invalid credentials. Please try again.'
    return login_layout, ''

db_lock = Lock()

# callback for data sunmission
@app.callback(
    [
        Output('submission-message', 'children'),
        Output('phone-names', 'value'),
        Output('services', 'value'),
        Output('name', 'value'),
        Output('amount', 'value'),
        Output('status', 'value')
    ],
    Input('submit-button', 'n_clicks'),
    State('phone-names', 'value'),
    State('services', 'value'),
    State('name', 'value'),
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

# #URL Routing
# @server.route('/')
# def index():
#     if session.get('logged_in'):
#         return app.index()
#     return redirect(url_for('login'))


# @server.route('/login')
# def login_page():
#     return app.index()

register_callbacks(app)
#run app
if __name__ == '__main__':
    app.run_server(host="0.0.0.0", port=8080)