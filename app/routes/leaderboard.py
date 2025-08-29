from flask import Blueprint, render_template, request, session, redirect, url_for, flash , jsonify

from functools import wraps


leaderboard_bp = Blueprint('leaderboard', __name__)




def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash("Login required", "warning")
            return redirect(url_for('auth.login', next=request.path))
        return f(*args, **kwargs)
    return decorated_function


@leaderboard_bp.route('/leaderboard')
@login_required
def leaderboard():
    return render_template('leaderboard.html')
