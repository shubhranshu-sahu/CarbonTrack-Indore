from flask import Blueprint, render_template, request, session, redirect, url_for, flash , jsonify

from functools import wraps

from app.models.user import User
from app.models.sector_limit import SectorLimit
from app.models.emmision import Emission

from datetime import datetime, date




from flask import abort



from app import db  # -----------------------> db only required and adding data to table , lile , db.session.add , db.session.commit() 
from sqlalchemy import extract, func

summary_bp = Blueprint('summary', __name__)




def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash("Login required", "warning")
            return redirect(url_for('auth.login', next=request.path))
        return f(*args, **kwargs)
    return decorated_function



@summary_bp.route("/summary")
@login_required
def summary():

    user_id = session.get("user_id")
    now = datetime.now()

 #-----------------------------------------------------Top header cards  --------------------------------------------------------------------------------------------------------------------   

    # card 1 data 
    # Monthly Emission
    monthly_emission = db.session.query(func.sum(Emission.emission)).filter(
        Emission.user_id == user_id,
        extract('year', Emission.date) == now.year,
        extract('month', Emission.date) == now.month
    ).scalar() or 0.0

    #card 2 data 
    # Yearly Emission
    yearly_emission = db.session.query(func.sum(Emission.emission)).filter(
        Emission.user_id == user_id,
        extract('year', Emission.date) == now.year
    ).scalar() or 0.0

    #card 3 data 
    # Total Emission
    all_time_total_emission = db.session.query(func.sum(Emission.emission)).filter(
        Emission.user_id == user_id
    ).scalar() or 0.0
 #-------------------------------------------------------------------------------------------------------------------------------------------------------------------------   


 #-----------------------------------------------------Bar Plot --------------------------------------------------------------------------------------------------------------------   
    # Emission by Category
    category_data = (
        db.session.query(Emission.category, func.sum(Emission.emission))
        .filter(Emission.user_id == user_id)
        .group_by(Emission.category)
        .all()
    )

    categories = [row[0] for row in category_data]
    emissions = [round(row[1], 2) for row in category_data]

 #-------------------------------------------------------------------------------------------------------------------------------------------------------------------------   

    # Add this after the category-wise query


 #--------------------------------------------------------------Line-Plot for monthly trend -------------------------------------------------------------------------------------------------   

# Emission by Month (Current Year)
    monthly_data = (
        db.session.query(func.extract('month', Emission.date), func.sum(Emission.emission))
        .filter(Emission.user_id == user_id)
        .filter(func.extract('year', Emission.date) == now.year)
        .group_by(func.extract('month', Emission.date))
        .order_by(func.extract('month', Emission.date))
        .all()
    )

    # Prepare data
    month_labels = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    monthly_emissions = [0] * 12  # Initialize with zero

    for month_num, total_emission in monthly_data:
        monthly_emissions[int(month_num) - 1] = round(total_emission, 2)


 #-------------------------------------------------------------------------------------------------------------------------------------------------------------------------   

    years = db.session.query(extract('year', Emission.date)).distinct().all()
    years = sorted(set(int(y[0]) for y in years), reverse=True)

    months = {
        1: "January", 2: "February", 3: "March", 4: "April",
        5: "May", 6: "June", 7: "July", 8: "August",
        9: "September", 10: "October", 11: "November", 12: "December"
    }

  


  
    return render_template(
    'summary.html',
    monthly_emission=round(monthly_emission, 2),
    yearly_emission=round(yearly_emission, 2),
    total_emission=round(all_time_total_emission, 2),
    current_year=now.year,
    categories=categories,
    emissions=emissions,
    month_labels=month_labels,
    monthly_emissions=monthly_emissions,
            
            years=years,
            months=months,
            selected_year=now.year,
            selected_month=now.month

   
)


#--------------------------------------------------------for line chart - without reloading page ----------------------------------------------

@summary_bp.route("/summary/trend-data")
@login_required
def trend_data():
    user_id = session.get("user_id")
    year = int(request.args.get("year", datetime.now().year))

    monthly_data = (
        db.session.query(func.extract('month', Emission.date), func.sum(Emission.emission))
        .filter(Emission.user_id == user_id)
        .filter(func.extract('year', Emission.date) == year)
        .group_by(func.extract('month', Emission.date))
        .order_by(func.extract('month', Emission.date))
        .all()
    )

    month_labels = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                    'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    monthly_emissions = [0] * 12

    for month_num, total_emission in monthly_data:
        monthly_emissions[int(month_num) - 1] = round(total_emission, 2)

    return jsonify({
        "labels": month_labels,
        "data": monthly_emissions
    })
#-------------------------------------------------------------------------------------------------------------------------------------------------

@summary_bp.route("/summary/data")
@login_required
def summary_data():
    user_id = session["user_id"]
    view_type = request.args.get("type", "monthly")
    year = int(request.args.get("year", datetime.now().year))
    month = int(request.args.get("month", datetime.now().month))

    query = db.session.query(
        Emission.category,
        func.sum(Emission.emission)
    ).filter(Emission.user_id == user_id)

    if view_type == "monthly":
        query = query.filter(extract("year", Emission.date) == year,
                             extract("month", Emission.date) == month)
    elif view_type == "yearly":
        query = query.filter(extract("year", Emission.date) == year)

    query = query.group_by(Emission.category).all()

    labels = [row[0] for row in query]
    data = [round(row[1], 2) for row in query]

    return jsonify({"labels": labels, "data": data})