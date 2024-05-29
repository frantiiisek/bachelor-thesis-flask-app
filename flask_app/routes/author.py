from sqlite3 import Cursor
from flask import render_template, Blueprint, g, current_app
import json

author_bp = Blueprint("author", __name__)

@author_bp.route('/author/<pid>/')
def author(pid):
    kwargs: dict[str, dict] = {}
    cursor: Cursor = g.db.cursor()
    logger = current_app.logger

    person_data: tuple = cursor.execute(
        """SELECT person_id, person_name, person_dept, 
        CASE WHEN person_correct_scholar = 1 THEN person_scholar ELSE NULL END AS person_scholar, 
        person_orcid, 
        CASE WHEN person_correct_scholar = 1 THEN person_scholar_citedby ELSE NULL END AS person_scholar_citedby
        FROM persons WHERE person_id = ?""",
        (int(pid),)
    ).fetchone()

    if not person_data:
        return render_template("404.html.j2", wats={"type":"Author", "id":pid}), 404

    kwargs["person_data"] = dict(
        zip(
            ("pers_id", "pers_name", "dept" , "sch_id", "orc_id", "sch_cited"),
            person_data
        )
    )
    # links for orcid and scholar profiles

    # TODO: display timetable, preferably filterable
    # --> last two years
    # --> link to filterable table
    kwargs["summary"] = {}
    kwargs["summary"]["rows"] = list(map(lambda x: x[1:12], cursor.execute("SELECT * FROM Windowed_data WHERE person_id = ?", (int(pid),)).fetchall()))
    kwargs["summary"]["columns"] = [
        ["number", "Window"], ["number", "Average contribution to publications"], ["number", "Crossref citation count"],
        ["number", "Altmetric citation count"], ["number", "Google Scholar citation count"], ["number", "Number of publications participating on"],
        ["number", "Number of students teached"], ["number", "Weighted average subject rating"], ["number", "Credit-students"],
        ["number", "Number of unique courses teached"], ["number", "Number of hours teached"]
    ]
    kwargs["summary"]["name"] = "Sum_table"

    kwargs["timetables"] = {}
    kwargs["timetables"]["rows"] = cursor.execute(
        """ SELECT tbl_year, tbl_semester, tbl_code, tbl_subject, tbl_groups
        FROM timetables
        WHERE tbl_person_id = ? AND tbl_year >= 2020 ORDER BY tbl_year, tbl_semester DESC;""",
        (int(pid), )
    ).fetchall()
    kwargs["timetables"]["columns"] = [
        ["number", "Year"], ["string", "Semester"], ["string", "Subject code"], 
        ["string", "Subject name"], ["string", "Study groups"]
    ]
    kwargs["timetables"]["name"] = "Rozvrh"

    kwargs["publications"] = {}
    kwargs["publications"]["rows"] = cursor.execute(
        """SELECT publ_title, publ_year, publ_epc_new, COALESCE(sch_citations, ""), COALESCE(sch_id, ""), COALESCE(publ_doi, "")
        FROM publications 
        JOIN authorships ON publ_id = auth_publ_id
        JOIN scholar_data ON publ_id = sch_publ_id
        WHERE auth_person_id = ? AND publ_year > 2021
""", (pid, )).fetchall()
    kwargs["publications"]["columns"] = [
        ["string", "Title"], ["number", "Year"], ["string", "EPC category"], ["number", "Google Scholar citations"],
        ["string", "Google Scholar publication ID"], ["string", "DOI"]
    ]
    kwargs["publications"]["name"] = "pub_tab"
    print(kwargs["publications"])


    return render_template("author.html.j2", **kwargs)
