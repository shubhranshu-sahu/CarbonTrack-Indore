from app import db
from sqlalchemy import TIMESTAMP

class Emission(db.Model):
    __tablename__ = 'emissions'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete="CASCADE"), nullable=False)

    category = db.Column(db.String(50), nullable=False)       # Main category
    sub_type = db.Column(db.String(50), nullable=False)       # e.g., Diesel
    value = db.Column(db.Float, nullable=False)               # Quantity entered
    unit = db.Column(db.String(20), nullable=False)           # Unit (L, kg, kWh, etc.)
    emission = db.Column(db.Float, nullable=False)            # Calculated CO₂ (in kg)
    date = db.Column(db.Date, nullable=False)                 # No default, matches DB


    created_at = db.Column(TIMESTAMP, server_default=db.func.current_timestamp())
    updated_at = db.Column(TIMESTAMP, server_default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())

