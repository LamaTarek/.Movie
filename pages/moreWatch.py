import dash
from dash import html, dcc, callback, Input, Output, State
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
import pickle
import numpy as np
import sklearn

dash.register_page(__name__, name='More', path='/moreWatch')
navbar = dbc.Navbar(
    dbc.Container(
        [
            html.A(
                dbc.Row(
                    [
                        dbc.Col(html.Img(src='/assets/favicon.ico', height="30px")),
                        dbc.Col(dbc.NavbarBrand(".Movie", className="ms-2", style={"fontFamily": "Pacifico, cursive"})),
                    ],
                    align="center",
                    className="g-0",
                ),
                href="/",  # Link to the homepage
                style={"textDecoration": "none", },
            ),
            dbc.NavbarToggler(id="navbar-toggler", n_clicks=0),
            dbc.Collapse(
                dbc.Nav(
                    [
                        dbc.NavLink("Home", href="/", active="exact", style={"color": "white"}),
                        dbc.NavLink("User Page", href="/UserPage", active="exact", style={"color": "white"}),
                        dbc.NavLink("Item Page", href="/ItemPage", active="exact", style={"color": "white"}),
                    ],
                    className="ms-auto",  # Align links to the right
                    navbar=True,
                ),
                id="navbar-collapse",
                navbar=True,
            ),
        ]
    ),
    color="rgba(0, 0, 0, 0)",  # Set background color to transparent
    dark=True,
)

# Function to generate the layout for the watchlist section
def generate_morelist_layout():
    # Create cards for the watchlist items
    watchlist_cards = [
        dbc.Card(
            [
                dbc.Row(
                    [
                        dbc.Col(
                            dbc.CardImg(
                                src="/assets/coco.jpg",
                                className="img-fluid rounded-start",
                                style={'height':"100%"}
                            ),
                            className="col-md-4",
                        ),
                        dbc.Col(
                            dbc.CardBody(
                                [
                                    html.H4("Card title", className="card-title"),
                                    html.P(
                                        "This is a wider card with supporting text "
                                        "below as a natural lead-in to additional "
                                        "content. This content is a bit longer.",
                                        className="card-text",
                                    ),
                                    html.Small(
                                        "Last updated 3 mins ago",
                                        className="card-text text-muted",
                                    ),
                                ]
                            ),

                        ),
                    ],
                    className="g-0 d-flex ",
                )
            ],
            className="mb-3",

        )

    ]

    # Return the watchlist section
    return html.Div(
        children=[
            dbc.Row(html.H2("Your Watchlist", style={"color": "white"})),
            html.Div(
                children=[dbc.Row(dbc.Col(card)) for card in watchlist_cards]
            ),

        ]
    )


dash.register_page(__name__, name='More', path='/moreWatch')

layout = html.Div([dbc.Container([

    dbc.Row(navbar),
    dbc.Row([generate_morelist_layout()]),
], style={"height": "161vh"})])
