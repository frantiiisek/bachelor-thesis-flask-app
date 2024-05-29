from sqlite3 import Cursor
from flask import render_template, Blueprint, g, current_app
import json
import plotly.express as px
import pandas as pd
from flask_login import UserMixin

def _dea_model_reader(path: str):
    return json.load(open(path, "rt", encoding="utf8"))

def _list_of_dea_models(return_type = "np"):
    if return_type=="np":
        frame = pd.read_json(open("model_data/toc.json", "rt", encoding="utf-8"), orient="index").reset_index()
        for a in frame.columns:
            if a in ["input", "output", "results"]:
                frame[a] = frame[a].map(lambda x: [{
                        "pay_grade":"Academic title",
                        "crossref":"Citation counts from Crossref",
                        "altmetric":"Citation counts from Altmetric",
                        "scholar":"Citation counts from Google Scholar",
                        "n_publications":"Number of publications participating on",
                        "studentCountAll":"Number of students teached",
                        "weighted_avg_ans":"Weighted average subject rating",
                        "credit_student":"Credit-students",
                        "unique_course_count":"Number of unique courses teached",
                        "hours_teached":"Number of hours teached",
                        "avg_contrib":"Contribution on the publications",
                        "eff":"Efficiency"
                    }.get(a, a) for a in x])
        return frame.to_numpy()
    if return_type=="dict":
        d = json.load(open("model_data/toc.json", "rt", encoding="utf-8"))
        for k,v in d.items():
            for kk, vv in v.items():
                if kk in ["input", "output", "results"]:
                    vv = [{
                        "pay_grade":["pay_grade", "Academic title"],
                        "crossref":["crossref", "Citation counts from Crossref"],
                        "altmetric":["altmetric", "Citation counts from Altmetric"],
                        "scholar":["scholar", "Citation counts from Google Scholar"],
                        "n_publications":["n_publications", "Number of publications participating on"],
                        "studentCountAll":["studentCountAll", "Number of students teached"],
                        "weighted_avg_ans":["weighted_avg_ans", "Weighted average subject rating"],
                        "credit_student":["credit_student", "Credit-students"],
                        "unique_course_count":["unique_course_count", "Number of unique courses teached"],
                        "hours_teached":["hours_teached", "Number of hours teached"],
                        "avg_contrib":["avg_contrib", "Contribution on the publications"],
                        "eff":["eff", "Efficiency"],
                        "efficiency":["efficiency", "Efficiency"]
                    }.get(x, [x,x]) for x in vv]
                    d[k][kk] = vv
        return d
    raise NotImplementedError

class User(UserMixin):
    def __init__(self, user_id, username, password):
        self.id = user_id
        self.username = username
        self.password = password  # In a real app, passwords should be hashed!

map_data_labels = {
    "pay_grade":"Academic title",
    "crossref":"Citation counts from Crossref",
    "altmetric":"Citation counts from Altmetric",
    "scholar":"Citation counts from Google Scholar",
    "n_publications":"Number of publications participating on",
    "studentCountAll":"Number of students teached",
    "weighted_avg_ans":"Weighted average subject rating",
    "credit_student":"Credit-students",
    "unique_course_count":"Number of unique courses teached",
    "hours_teached":"Number of hours teached",
    "avg_contrib":"Contribution on the publications",
    "eff":"Efficiency"
}
