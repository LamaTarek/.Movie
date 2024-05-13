import dash
from dash import html, dcc, callback, Input, Output, State
import dash_bootstrap_components as dbc
import pandas as pd
import numpy as np
import pickle
from deepctr_torch.models import DeepFM
from sklearn.preprocessing import LabelEncoder
import requests
from bs4 import BeautifulSoup

dash.register_page(__name__, name='User Page', path='/UserPage')

data = pd.read_csv('data.csv')
saved_model = "./pages/model.pkl"
with open(saved_model, 'rb') as file:
    DeepFM_model = pickle.load(file)


def split(x):
    key2index = {}
    key_ans = x.split('|')
    for key in key_ans:
        if key not in key2index:
            key2index[key] = len(key2index) + 1
    return list(map(lambda x: key2index[x], key_ans))

def scrape_movie_poster(movie_title):
    search_url = f"https://www.imdb.com/find?q={movie_title}&s=tt&ttype=ft&ref_=fn_ft"
    response = requests.get(search_url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        result_link = soup.find('td', class_='result_text').find('a')['href']
        movie_url = f"https://www.imdb.com{result_link}"
        movie_response = requests.get(movie_url)
        if movie_response.status_code == 200:
            movie_soup = BeautifulSoup(movie_response.content, 'html.parser')
            poster_element = movie_soup.find('div', class_='poster').find('img')
            poster_url = poster_element['src']
            return poster_url
        else:
            print(f"Failed to fetch movie page: {movie_url}")
    else:
        print(f"Failed to fetch search page: {search_url}")
def user_recommends(user_id):
    obs = {}

    not_watched_list = data[~data.userId.isin(user_rated_movies(user_id))][data.userId == user_id].values
    for movie_info in not_watched_list:
        obs['userId'] = pd.Series(0, LabelEncoder().fit_transform(np.array([user_id])))
        obs['movieId'] = pd.Series(0, LabelEncoder().fit_transform(np.array([movie_info[1]])))
        obs['genres'] = np.array(split(movie_info[6])).reshape(1, -1)
        data.loc[(data.userId == user_id) & (data.movieId == movie_info[1]), 'prediction'] = \
        DeepFM_model.predict(obs)[0][0]

    return sorted(data[data.userId == user_id].values, key=lambda x: x[-1], reverse=True)

def user_rated_movies(user_id):
    items_our_user_rated = sorted(data[data.userId == user_id][['movieId', 'title', 'genres', 'rating']].values,
                                  key=lambda x: x[1])
    return items_our_user_rated


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

carousel = dbc.Carousel(
    items=[
        {"key": "1", "src": "/assets/scale.png"},
        {"key": "2", "src": "/assets/scale (1).png"},
        {"key": "3", "src": "/assets/b.jpg"},

    ],
    controls=True,
    indicators=True,
    interval=1500,
    ride="carousel",
    className="carousel-fade",
    variant="dark",
)
number_input = html.Div(
    [
        html.P("Enter a user ID"),

        dbc.Input(type="number", min=1, max=610, step=1, size="lg", className="mb-3",
                  placeholder="between 1 and 610 ", id="userid", ),

    ],

)
number_input2 = html.Div(
    [
        html.P("Enter number of movies to recommend"),

        dbc.Input(type="number", size="lg", className="mb-3",
                  placeholder="", id="k"),

    ],

)

card_margin_right = {
    "marginRight": "20px"
}

item_list = user_rated_movies(1)
n = len(item_list)


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
                                                item_list[i][1],
                                                className="card-title mb-3",
                                                style={"color": "white", "white-space": "pre-wrap"}

                                            ),
                                            html.P([
                                                html.I(className="fa fa-star text-warning md-5",
                                                       style={"color": "gold"}),
                                                f"  {item_list[i][3]}"
                                            ], style={'color': '#F4BD61'}),
                                            html.P([
                                                f"{item_list[i][2]}"
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
                id="watchlist_cards",
                children=watchlist_cards
            ),

        ]
    )


def generate_predict_layout(userid=1, k=3):
    predict_cards = [
        dbc.Card(
            className="mb-3",
            style={"maxWidth": "540px", "backgroundColor": "#1f1f29", "borderRadius": "10px",
                   **(card_margin_right if i < 2 else {})},
            children=[
                dbc.CardBody(
                    [
                        html.Div(
                            className="g-0 d-flex align-items-center",
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
                                            html.H4("Card title", className="card-title", style={"color": "white"}),

                                            html.Small(
                                                "Last updated 3 mins ago",
                                                className="card-text text-muted",
                                            ),
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
                dbc.Col(html.H2("Recommendation", style={"color": "white"}), width=10),
                dbc.Col(
                    html.A("Show More", href="/moreRecommendation", className="show-more-link",
                           style={"color": "white"})),
            ]),
            html.Div(
                className="watchlist-scrollable",
                id='predict_cards'
                ,
                children=predict_cards
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
                                style={"fontFamily": "Pacifico, cursive", 'margin-bottom': '40px'}),
                        number_input,
                        number_input2,
                        dbc.Button('Predict', id='submit', outline=True, size='lg',
                                   style={"border-color": "#6A0000", "color": "white"}, className="d-grid dash-button"
                                   ),
                    ], style={'width': '500px'}
                ),
            ], style={'height': '420px', "maxWidth": "540px", "backgroundColor": "#1f1f29", "borderRadius": "10px",
                      "color": "white"})
        ], width=5, style={'margin-top': '30px'}),
        dbc.Col([
            carousel
        ], width=7, style={'margin-top': '30px'}),

    ]),
    dbc.Row([
        dbc.Col([
            generate_watchlist_layout(),
        ], width=12, style={'margin-top': '30px'}),

    ]),
    dbc.Row([
        dbc.Col([
            generate_predict_layout(),
        ], width=12, style={'margin-top': '30px'}),

    ]),

], style={"height": "170vh", }, )])


@callback(
    Output(component_id='predict_cards', component_property='children'),
    Output(component_id='watchlist_cards', component_property='children'),
    Input(component_id='submit', component_property='n_clicks'),
    State(component_id='userid', component_property='value'),
    State(component_id='k', component_property='value'),
)
def show(n_clicks, userid, k):
    if n_clicks is None or n_clicks == 0:
        # If no click event or initial load, return the current watchlist cards
        return dash.no_update

    # Fetch the list of movies the user has rated
    item_list = user_rated_movies(userid)
    n = len(item_list)

    # Generate cards for the user's watchlist
    new_watchlist_cards = []
    for i in range(n):
        movie_info = item_list[i]
        poster_url = scrape_movie_poster(movie_info[1])
        new_watchlist_cards.append(
            dbc.Card(
                className="mb-3",
                style={"height": '250px', "maxWidth": "470px", "backgroundColor": "#1f1f29", "borderRadius": "10px",
                       **(card_margin_right if i < 2 else {})},
                children=[
                    dbc.CardBody(
                        [
                            html.Div(
                                className="g-0 d-flex",
                                children=[
                                    dbc.Col(
                                        html.Img(
                                            src=poster_url,
                                            className="img-fluid rounded-start",
                                        ),
                                        className="col-md-4"
                                    ),
                                    dbc.Col(
                                        dbc.CardBody(
                                            [
                                                html.H4(
                                                    movie_info[1],
                                                    className="card-title mb-3",
                                                    style={"color": "white", "white-space": "pre-wrap"}
                                                ),
                                                html.P([
                                                    html.I(className="fa fa-star text-warning md-5",
                                                           style={"color": "gold"}),
                                                    f"  {movie_info[3]}"
                                                ], style={'color': '#F4BD61'}),
                                                html.P([
                                                    movie_info[2]
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
        )

    # Generate cards for recommended movies
    list_recommendations = user_recommends(userid)
    new_recommendation_cards = []
    for i in range(k):
        poster_url = scrape_movie_poster(list_recommendations[i][5])  # Fetch poster URL dynamically
        new_recommendation_cards.append(
            dbc.Card(
                className="mb-3",
                style={"height": '250px', "maxWidth": "470px", "backgroundColor": "#1f1f29", "borderRadius": "10px",
                       **(card_margin_right if i < 2 else {})},
                children=[
                    dbc.CardBody(
                        [
                            html.Div(
                                className="g-0 d-flex",
                                children=[
                                    dbc.Col(
                                        html.Img(
                                            src=poster_url,  # Use dynamically fetched poster URL
                                            className="img-fluid rounded-start",
                                        ),
                                        className="col-md-4"
                                    ),
                                    dbc.Col(
                                        dbc.CardBody(
                                            [
                                                html.H4(
                                                    list_recommendations[i][5],
                                                    className="card-title mb-3",
                                                    style={"color": "white", "white-space": "pre-wrap"}
                                                ),
                                                html.P([
                                                    list_recommendations[i][6]
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
        )

    return new_recommendation_cards, new_watchlist_cards
