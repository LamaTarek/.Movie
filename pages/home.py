from dash import html, register_page  # , callback # If you need callbacks, import it here.
import dash
from dash import Dash, dcc, html, callback_context
import dash_bootstrap_components as dbc

register_page(
    __name__,
    name='.Movie',
    path='/'
)

def layout():
    layout = html.Div(
        style={"backgroundImage": "url('assets/ccgif.gif')", 'backgroundRepeat': 'no-repeat',
               'backgroundPositionY': '200px', 'backgroundPositionX': '750px'},
        id='homeLayout',
        children=[
            dbc.Container(html.Div(
                [
                    dbc.Row(
                        dbc.Col(
                            html.Div("Discover Your Next Favorite Movie",
                                     style={"margin-top": "200px", "font-size": "50px",
                                            "font-weight": "bold", "color": "white"}),  # Change font color here
                        )
                    ),
                    dbc.Row(
                        dbc.Col(
                            html.Div(
                                [
                                    "Navigate the vast world of cinema with ease. Our dashboard offers personalized movie recommendations, helping you uncover hidden gems and beloved classics perfectly suited to your tastes. "],
                                style={"margin-top": "50px", "margin-right": "45px", "font-size": "30px", "color": "white"}  # Change font color here
                            ),

                            width={"size": 9}
                        )
                    ),
                    dbc.Row(
                        dbc.Col(
                            dbc.NavLink(
                                dbc.Button("Let's Explore", outline=True, size='lg',
                                           style={"border-color": "#6A0000","color":"white" }, className="d-grid gap-2 dash-button"
                                           )

                                , href='/UserPage')
                            , style={"margin-top": "50px", "font-size": "30px", "width": "auto"},

                            width={"size": 5}
                        )
                    )], style={"height": "100vh", }, ))
        ]

    )
    return layout
