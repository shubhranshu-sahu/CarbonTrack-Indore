from app import db
from passlib.hash import pbkdf2_sha256 as hasher

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    business_name = db.Column(db.String(100), nullable=False)
    owner_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)

    msme_category = db.Column(db.String(10), nullable=False)  # Micro / Small / Medium
    business_type = db.Column(db.String(100), nullable=False)
    sector = db.Column(db.String(100), nullable=False)

    annual_turnover = db.Column(db.Float, nullable=True)
    location = db.Column(db.String(150), nullable=True)
    contact_number = db.Column(db.String(15), nullable=True)
    registration_number = db.Column(db.String(50), nullable=True)

    created_at = db.Column(
        db.DateTime,
        nullable=True,
        server_default=db.text('CURRENT_TIMESTAMP')  # Matches MySQL exactly
    )

    def verify_password(self, input_password):
        return hasher.verify(input_password, self.password)
