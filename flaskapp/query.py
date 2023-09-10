from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for, send_file, current_app
)
from flaskapp.db import get_db
import tempfile
from flaskapp.queryHelper.merger import Merge
from flaskapp.queryHelper.querydb import queryDb
from flaskapp.queryHelper.form import queryForm, ValidationError

bp = Blueprint('query', __name__, url_prefix='/query')

@bp.route('/', methods=('GET', 'POST'))
def query():
    try:
        db = get_db()
    # If there is an error connecting to the database, log the error and flash a message
    except Exception as e:
        current_app.logger.error(e)
        flash("Error connecting to database. This is an issue with the server. Please try again later.")
        return render_template('query/query.html')

    # Gets unique subject codes
    subject_codes = [subject_code[0] for subject_code in db.execute("SELECT DISTINCT subject_code FROM questions").fetchall()]
    # Gets unique exam boards
    exam_boards = [exam_board[0] for exam_board in db.execute("SELECT DISTINCT exam_board FROM questions").fetchall()]
    
    # Gets the column names of the database
    filters = [column[1] for column in db.execute("PRAGMA table_info(questions)").fetchall()]

    # Removes subject code and exam board from column names to be used as filter
    filters.remove('subject_code')
    filters.remove('exam_board')

    # Dictionary of column names and the base info
    info = {"filters": filters, "subjects": subject_codes, "boards": exam_boards}

    if request.method == 'GET':
        return render_template('query/query.html', info=info)
    
    elif request.method == 'POST':
        # Get and validate form data
        try:
            exam_board, subject, filters, search_terms, matches = queryForm(request.form, info)
        # If there is an error validating the form, flash a message
        except ValidationError as e:
            print(e.message)
            flash(e.message)
            return render_template('query/query.html', info=info)

        # Pairs the elements of filter, search string and match into a list of dictionaries
        # E.g [{'text': 'Topic', 'search_term': 'Topic 1', 'match': '0.8'}, {'filter': 'year', 'search_term': '2017', 'match': '0.9'}]
        search_list = [{'filter': f, 'search_term': str, 'match': sim} for f, str, sim in zip(filters, search_terms, matches)]
        
        # Query the database
        matches = queryDb(db, {'exam_board': exam_board, 'subject_code': subject, 'conditions': search_list})

        if len(matches) == 0:
            flash("No results found.")
            return render_template('query/query.html', info=info)
        
        # Merge the pdfs
        try:
            temp_file, missingFiles = Merge(matches, current_app.config['DATABASE']).mergePages()

            # If an error was thrown and some files are missing
            if len(missingFiles):
                current_app.logger.error(f"Missing files: {missingFiles}")
                # flash("Some results may not have been returned, this is a server issue.")

            return send_file(temp_file, mimetype='application/pdf', as_attachment=True, download_name='output.pdf')
        # If there is an error merging the pdfs, flash a message
        except Exception as e:
            current_app.logger.error(e)
            flash("No matching questions found in database. Please try another search.")
            return render_template('query/query.html', info=info)
        
    else:
        flash("Invalid request method.")