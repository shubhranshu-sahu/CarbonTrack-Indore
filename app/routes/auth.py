from flask import Blueprint, render_template, request, session ,redirect, url_for, flash
from passlib.hash import pbkdf2_sha256 as hasher
from functools import wraps
from app.models.user import User

from app import db

auth_bp = Blueprint("auth",__name__)



@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        user = User.query.filter_by(email=email).first()

        if user and user.verify_password(password):
            session['user_id'] = user.id
            session['email'] = user.email
            next_page = request.form.get('next') or request.args.get('next')
            if next_page and next_page.startswith('/'):
                return redirect(next_page) ##############################################################################################################
            return redirect(url_for('main.dashboard'))

        else:
            
            flash("Invalid email or password.", "danger")  # 'danger' is Bootstrap class
            return redirect(url_for('auth.login'))  # redirect to show flash message

    return render_template("login.html")






@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        business_name = request.form.get("business_name")
        owner_name = request.form.get("owner_name")
        email = request.form.get("email")
        password = request.form.get("password")
        msme_category = request.form.get("msme_category")
        business_type = request.form.get("business_type")
        sector = request.form.get("sector")

        # Hash password
        hashed_pw = hasher.hash(password)

        # Check if email or username already exists
        if User.query.filter_by(email=email).first():
            return "Email already registered."
        

        new_user = User(business_name=business_name, email=email, password=hashed_pw, owner_name=owner_name,msme_category=msme_category, business_type=business_type ,sector=sector)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('auth.login'))

    return render_template("register.html")


# use post method for logout --------------- to avoid CSRF attack , and simply logging out via url 
# also make logout button in a form , so that you can send post request

@auth_bp.route("/logout", methods=["POST"])
def logout():
    if 'user_id' not in session:
        flash("You're not logged in.", "warning")
        return redirect(url_for('auth.login'))

    session.pop('user_id', None)
    session.pop('email', None)
    flash("You have been logged out.", "info")
    return redirect(url_for('main.welcome'))
