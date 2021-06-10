import dash
from flask import Flask, session, request, redirect, render_template, url_for, Blueprint
from flask.helpers import get_root_path
from flask_session import Session


from .config import BaseConfig


def create_app():
    sess = Session()
    server = Flask(__name__)
    server.config.from_object(BaseConfig)
    register_dashapps(server)
    register_blueprints(server)
    sess.init_app(server)

    return server

def register_dashapps(app):
    from .dashapp1.layout import layout
    from .dashapp1.callbacks import register_callbacks

    # Meta tags for viewport responsiveness
    meta_viewport = {"name": "viewport", "content": "width=device-width, initial-scale=1, shrink-to-fit=no"}
    external_stylesheets = ['css/main.css',
            {
                'href': 'https://use.fontawesome.com/releases/v5.8.1/css/all.css',
                'rel': 'stylesheet',
                'integrity': 'sha384-50oBUHEmvpQ+1lW4y57PTFmhCaXp0ML5d60M1M7uH2+nqUivzIebhndOJK28anvf',
                'crossorigin': 'anonymous'
            }
        ]
    dashapp1 = dash.Dash(__name__,
                         server=app,
                         url_base_pathname='/dashboard/',
                         external_stylesheets=external_stylesheets,
                        #  assets_folder=get_root_path(__name__) + '/dashboard/assets/',
                         meta_tags=[meta_viewport])

    with app.app_context():
        dashapp1.title = 'Mus-X'
        dashapp1.layout = layout
        register_callbacks(dashapp1)

    # _protect_dashviews(dashapp1)
    return dashapp1


def _protect_dashviews(dashapp):
    for view_func in dashapp.server.view_functions:
        if view_func.startswith(dashapp.config.url_base_pathname):
            dashapp.server.view_functions[view_func] = dashapp.server.view_functions[view_func]


def register_blueprints(server):
    from .webapp import server_bp

    server.register_blueprint(server_bp)
