from flask import Flask, g, url_for, redirect, render_template
import sqlite3
import logging
from flask_login import LoginManager, UserMixin
from time import strftime
from routes.author import author_bp  # type: ignore
from routes.general import general_bp  # type: ignore
from routes.publications import publication_bp # type: ignore
from routes.utils import User

# logger = logging.getLogger()
# fileHandler = logging.FileHandler(
#     filename="logs/"+strftime("%Y%m%d-%H%M%S")+"-flask.log", mode="at", )
# fileHandler.setFormatter(fmt=logging.Formatter(
#     '%(asctime)s %(name)-40s %(levelname)-8s %(message)s'))
# fileHandler.setLevel(logging.DEBUG)
# logger.addHandler(fileHandler)

# streamHandler = logging.StreamHandler()
# streamHandler.setLevel(logging.DEBUG)
# logger.addHandler(streamHandler)

# werkzeug_logger = logging.getLogger('werkzeug')
# werkzeug_logger.addHandler(fileHandler)
# werkzeug_logger.setLevel(logging.DEBUG)

app = Flask(__name__, instance_relative_config=False)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "general.login" # type: ignore

@login_manager.user_loader
def loader_user(user_id):
    data = g.db.cursor().execute("""SELECT * FROM "App_user_list" WHERE id = ?""", (user_id,)).fetchone()
    if data:
        return User(*data)
    return None


app.register_blueprint(author_bp, url_prefix="")
app.register_blueprint(general_bp, url_prefix="")
app.register_blueprint(publication_bp, url_prefix="")

# @app.errorhandler(Exception)
# def handle_exception(error): # pylint: disable=unused-argument
#     # Log the error
#     # logger.exception("Unhandled exception:", exc_info=True)
#     return render_template("404.html.j2", wats={"type":"Error", "id":error})


def connect_db():
    return sqlite3.connect('databases/joint_database.db')


@app.before_request
def before_request():
    g.db = connect_db()


@app.teardown_request
def teardown_request(exception): # pylint: disable=unused-argument
    db = getattr(g, 'db', None)
    if db is not None:
        db.close()

def has_no_empty_params(rule):
    defaults = rule.defaults if rule.defaults is not None else ()
    arguments = rule.arguments if rule.arguments is not None else ()
    return len(defaults) >= len(arguments)

    # @app.route("/sitemap")
    # def site_map():
    #     links = []
    #     for rule in app.url_map.iter_rules():
    #         # Filter out rules we can't navigate to in a browser
    #         # and rules that require parameters
    #         if "GET" in rule.methods:
    #             url = url_for(rule.endpoint, **(rule.defaults or {}))
    #             links.append((url, rule.endpoint))
    #             # links.append(rule.endpoint)
    #     # links is now a list of url, endpoint tuples
    #     return links

if __name__ == "__main__":
    app.run()
