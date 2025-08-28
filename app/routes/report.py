from flask import Blueprint, render_template, request, session, redirect, url_for, flash , send_file, abort, make_response

from functools import wraps

from app.models.user import User
from app.models.emmision import Emission

from datetime import datetime, date

from io import BytesIO
from sqlalchemy import func, extract

from collections import defaultdict

from xhtml2pdf import pisa

from flask import abort



from app import db  # -----------------------> db only required and adding data to table , lile , db.session.add , db.session.commit() 
from sqlalchemy import extract, func

report_bp = Blueprint('report', __name__)






def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash("Login required", "warning")
            return redirect(url_for('auth.login', next=request.path))
        return f(*args, **kwargs)
    return decorated_function




@report_bp.route("/report")
@login_required

def report():
    return render_template('report.html')






#--------------------------------------------------------------------------------------------------------------------



@report_bp.route("/report/download")
@login_required
def download_report():
    user_id = session.get("user_id")
    if not user_id:
        abort(403)

    try:
        start_str = request.args.get("start_date")
        end_str = request.args.get("end_date")
        start_date = datetime.strptime(start_str, "%Y-%m-%d")
        end_date = datetime.strptime(end_str, "%Y-%m-%d")
        # end_date = end_date.replace(hour=23, minute=59, second=59)  #------------------------------------------------------------------------------------
    except Exception:
        return "Invalid date format", 400

    if start_date > end_date:
        return "Start date cannot be after end date.", 400

    now = datetime.now()
    if end_date >= now:
        return "End date cannot be in the future.", 400

    emissions = Emission.query.filter(
        Emission.user_id == user_id,
        Emission.date >= start_date,
        Emission.date <= end_date
    ).all()

    total_emission = sum(e.emission for e in emissions)

    category_data = {}
    sub_category_data = {}
    for e in emissions:
        category_data[e.category] = category_data.get(e.category, 0) + e.emission
        key = f"{e.category} - {e.sub_type}"
        sub_category_data[key] = sub_category_data.get(key, 0) + e.emission

    # Convert dicts into lists of dicts for easier use in template
    category_emissions = [{"category": k, "total": round(v, 2)} for k, v in category_data.items()]

    subcategory_emissions_grouped = defaultdict(list)

    for full_key, total in sub_category_data.items():
        if " - " in full_key:
            cat, sub = full_key.split(" - ", 1)
            subcategory_emissions_grouped[cat].append({
                "sub_type": sub,
                "total": round(total, 2)
            })

    # Optional: sort subcategories alphabetically within each category
    for cat in subcategory_emissions_grouped:
        subcategory_emissions_grouped[cat].sort(key=lambda x: x["sub_type"])


    html = render_template("pdf_template.html",
                                total_emission=round(total_emission, 2),
                                start_date=start_str,
                                end_date=end_str,
                                generated_on=datetime.now().strftime("%Y-%m-%d %H:%M"),
                                category_emissions=category_emissions,
                                subcategory_emissions=subcategory_emissions_grouped )


    result = BytesIO()
    pisa_status = pisa.CreatePDF(src=html, dest=result)

    if pisa_status.err:
        return "Error generating PDF", 500

    result.seek(0)
    return send_file(result,
                     download_name="emission_report.pdf",
                     mimetype="application/pdf")
