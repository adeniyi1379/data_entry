import csv
from dash import html, dcc, Input, Output, State
import pandas as pd
import data_entry_style as style

# Load services from the CSV file
def load_services():
    """Load services from the CSV file."""
    try:
        services = pd.read_csv("services.csv")
        return services['service'].tolist()
    except FileNotFoundError:
        return []

# Append a new service to the CSV file
def append_service(new_service):
    """Append a new service to the CSV file."""
    with open("services.csv", mode="a", newline="") as file:
        writer = csv.writer(file)
        writer.writerow([new_service])

# Layout for the Service tab
def service_layout():
    """Generate the layout for the Service tab."""
    services = load_services()

    return html.Div(
        [
            html.H2("Available Services", style={"textAlign": "center", "marginBottom": "20px"}),
            html.Ul(
                [html.Li(service, style={"marginRight": "10px", "color": "rgb(232,37,97)"}) for service in services],
                style={"padding": "20px", "backgroundColor": "rgb(232,231,171)", "borderRadius": "5px" , "display":"flex", "flexDirection": "column", "alignItems": "center"},
            ),
            html.Div(
                [
                    dcc.Input(
                        id="new-service-input",
                        type="text",
                        placeholder="Enter new service",
                        style=style.input_style,
                    ),
                    html.Button(
                        "Add Service",
                        id="add-service-button",
                        style=style.button_style,
                    ),
                    html.Div(id="service-message", style=style.message_style),
                ],
                style={"marginTop": "20px"},
            ),
        ],
        style={"padding": "20px"},
    )

# Callback to handle adding a new service
def register_service_callbacks(app):
    @app.callback(
        [Output("service-message", "children"), Output("services-store", "data")],
        Input("add-service-button", "n_clicks"),
        State("new-service-input", "value"),
        State("services-store", "data"),
        prevent_initial_call=True,
    )
    def add_service(n_clicks, new_service, current_services):
        if not new_service:
            return "Please enter a service name.", current_services
        if str.lower(new_service) in [str.lower(s) for s in current_services]:
            return f"Service '{new_service}' already exists.", current_services

        # Append the new service to the CSV file
        append_service(new_service)

        # Update the services list
        updated_services = current_services + [new_service]
        return f"Service '{new_service}' added successfully!", updated_services
