import os
import base64
from werkzeug.utils import secure_filename
from dash import Dash, html, dcc, Input, Output, State
import dash_bootstrap_components as dbc
from embed import embed
from query import query

# these three lines swap the stdlib sqlite3 lib with the pysqlite3 package
#__import__('pysqlite3')
#import sys
#sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')

# Load environment variables
from dotenv import load_dotenv

load_dotenv()

# Configuration
TEMP_FOLDER = os.getenv("TEMP_FOLDER", "./_temp")
os.makedirs(TEMP_FOLDER, exist_ok=True)

# Initialize the Dash app with the Bootstrap theme
app = Dash(__name__, external_stylesheets=[dbc.themes.LUMEN])

collection_names = ["PyAEDT", "PyFluent", "PyMech"]

# App Layout
app.layout = dbc.Container(
    [
        dbc.Row(
            dbc.Col(html.H1("PyAnsys Chatbot"), width={"size": 6, "offset": 3}),
            className="my-4",
        ),
        html.Hr(),
        dcc.Store(id='chat-history-store', data=''),
        # File Embedding Section
        dbc.Row(
            [
                dbc.Col(
                    html.H3("Embed a New File, if any"), width={"size": 6, "offset": 3}
                ),
                dbc.Col(
                    dcc.Upload(
                        id="upload-file",
                        children=html.Div(
                            ["Drag and Drop or ", html.A("Select Files")]
                        ),
                        style={
                            "width": "100%",
                            "height": "60px",
                            "lineHeight": "60px",
                            "borderWidth": "1px",
                            "borderStyle": "dashed",
                            "borderRadius": "5px",
                            "textAlign": "center",
                            "marginTop": "10px",
                        },
                        multiple=True,
                    ),
                    width={"size": 6, "offset": 3},
                ),
                dbc.Col(
                    html.Div(id="embed-status", className="text-center my-3"),
                    width={"size": 6, "offset": 3},
                ),
            ]
        ),
        html.Hr(),
        # Chat Section
        dbc.Row(
            [
                dbc.Col(html.H3("Chat with the Model"), width={"size": 6, "offset": 3}),
                dbc.Col(
                    dcc.Textarea(
                        id="query-input",
                        placeholder="Enter your query here...",
                        style={"width": "100%", "height": "100px"},
                    ),
                    width={"size": 6, "offset": 3},
                ),
                dbc.Col(
                    dcc.RadioItems(
                        id="collection-name-radio",
                        options=[{"label": name, "value": name} for name in collection_names],
                        value=collection_names[0],  # Default selected values
                        labelStyle={"display": "block"},
                    ),
                    width={"size": 6, "offset": 3},
                ),
                dbc.Col(
                    html.Button(
                        "Submit Query",
                        id="submit-query",
                        n_clicks=0,
                        className="btn btn-primary btn-block mt-2",
                    ),
                    width={"size": 6, "offset": 3},
                ),
                dbc.Col(
                    html.Div(id="query-response", className="text-center my-3"),
                    width={"size": 6, "offset": 3},
                ),
            ]
        ),
    ],
    fluid=True,
)


# Define callbacks for file embedding
@app.callback(
    Output("embed-status", "children"),
    Input("upload-file", "contents"),
    State("upload-file", "filename"),
    State("collection-name-radio", "value"),
    prevent_initial_call=True,
)
def handle_file_upload(contents, filenames, collection_name):
    if contents is None or filenames is None:
        return "No file uploaded."

    alerts = []
    
    for content, filename in zip(contents, filenames):  
        # Secure the filename to avoid directory traversal attacks
        filename = secure_filename(filename)
        print(filename)
        # Decode the base64 content
        content_type, content_string = content.split(",")
        decoded = base64.b64decode(content_string)

        # Save the file to the temporary folder
        file_path = os.path.join(TEMP_FOLDER, filename)
        with open(file_path, "wb") as f:
            f.write(decoded)

        # Call the embed function with the file path
        if embed(file_path, collection_name):
            alerts.append(dbc.Alert(f"File {filename} embedded successfully!", color="success", className="my-3"))
        else:
            alerts.append(dbc.Alert(f"Failed to embed file {filename}.", color="danger", className="my-3"))

    return alerts


# Define callbacks for querying
@app.callback(
    Output("query-response", "children"),
    Output("chat-history-store", "data"),
    Input("submit-query", "n_clicks"),
    State("query-input", "value"),
    State("collection-name-radio", "value"),
    State("chat-history-store", "data"),
    prevent_initial_call=True,
)
def handle_query(n_clicks, user_query, collection_name, chat_history):
    if not user_query:
        return dbc.Alert("Query cannot be empty.", color="warning", className="my-3")
    
    input_ = {"collection_name":collection_name, "question":user_query, "chat_history":chat_history}
    response = query(input_)
    chat_history = chat_history + "\nUSER: " + user_query
    if response:
        print(response)
        chat_history = chat_history + "\nBOT:" + response
        return dbc.Alert(f"Response: {response}", color="info", className="my-3"), chat_history
    return dbc.Alert(
        "Something went wrong. Please try again.", color="danger", className="my-3"
    ), chat_history


# Run the app
if __name__ == "__main__":
    # Admin Frontend
    app.run_server(host="0.0.0.0", port=9001, debug=True)
    
