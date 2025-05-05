from dash import dcc, html
import data_entry_style as style

#login page layout
login_layout = html.Div([
html.H2("Log In"),
dcc.Input(id='username', type='text', placeholder='Username', style=style.input_style),
dcc.Input(id='password', type='password', placeholder='Password', style=style.input_style),
html.Button('Login', id='login-button',style=style.login_button_style),
html.Div(id= "login-message")

], style=style.container_style),
