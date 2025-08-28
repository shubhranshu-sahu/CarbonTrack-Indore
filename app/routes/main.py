from flask import Blueprint, render_template, request, session, redirect, url_for, flash , jsonify

from functools import wraps

from app.models.user import User
from app.models.sector_limit import SectorLimit
from app.models.emmision import Emission

from datetime import datetime, date, timedelta


from flask import abort

import os
import requests
# from openai import OpenAI  # ✅ This is correct for v1.0+
import json


from app import db  # -----------------------> db only required and adding data to table , lile , db.session.add , db.session.commit() 
from sqlalchemy import extract, func

main_bp = Blueprint('main', __name__)




def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash("Login required", "warning")
            return redirect(url_for('auth.login', next=request.path))
        return f(*args, **kwargs)
    return decorated_function



@main_bp.route("/")
def welcome():
    return render_template("welcome.html")



@main_bp.route("/dashboard")
@login_required
def dashboard():

    email = session.get('email')  # or user_id if stored
    user_id = session["user_id"]

    user = User.query.filter_by(email=email).first()

    if not user:
        return redirect(url_for('auth.logout'))  # fail-safe

    # Fetch carbon limit based on user’s sector/business/category
    limit = SectorLimit.query.filter_by(
        business_type=user.business_type,
        sector=user.sector,
        msme_category=user.msme_category
    ).first()


    today = date.today()

    # Current month and year
    current_month = today.month
    current_year = today.year

       # Total emission for current month
    monthly_emission = (
        db.session.query(func.sum(Emission.emission))
        .filter(
            Emission.user_id == user_id,
            extract("year", Emission.date) == current_year,
            extract("month", Emission.date) == current_month,
        )
        .scalar()
    ) or 0.0  # fallback if None

    # Total emission for current year
    yearly_emission = (
        db.session.query(func.sum(Emission.emission))
        .filter(
            Emission.user_id == user_id,
            extract("year", Emission.date) == current_year,
        )
        .scalar()
    ) or 0.0



    carbon_limit = limit.yearly_limit_tco2

    monthly_limit = (carbon_limit * 1000) / 12  # in kg
    status = "Under Limit"
    status_class = "success"

    if yearly_emission > carbon_limit * 1000:
        status = "Over Limit"
        status_class = "danger"

    show_monthly_warning = monthly_emission > monthly_limit


#-----------------------------another section ------------------------------- 
    user_id = session["user_id"]
    filter_type = request.args.get("filter", "monthly")  # 'monthly' or 'yearly'
    
    current_date = datetime.now()
    current_year = current_date.year
    current_month = current_date.month

    if filter_type == "monthly":
        emission_value = (
            db.session.query(func.sum(Emission.emission))
            .filter(
                Emission.user_id == user_id,
                extract("year", Emission.date) == current_year,
                extract("month", Emission.date) == current_month,
            )
            .scalar()
        ) or 0.0
        emission_limit = monthly_limit  # 4 tons = 4000 kg
    else:  # yearly
        emission_value = (
            db.session.query(func.sum(Emission.emission))
            .filter(
                Emission.user_id == user_id,
                extract("year", Emission.date) == current_year,
            )
            .scalar()
        ) or 0.0
        emission_limit = carbon_limit*1000  # 50 tons = 50000 kg

    percent_used = round((emission_value / emission_limit) * 100, 1)




    return render_template(
        "dashboard.html",
        user=user,
        carbon_limit=carbon_limit,  # in tonnes
        yearly_emission=yearly_emission / 1000,  # convert to tCO2
        monthly_emission=monthly_emission / 1000,  # convert to tCO2
        monthly_limit=carbon_limit / 12,
        status=status,
        status_class=status_class,
        show_monthly_warning=show_monthly_warning,


        emission_value=round(emission_value, 2),
        emission_limit=emission_limit,
        percent_used=percent_used,
        filter_type=filter_type
    )



#------------------------------- Openrouter AI Suggestion Route ------------------------------------------------------------------------------------

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

headers = {
    "Authorization": f"Bearer {OPENROUTER_API_KEY}",
    "Content-Type": "application/json",
    "HTTP-Referer": "http://localhost:5000",  # Or your real URL later
    "X-Title": "CarbonTrack-AI"
}

@main_bp.route("/get_ai_suggestions")
@login_required
def get_ai_suggestions():
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 403

    start = datetime.now() - timedelta(days=30)
    emissions = Emission.query.filter(Emission.user_id == user_id,
                                      Emission.date >= start).all()
    if not emissions:
        return jsonify({"suggestions": [
            "No recent data. Log some activities!",
            "Try to add electricity or travel data.",
            "Tracking helps you improve.",
            "Stay consistent to see trends."
        ]})

    cat_totals = {}
    for e in emissions:
        cat_totals[e.category] = cat_totals.get(e.category, 0) + e.emission
    summary = "\n".join(f"{c}: {round(v, 2)} kg CO₂" for c, v in cat_totals.items())

    prompt = f"""You are 'Carbon Coach 🤖🌱'. Based on the emissions:
{summary}

Suggest 4 easy, practical actions that a small business can take to reduce their carbon footprint. Provide them as a numbered list."""

    try:
        data = {
            "model": "mistralai/mistral-7b-instruct:free",
            "messages": [
                {"role": "system", "content": "You are Carbon Coach, an AI that helps businesses reduce carbon emissions."},
                {"role": "user", "content": prompt}
            ]
        }

        r = requests.post(OPENROUTER_URL, headers=headers, data=json.dumps(data))
        r.raise_for_status()
        response = r.json()

        reply = response["choices"][0]["message"]["content"]
        suggestions = [s.strip("0123456789. ") for s in reply.split("\n") if s.strip()]
        return jsonify({"suggestions": suggestions[:4]})
    except Exception as e:
        print("OpenRouter API error:", e)
        return jsonify({"suggestions": [
            "AI temporarily unavailable.",
            "Try again later.",
            "Check your API key or model.",
            "Contact support if it persists."
        ]})
#----------------------------------------------------------------------------------------------------------------------------------------------------------------------------


#------------------------------- OpenAI Suggestion Route ------------------------------------------------------------------------------------
 


# client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))  # You can use environment variable too

# @main_bp.route("/get_ai_suggestions")
# @login_required
# def get_ai_suggestions():
#     user_id = session.get("user_id")
#     if not user_id:
#         return jsonify({"error": "Unauthorized"}), 403

#     # Get emissions in last 30 days
#     start_date = datetime.now() - timedelta(days=30)
#     emissions = Emission.query.filter(
#         Emission.user_id == user_id,
#         Emission.date >= start_date
#     ).all()

#     if not emissions:
#         return jsonify({"suggestions": [
#             "We couldn't find any recent emission data.",
#             "Try logging your activities regularly.",
#             "Once you add some records, Carbon Coach will generate insights.",
#             "Reduce your footprint today by tracking energy and transport."
#         ]})

#     # Aggregate emissions by category
#     category_totals = {}
#     for e in emissions:
#         category_totals[e.category] = category_totals.get(e.category, 0) + e.emission

#     # Create a summary string
#     summary_lines = [f"{cat}: {round(total, 2)} kg CO₂" for cat, total in category_totals.items()]
#     summary_text = "\n".join(summary_lines)

#     # OpenAI Prompt
#     prompt = f"""
# You're an AI environmental assistant called 'Carbon Coach 🤖🌱'. Based on the following user's emissions from the last 30 days:

# {summary_text}

# Suggest 4 clear, practical, and MSME-friendly actions to reduce their carbon footprint. Respond as a numbered list, no extra intro or outro.
# """

#     try:
#         response = client.chat.completions.create(
#             model="gpt-3.5-turbo",
#             messages=[
#                 {"role": "system", "content": "You are a helpful environmental assistant."},
#                 {"role": "user", "content": prompt}
#             ],
#             max_tokens=300,
#             temperature=0.7
#         )

#         suggestions_raw = response.choices[0].message.content
#         suggestions = [s.strip() for s in suggestions_raw.split("\n") if s.strip()]
#         suggestions = suggestions[:4] if len(suggestions) >= 4 else suggestions

#         return jsonify({"suggestions": suggestions})

#     except Exception as e:
#         print("OpenAI error:", e)
#         return jsonify({"suggestions": [
#             "We encountered an issue generating suggestions.",
#             "Try again shortly or check your OpenAI setup.",
#             "Make sure your emissions are updated.",
#             "Contact support if the issue persists."
#         ]})

#-------------------------------------------------------------------------------------------------------------------



carbon_factors = {
    "Electricity": {
        "Electricity": 0.92  # kg CO₂ per kWh
    },
    "Fuel": {
        "Diesel": 2.68,   # kg CO₂ per liter
        "Petrol": 2.31,
        "LPG": 1.51       # kg CO₂ per kg
    },
    "Transport": {
        "Car": 0.12,      # kg CO₂ per km
        "Truck": 0.25,
        "Bus": 0.07
    },
    "Material": {
        "Steel": 1.85,    # kg CO₂ per kg
        "Plastic": 6.00,
        "Aluminum": 11.00
    },
    "Waste": {
        "Plastic Waste": 1.8,   # kg CO₂ per kg
        "Organic Waste": 0.5,
        "General Waste": 1.0
    }
}

def calculate_emission(category, sub_type, value):
    all_emission_factors = carbon_factors

    try:
        return round(value * all_emission_factors[category][sub_type], 2)
    except KeyError:
        return 0.0


 

@main_bp.route('/activities/add', methods=['POST'])
def add_activity():
    if 'user_id' not in session:
        flash("Please login first", "warning")
        return redirect(url_for('auth.login'))

    user_id = session['user_id']
    category = request.form.get('category')
    sub_type = request.form.get('sub_type')
    value = float(request.form.get('value'))
    unit = request.form.get('unit')
    date = request.form.get('date')

    # Calculate emission using factor
    try:
        factor = carbon_factors[category][sub_type]
        emission = round(value * factor, 2)
    except KeyError:
        flash("Invalid category or subtype", "danger")
        return redirect(url_for('main.activities'))

    # Store in DB
    new_entry = Emission(
        user_id=user_id,
        category=category,
        sub_type=sub_type,
        value=value,
        unit=unit,
        emission=emission,
        date=datetime.strptime(date, "%Y-%m-%d")
    )

    db.session.add(new_entry)
    db.session.commit()

    flash("Activity logged successfully!", "success")
    return redirect(url_for('main.activities'))
   


# @main_bp.route("/activities")
# @login_required
# def activities():
   

#     return render_template(
#         "activities.html"
#     )



#---------------------------------------------------------------------------------------------------------------------------------------------------------------------

@main_bp.route("/activities")
@login_required
def activities():
    # Ensure user is logged in
    if "user_id" not in session:
        return redirect(url_for("auth.login"))  # not needed , since already using login_req decorator , remove it later !!!

    user_id = session["user_id"]

    # Fetch recent 10 activities
    recent_emissions = (
                            Emission.query
                            .filter_by(user_id=user_id)
                            .order_by(Emission.created_at.desc())
                            .limit(10)
                            .all()
                        )

    # print("User ID:", user_id)
    # print("Emissions found:", recent_emissions)
    all_emissions = Emission.query.filter_by(user_id=user_id).order_by(Emission.date.desc()).all()

    now = datetime.now()
    monthly_count = Emission.query.filter_by(user_id=user_id)\
        .filter(Emission.date.between(datetime(now.year, now.month, 1), now)).count()

    total_count = Emission.query.filter_by(user_id=user_id).count()

    return render_template("activities.html", recent_emissions=recent_emissions , emissions=all_emissions,monthly_count=monthly_count, total_count=total_count)



@main_bp.route("/activities/delete/<int:activity_id>", methods=["POST"])
def delete_activity(activity_id):
    if "user_id" not in session:
        return redirect(url_for("login"))

    emission = Emission.query.get_or_404(activity_id)

    if emission.user_id != session["user_id"]:
        abort(403)

    db.session.delete(emission)
    db.session.commit()
    return redirect(request.referrer or url_for("activities"))


@main_bp.route("/activities/edit/<int:activity_id>", methods=["POST"])
def edit_activity(activity_id):
    if "user_id" not in session:
        return redirect(url_for("login"))

    emission = Emission.query.get_or_404(activity_id)

    if emission.user_id != session["user_id"]:
        abort(403)

    # Get form data
    emission.category = request.form.get("category")
    emission.sub_type = request.form.get("sub_type")
    emission.unit = request.form.get("unit")
    emission.value = float(request.form.get("value"))
    emission.date = request.form.get("date")

    # Recalculate emission
    emission.emission = calculate_emission(emission.category, emission.sub_type, emission.value)

    db.session.commit()
    return redirect(request.referrer or url_for("activities"))
