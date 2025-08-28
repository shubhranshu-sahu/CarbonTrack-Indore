from app import db
from datetime import date

class Emission(db.Model):
    __tablename__ = 'emissions'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    category = db.Column(db.String(50), nullable=False)   # Main category
    sub_type = db.Column(db.String(50), nullable=False)   # e.g., Diesel
    value = db.Column(db.Float, nullable=False)           # Quantity entered
    unit = db.Column(db.String(20), nullable=False)       # Unit (L, kg, kWh, etc.)
    emission = db.Column(db.Float, nullable=False)        # Calculated CO₂ (in kg)
    date = db.Column(db.Date, default=date.today, nullable=False)

    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, server_default=db.func.now(), onupdate=db.func.now())

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
