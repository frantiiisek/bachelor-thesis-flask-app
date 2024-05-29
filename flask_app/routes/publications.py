from sqlite3 import Cursor
from flask import render_template, Blueprint, g, current_app, abort
from plotly.utils import PlotlyJSONEncoder
import plotly.express as px
import json
import pandas as pd


publication_bp = Blueprint("publication", __name__)

@publication_bp.route('/publication/<publ_index>/')
def publication(publ_index):
    cursor = g.db.cursor()
    wats={}
    wats["pub"] = cursor.execute(
        """ SELECT * FROM publications JOIN scholar_data ON publ_id = sch_publ_id WHERE publ_id = ?
        """, (publ_index,)).fetchone()
    a = cursor.execute("""SELECT a.*, p.person_name
FROM authorships AS a JOIN persons AS p ON auth_person_id = person_id WHERE auth_publ_id = ?""", (publ_index, )).fetchall()
    frame = pd.DataFrame(a, columns=["auth_index", "person_id", "publ_id", "Contribution", "Status", "Name"])
    if frame["Contribution"].sum()<100:
        frame.loc[-1] = [None, None, publ_index, 100 - frame["Contribution"].sum(), None, "Non-faculty member(s)"]
    wats["authors"] = frame.to_numpy().tolist()
    plot = px.pie(frame, "Name", "Contribution", title="Contribution of individual authors to the publication")
    wats["pie"] = ["p", "vp", json.dumps(plot, cls=PlotlyJSONEncoder)]

    return render_template("publication.html.j2", wats=wats)
