from flask import Blueprint, render_template, request, session, redirect, url_for, flash , jsonify

from functools import wraps


community_bp = Blueprint('community', __name__)




def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash("Login required", "warning")
            return redirect(url_for('auth.login', next=request.path))
        return f(*args, **kwargs)
    return decorated_function

@community_bp.route('/community')
@login_required
def community():
    return render_template('community.html')
