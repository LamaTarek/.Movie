import pandas as pd
import dash
from dash import Dash, dcc, html, callback_context
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc



app = Dash(__name__, external_stylesheets=[dbc.themes.ZEPHYR, dbc.icons.BOOTSTRAP,dbc.icons.FONT_AWESOME], use_pages=True)

app.title = ".Movie"

app.layout = html.Div(

    children=[

                html.Div(
                    id="page-content",
                    children=[
                        dash.page_container
                    ]
                )


    ], style={
        "backgroundColor": "#22292C",

    }
)

if __name__ == "__main__":
    app.run_server(debug=True)
