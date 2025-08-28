from flask import Blueprint, render_template, request, session, redirect, url_for, flash 

from functools import wraps

from app.models.user import User
from app.models.sector_limit import SectorLimit
from app.models.emmision import Emission

from datetime import datetime, date


from app import db
from passlib.hash import pbkdf2_sha256



from flask import abort



from app import db  # -----------------------> db only required and adding data to table , lile , db.session.add , db.session.commit() 
from sqlalchemy import extract, func

profile_bp = Blueprint('profile', __name__)



def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash("Login required", "warning")
            return redirect(url_for('auth.login', next=request.path))
        return f(*args, **kwargs)
    return decorated_function



@profile_bp.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    user_id = session.get("user_id")
    if not user_id:
        return redirect(url_for("auth.login"))

    user = User.query.get(user_id)

    if request.method == "POST":
        user.business_name = request.form.get("business_name", "").strip()
        user.owner_name = request.form.get("owner_name", "").strip()
        user.business_type = request.form.get("business_type", "").strip()
        user.sector = request.form.get("sector", "").strip()
        user.category = request.form.get("category", "").strip()

        try:
            db.session.commit()
            flash("Profile updated successfully.", "success")
        except Exception as e:
            db.session.rollback()
            flash("Error updating profile: " + str(e), "danger")

        return redirect(url_for("profile.profile"))

    return render_template("profile.html", user=user)



@profile_bp.route("/profile/change-password", methods=["POST"])
@login_required
def change_password():
    user_id = session.get("user_id")
    if not user_id:
        return redirect(url_for("auth.login"))

    user = User.query.get(user_id)

    old_pw = request.form.get("old_password")
    new_pw = request.form.get("new_password")
    confirm_pw = request.form.get("confirm_password")

    if not pbkdf2_sha256.verify(old_pw, user.password):
        flash("Incorrect old password.", "danger")
        return redirect(url_for("profile.profile"))

    if new_pw != confirm_pw:
        flash("New passwords do not match.", "danger")
        return redirect(url_for("profile.profile"))

    if len(new_pw) < 6:
        flash("New password must be at least 6 characters.", "danger")
        return redirect(url_for("profile.profile"))

    user.password = pbkdf2_sha256.hash(new_pw)
    db.session.commit()

    flash("Password updated successfully.", "success")
    return redirect(url_for("profile.profile"))
