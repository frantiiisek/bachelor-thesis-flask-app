from math import ceil
from flask import request, render_template, g, Blueprint, redirect, flash
from flask_login import LoginManager, login_user, logout_user, login_required
from plotly.utils import PlotlyJSONEncoder
import plotly.express as px
import json
from .utils import _dea_model_reader, _list_of_dea_models, User, map_data_labels
import pandas as pd
import numpy as np


general_bp = Blueprint("general", __name__)

@general_bp.route('/search')
@login_required
def search():
    query = request.args.get('query', "").lower()
    where = request.args.get("where", "")
    method = request.args.get("method", "")
    page = int(request.args.get("page", 1))
    cursor = g.db.cursor()
    per_page = 50
    print(f"{repr(query)}")

    # Filter data based on the search query
    if method == "begins":
        search_query = query + "%"
    elif method == "contains":
        search_query = "%"+query+"%"
    else:
        raise NotImplementedError

    if where == "authors":
        results = cursor.execute(
            """SELECT person_name, person_id, person_dept 
            FROM persons 
            WHERE person_name_norm LIKE ? AND person_dept NOT NULL
            ORDER BY person_name""",
            (search_query,)
        ).fetchall()
        heading = "Search results"
    elif where == "publications":
        print("test")
        results = cursor.execute(
            """SELECT publ_title, publ_id, publ_year 
            FROM publications 
            WHERE publ_title LIKE ? 
            ORDER BY publ_title""",
            (search_query,)
        ).fetchall()
        heading = "Search results"
    else:
        return render_template('404.html.j2')
    return render_template(
        'search.html.j2',
        wats=results[(page-1)*per_page:page*per_page],
        heading=heading,
        page=page, max_pages=ceil((len(results)/per_page)),
        where=where, query=query, method=method
    )

@general_bp.route('/')
@general_bp.route('/index')
def home():
    # TODO add summary, some stats on all data, ...
    dea_toc = _list_of_dea_models()
    return render_template('index.html.j2', dea_toc=dea_toc)

@general_bp.route('/login', methods=['GET', 'POST'])
def login():
    # If a post request was made, find the user by 
    # filtering for the username
    if request.method == "POST":
        data = g.db.cursor().execute("""SELECT * FROM "App_user_list" WHERE username = ?""", (request.form.get("username"),)).fetchone()
        user = User(*data) if data else None
        # Check if the password entered is the 
        # same as the user's password
        if user and user.password == request.form.get("password"):
            # Use the login_user method to log in the user
            login_user(user)
            flash('Logged in successfully.')
            if (next_page := request.args.get("next")):
                return redirect(next_page)
            return redirect("/index")
        # Redirect the user back to the home
        # (we'll create the home route in a moment)
    return render_template("login.html.j2")

@general_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash('Logged out successfully.')
    return redirect("/index")

@general_bp.route('/dea')
@login_required
def dea():
    path = request.args.get('path', "")
    x = request.args.get('x', "credit_student")
    y = request.args.get('y', "scholar")
    x_scale = request.args.get("x_scale", False) == "True"
    y_scale = request.args.get("y_scale", False) == "True"
    person_id = request.args.get("person_id")

    dea_data = pd.read_csv(open(f"model_data/{path}.csv", "rt", encoding="utf-8"))
    dea_data["eff"] = np.round(dea_data["eff"], 2)
    dea_data["window"] = dea_data["window"].apply(lambda x: f"{2023 - 3*x - 2}-{2023 - 3*x}")
    dea_data["Title"] = dea_data["pay_grade"].apply(lambda x: {1.0:"Assistant professor", 1.2:"Associate professor", 1.4:"Full professor"}[x])
    dea_data["size"] = dea_data["eff"]
    dea_data.loc[dea_data["eff"]<10,"size"] = 11 - dea_data.loc[dea_data["eff"]<10, "eff"]
    dea_data.loc[dea_data["eff"]>=10, "size"] = 1
    dea_data["size"] = dea_data["size"]
    dea_data.loc[dea_data["size"].isna(), "size"] = 1

    figure = px.scatter(
        dea_data,
        x=x, y=y,
        color="Title",
        log_x=x_scale, log_y=y_scale,
        symbol="Title",
        hover_data={"eff":True, "person_id":True, "window":True, "Title":True, "pay_grade":False},
        custom_data=np.stack((dea_data["person_id"], dea_data["window"], dea_data["Title"], dea_data["eff"]), axis=0),
        size=dea_data["size"].to_list(),
        opacity=0.8,
        render_mode="svg",
        labels={
            x:map_data_labels.get(x, x),
            y:map_data_labels.get(y, y)
        },
    )
    figure.update_coloraxes(showscale=False)
    figure.update_traces(hovertemplate="<br>".join([
        "Person id: %{customdata[0]}",
        "Time window: %{customdata[1]}",
        "Title: %{customdata[2]}",
        "x: %{x}",
        "y: %{y}",
        "Efficiency: %{customdata[3]}",
    ]))
    figure_json = json.dumps(figure, cls=PlotlyJSONEncoder)

    dea_data["dept"] = dea_data.loc[:,[a.startswith("K") for a in dea_data.columns]].idxmax(axis=1)
    figure2 = px.box(
        dea_data,
        x="dept",
        y="eff",
        color="dept",
        notched=True,
        labels={
            "dept":"Department",
            "eff":"Efficiency",
        },
    )
    figure2.update_layout(yaxis_range=[0,10])
    figure2_json = json.dumps(figure2, cls=PlotlyJSONEncoder)

    descriptors = list(_list_of_dea_models("dict")[path].values()) + [x, y, path, str(x_scale), str(y_scale)]
    return render_template("dea.html.j2", wats=["g1", "vg1", figure_json], wats2=["g2", "vg2", figure2_json], descriptors=descriptors)


@general_bp.route('/px')
def express_test():
    df = px.data.medals_wide()
    fig1 = px.bar(x=np.arange(10_000)/100, y=np.sin(np.arange(10_000)/100), title="Wide-Form Input")
    graph1JSON = json.dumps(fig1, cls=PlotlyJSONEncoder)
    wats = ["g1", "vg1", graph1JSON]
    return render_template('plotlyexpress.html.j2', wats = wats)
