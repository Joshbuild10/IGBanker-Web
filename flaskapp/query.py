from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)

bp = Blueprint('query', __name__, url_prefix='/query')

@bp.route('/', methods=('GET', 'POST'))
def query():
    if request.method == 'GET':
        return render_template('query/query.html')
    elif request.method == 'POST':
        return render_template('query/query.html')
    else:
        flash("Invalid request method.")