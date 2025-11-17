from config import db

class Parking(db.Model):
    __tablename__ = "parking"

    id = db.Column(db.Integer, primary_key=True)
    lat = db.Column(db.Float, nullable=False)
    lng = db.Column(db.Float, nullable=False)
    congestion = db.Column(db.String(20), nullable=True)
    ev_charge = db.Column(db.Boolean, default=False)
