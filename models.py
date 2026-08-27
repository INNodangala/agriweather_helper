"""
Database models for AgriWeather Helper.
"""

from datetime import datetime, timezone
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()


class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    full_name = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(20))
    role = db.Column(db.String(20), nullable=False, default='farmer')  # farmer, buyer, lender
    location = db.Column(db.String(120))
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc),
                           onupdate=lambda: datetime.now(timezone.utc))

    farms = db.relationship('Farm', backref='owner', lazy='dynamic')
    livestock = db.relationship('LivestockAsset', backref='owner', lazy='dynamic')
    scans = db.relationship('VisionScan', backref='user', lazy='dynamic')
    listings = db.relationship('MarketplaceListing', backref='seller', lazy='dynamic')
    offers = db.relationship('MarketplaceOffer', backref='buyer', lazy='dynamic')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Farm(db.Model):
    __tablename__ = 'farms'

    id = db.Column(db.Integer, primary_key=True)
    owner_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    name = db.Column(db.String(120), nullable=False)
    location = db.Column(db.String(200))
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    farm_size = db.Column(db.Float)
    farm_size_unit = db.Column(db.String(10), default='hectares')
    soil_type = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc),
                           onupdate=lambda: datetime.now(timezone.utc))

    livestock = db.relationship('LivestockAsset', backref='farm', lazy='dynamic')
    crops = db.relationship('CropAsset', backref='farm', lazy='dynamic')
    scans = db.relationship('VisionScan', backref='farm', lazy='dynamic')
    listings = db.relationship('MarketplaceListing', backref='farm', lazy='dynamic')


class LivestockAsset(db.Model):
    __tablename__ = 'livestock_assets'

    id = db.Column(db.Integer, primary_key=True)
    farm_id = db.Column(db.Integer, db.ForeignKey('farms.id'), nullable=False, index=True)
    owner_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    species = db.Column(db.String(30), nullable=False)  # cattle, goats, sheep, pigs, poultry
    breed = db.Column(db.String(60))
    sex = db.Column(db.String(10))
    age = db.Column(db.Float)
    age_unit = db.Column(db.String(10), default='years')
    health_status = db.Column(db.String(30), default='healthy')
    estimated_weight_kg = db.Column(db.Float)
    weight_margin_kg = db.Column(db.Float)
    weight_confidence = db.Column(db.Float)
    valuation_amount = db.Column(db.Float)
    currency = db.Column(db.String(3), default='ZAR')
    verification_status = db.Column(db.String(20), default='unverified')
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc),
                           onupdate=lambda: datetime.now(timezone.utc))

    scans = db.relationship('VisionScan', backref='livestock', lazy='dynamic')


class CropAsset(db.Model):
    __tablename__ = 'crop_assets'

    id = db.Column(db.Integer, primary_key=True)
    farm_id = db.Column(db.Integer, db.ForeignKey('farms.id'), nullable=False, index=True)
    owner_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    crop_type = db.Column(db.String(60), nullable=False)
    variety = db.Column(db.String(60))
    area = db.Column(db.Float)
    area_unit = db.Column(db.String(10), default='hectares')
    planting_date = db.Column(db.Date)
    expected_harvest_date = db.Column(db.Date)
    health_status = db.Column(db.String(30), default='healthy')
    disease_status = db.Column(db.String(60))
    health_score = db.Column(db.Float)
    estimated_yield = db.Column(db.Float)
    yield_unit = db.Column(db.String(20))
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc),
                           onupdate=lambda: datetime.now(timezone.utc))


class VisionScan(db.Model):
    __tablename__ = 'vision_scans'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    farm_id = db.Column(db.Integer, db.ForeignKey('farms.id'), index=True)
    livestock_id = db.Column(db.Integer, db.ForeignKey('livestock_assets.id'), index=True)
    crop_id = db.Column(db.Integer, db.ForeignKey('crop_assets.id'), index=True)
    scan_type = db.Column(db.String(30), nullable=False)  # LIVESTOCK_WEIGHT, CROP_DISEASE, CROP_HEALTH
    image_reference = db.Column(db.String(500))
    model_name = db.Column(db.String(60))
    model_version = db.Column(db.String(20))
    result_json = db.Column(db.Text)
    confidence = db.Column(db.Float)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), index=True)
    synced_at = db.Column(db.DateTime)


class MarketplaceListing(db.Model):
    __tablename__ = 'marketplace_listings'

    id = db.Column(db.Integer, primary_key=True)
    seller_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    farm_id = db.Column(db.Integer, db.ForeignKey('farms.id'))
    asset_id = db.Column(db.Integer)
    asset_type = db.Column(db.String(20))  # livestock, crop
    category = db.Column(db.String(40), index=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    quantity = db.Column(db.Float)
    unit = db.Column(db.String(20))
    asking_price = db.Column(db.Float)
    currency = db.Column(db.String(3), default='ZAR')
    location = db.Column(db.String(200), index=True)
    status = db.Column(db.String(20), default='active', index=True)  # active, sold, withdrawn
    verified_weight = db.Column(db.Float)
    verified_grade = db.Column(db.String(20))
    verification_badge = db.Column(db.String(40))
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc),
                           onupdate=lambda: datetime.now(timezone.utc))

    offers = db.relationship('MarketplaceOffer', backref='listing', lazy='dynamic')


class MarketplaceOffer(db.Model):
    __tablename__ = 'marketplace_offers'

    id = db.Column(db.Integer, primary_key=True)
    listing_id = db.Column(db.Integer, db.ForeignKey('marketplace_listings.id'), nullable=False, index=True)
    buyer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    amount = db.Column(db.Float, nullable=False)
    currency = db.Column(db.String(3), default='ZAR')
    message = db.Column(db.Text)
    status = db.Column(db.String(20), default='pending')  # pending, accepted, rejected, cancelled, expired
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc),
                           onupdate=lambda: datetime.now(timezone.utc))


class AuditLog(db.Model):
    __tablename__ = 'audit_logs'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), index=True)
    action = db.Column(db.String(60), nullable=False)
    entity_type = db.Column(db.String(40))
    entity_id = db.Column(db.Integer)
    details = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
