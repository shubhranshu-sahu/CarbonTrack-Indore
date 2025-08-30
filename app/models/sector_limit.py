from app import db

class SectorLimit(db.Model):
    __tablename__ = 'sector_limits'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    business_type = db.Column(db.String(100), nullable=True)
    sector = db.Column(db.String(100), nullable=True)
    msme_category = db.Column(
        db.Enum('Micro', 'Small', 'Medium', name='msme_category_enum'),
        nullable=True
    )
    yearly_limit_tco2 = db.Column(db.Integer, nullable=True)
    last_updated = db.Column(db.Date, nullable=True)
