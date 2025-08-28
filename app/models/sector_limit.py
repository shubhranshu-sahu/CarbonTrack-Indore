from app import db

class SectorLimit(db.Model):
    __tablename__ = 'sector_limits'

    id = db.Column(db.Integer, primary_key=True)
    business_type = db.Column(db.String(100), nullable=False)
    sector = db.Column(db.String(100), nullable=False)
    msme_category = db.Column(db.String(10), nullable=False)  # Micro/Small/Medium
    yearly_limit_tco2 = db.Column(db.Float, nullable=False)
    last_updated = db.Column(db.Date, nullable=False)
