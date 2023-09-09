from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for, send_file, current_app
)
from flaskapp.db import get_db
import tempfile
from flaskapp.queryHelper.merger import Merge
from flaskapp.queryHelper.querydb import queryDb


bp = Blueprint('query', __name__, url_prefix='/query')

@bp.route('/', methods=('GET', 'POST'))
def query():
    db = get_db()

    # Gets unique subject codes
    subject_codes = [subject_code[0] for subject_code in db.execute("SELECT DISTINCT subject_code FROM questions").fetchall()]
    # Gets unique exam boards
    exam_boards = [exam_board[0] for exam_board in db.execute("SELECT DISTINCT exam_board FROM questions").fetchall()]
    
    # Gets the column names of the database
    criterias = [column[1] for column in db.execute("PRAGMA table_info(questions)").fetchall()]

    # Removes subject code and exam board from column names to be used as criteria
    criterias.remove('subject_code')
    criterias.remove('exam_board')

    # Dictionary of column names and the base info
    info = {"criterias": criterias, "subjects": subject_codes, "boards": exam_boards}

    if request.method == 'GET':
        return render_template('query/query.html', info=info)
    
    elif request.method == 'POST':
        # Get the form data
        exam_board = request.form['board']
        subject = request.form['subject']
        criteria = request.form.getlist('criteria')
        search_string = request.form.getlist('search_string')
        similarity = request.form.getlist('similarity')

        # Pairs the elements of criteria, search string and similarity into a list of dictionaries
        # E.g [{'text': 'Topic', 'search_string': 'Topic 1', 'similarity': '0.8'}, {'criteria': 'year', 'search_string': '2017', 'similarity': '0.9'}]
        search_list = [{'criteria': c, 'search_string': s, 'similarity': sim} for c, s, sim in zip(criteria, search_string, similarity)]

        # Query the database
        matches = queryDb(db, {'exam_board': exam_board, 'subject_code': subject, 'conditions': search_list})

        # Merge the pdfs
        temp_file = Merge(matches, current_app.config['DATABASE']).mergePages()       
        
        return send_file(temp_file, mimetype='application/pdf', as_attachment=True, download_name='output.pdf')
    else:
        flash("Invalid request method.")