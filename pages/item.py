import dash
from dash import html, dcc, callback, Input, Output, State
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
import pickle
import numpy as np
import sklearn

dash.register_page(__name__, name='Item Page', path='/ItemPage')
ratings = pd.read_csv('ratings.csv')
movies = pd.read_csv('movies.csv')
links = pd.read_csv('links.csv')
ratings['ones'] = 1
history = ratings.pivot_table(index='userId', columns='movieId', values='ones', fill_value=0)
data = ratings.merge(movies, how='left', on=['movieId'])
def user_rated_movies(user_id):
    items_our_user_rated = sorted(data[data.userId==user_id][['movieId', 'title', 'genres','rating']].values, key=lambda x: x[1])
    return items_our_user_rated
def not_watched(user_id):
    items_our_user_can_rate = data[~data.userId.isin(user_rated_movies(user_id))].movieId.values
    return items_our_user_can_rate
def movie_info(movie_id):
    try:
        return movies[movies.movieId == movie_id].values[0]
    except:
        return None


def adjusted_cosine_sim(vec_a, vec_b):
    a_avg = np.average(vec_a)
    b_avg = np.average(vec_b)

    sim_score = np.dot(vec_a - a_avg, vec_b - b_avg) / (np.linalg.norm(vec_a - a_avg) * np.linalg.norm(vec_b - b_avg))

    return sim_score


def most_sim(movie_id):
    sim_movies = []
    all_info = []
    utility_matrix = history
    for j in data.movieId.unique():
        sim_movies.append((j, adjusted_cosine_sim(utility_matrix.loc[:, movie_id], utility_matrix.loc[:, j])))

    sim_movies = sorted(sim_movies, key=lambda x: x[1], reverse=True)

    for mov in sim_movies:
        ret = movies[movies.movieId == mov[0]]
        if ret is None:
            all_info.append(mov)
        else:
            all_info.append(ret)
    return all_info

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
                href="/",
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
                    className="ms-auto",
                    navbar=True,
                ),
                id="navbar-collapse",
                navbar=True,
            ),
        ]
    ),
    color="rgba(0, 0, 0, 0)",
    dark=True,
)

number_input = html.Div(
    [
        html.P("Enter Movie ID"),

        dbc.Input(type="number", min=1, max=610, step=1, size="lg", className="mb-3",
                  placeholder="between 1 and 9724 ", id="movieid", ),

    ],

)
number_input2 = html.Div(
    [
        html.P("Enter number of similar movies to recommend"),

        dbc.Input(type="number", size="lg", className="mb-3",
                  placeholder="", id="k"),

    ],

)

card_margin_right = {
    "marginRight": "20px"
}


#
# item_list = user_rated_movies(1)
# n = len(item_list)


def generate_watchlist_layout(userid=1, k=3):
    # Create cards for the watchlist items
    watchlist_cards = [
        dbc.Card(
            className="mb-3",  # Added margin bottom class
            style={"maxWidth": "470px", "backgroundColor": "#1f1f29", "borderRadius": "10px",
                   **(card_margin_right if i < 2 else {})},  # Added border radius and right margin
            children=[
                dbc.CardBody(
                    [
                        html.Div(
                            className="g-0 d-flex",
                            children=[
                                dbc.Col(
                                    html.Img(
                                        src="/assets/coco.jpg",
                                        className="img-fluid rounded-start",

                                    ),
                                    className="col-md-4"
                                ),
                                dbc.Col(
                                    dbc.CardBody(
                                        [
                                            html.H4(
                                                "Movie Title",
                                                className="card-title mb-3",
                                                style={"color": "white", "white-space": "pre-wrap"}

                                            ),
                                            html.P([
                                                # f"{item_list[i][2]}"
                                            ], style={'color': '#636667', 'font-size': '18px'})
                                        ]
                                    ),
                                    className="col-md-8"
                                )
                            ]
                        )
                    ]
                )
            ]
        )
        for i in range(k)
    ]

    # Return the watchlist section
    return html.Div(
        className="container",
        children=[

            dbc.Row([
                dbc.Col(html.H2("Your Watchlist", style={"color": "white"}), width=10),
                dbc.Col(
                    html.A("Show All", href="/moreWatch", className="show-more-link", style={"color": "white"})),
            ]),
            html.Div(
                className="watchlist-scrollable",
                id="watchlist_cards2",
                children=watchlist_cards
            ),

        ]
    )


layout = html.Div([dbc.Container([

    dbc.Row(navbar),
    dbc.Row([

        dbc.Col([
            dbc.Card([

                dbc.CardBody(
                    [
                        html.H1(".Movie", className="card-title",
                                style={"fontFamily": "Pacifico, cursive", 'margin-bottom': '30px'}),
                        number_input,
                        number_input2,
                        dbc.Button('Predict', id='submit', outline=True, size='lg',
                                   style={"border-color": "#6A0000", "color": "white"}, className="d-grid dash-button"
                                   ),
                    ], style={'width': '500px'}
                ),
            ], style={'height': '380px', "maxWidth": "540px", "backgroundColor": "#1f1f29", "borderRadius": "10px",
                      "color": "white"})
        ], width=5, style={'margin-top': '30px'}),
        dbc.Col(html.Div([
            dbc.Card(
                className="mb-3 fix",
                style={'height': '380px', 'width': '100%', "backgroundColor": "#1f1f29", "borderRadius": "10px"},

                children=[
                    dbc.CardBody(
                        [
                            html.Div(
                                className="g-0 d-flex",
                                children=[
                                    dbc.Col(
                                        html.Img(
                                            src="assets/l.png",
                                            className="img-fluid rounded-start ",

                                        ),
                                        className="col-md-4"
                                    ),
                                    dbc.Col(
                                        dbc.CardBody(
                                            [
                                                html.H1(
                                                    "Movie title",
                                                    className="card-title mb-3",
                                                    style={"color": "white", "white-space": "pre-wrap"}

                                                ),

                                                html.P([
                                                    f" Genre"
                                                ], style={'color': '#636667', 'font-size': '18px'})
                                            ]
                                        ),
                                        className="col-md-8"
                                    )
                                ],
                            )
                        ]
                    )
                ]
            )
        ], id="movieInfo"), width=7, style={'margin-top': '30px'}, ),

    ]),
    dbc.Row([
        dbc.Col([
            generate_watchlist_layout(),
        ], width=12, style={'margin-top': '30px'}),

    ]),

], style={"height": "110vh", }, )])


@callback(
    Output(component_id='watchlist_cards2', component_property='children'),
    Output(component_id='movieInfo', component_property='children'),
    Input(component_id='submit', component_property='n_clicks'),
    State(component_id='movieid', component_property='value'),
    State(component_id='k', component_property='value'),
)
def func(n_clicks, movieid, k):
    if n_clicks is None or n_clicks == 0:
        # If no click event or initial load, return the current watchlist cards
        return dash.no_update

    movie_data = movie_info(movieid)

    new_movie_info = [
        dbc.Card(
            className="mb-3 fix",
            style={'height': '380px', 'width': '100%', "backgroundColor": "#1f1f29", "borderRadius": "10px"},

            children=[
                dbc.CardBody(
                    [
                        html.Div(
                            className="g-0 d-flex",
                            children=[
                                dbc.Col(
                                    html.Img(
                                        src="/assets/coco.jpg",
                                        className="img-fluid rounded-start ",

                                    ),
                                    className="col-md-4"
                                ),
                                dbc.Col(
                                    dbc.CardBody(
                                        [
                                            html.H1(
                                                movie_data[1],
                                                className="card-title mb-3",
                                                style={"color": "white", "white-space": "pre-wrap"}

                                            ),

                                            html.P([
                                                f"{movie_data[2]}"
                                            ], style={'color': '#636667', 'font-size': '18px'})
                                        ]
                                    ),
                                    className="col-md-8"
                                )
                            ],
                        )
                    ]
                )
            ]
        )
    ]

    item_list = most_sim(movieid)
    n = len(item_list)
    new_watchlist_cards = [
        dbc.Card(

            className="mb-3",  # Added margin bottom class
            style={"height": '250px', "maxWidth": "470px", "backgroundColor": "#1f1f29", "borderRadius": "10px",
                   **(card_margin_right if i < 2 else {})},  # Added border radius and right margin
            children=[
                dbc.CardBody(
                    [
                        html.Div(
                            className="g-0 d-flex",
                            children=[
                                dbc.Col(
                                    html.Img(
                                        src="/assets/coco.jpg",
                                        className="img-fluid rounded-start",

                                    ),
                                    className="col-md-4"
                                ),
                                dbc.Col(
                                    dbc.CardBody(
                                        [
                                            html.H4(
                                                item_list[i].values[0][1],
                                                className="card-title mb-3",
                                                style={"color": "white", "white-space": "pre-wrap"}
                                            ),

                                            html.P([
                                                f"{item_list[i].values[0][2]}"
                                            ], style={'color': '#636667', 'font-size': '18px',"white-space": "pre-wrap"})
                                        ]
                                    ),
                                    className="col-md-8"
                                )
                            ]
                        )
                    ]
                )
            ]
        )
        for i in range(1,k+1)
    ]

    return new_watchlist_cards, new_movie_info
