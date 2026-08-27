"""
Agriculture Dashboard routes.
"""

import json
from datetime import datetime, timezone
from flask import render_template, jsonify
from flask_login import login_required, current_user
from models import db, Farm, LivestockAsset, CropAsset, VisionScan, MarketplaceListing, MarketplaceOffer
from agriculture import agriculture_bp


@agriculture_bp.route('/dashboard')
@login_required
def dashboard():
    farms = Farm.query.filter_by(owner_id=current_user.id).all()

    total_livestock = 0
    total_biomass_kg = 0
    total_crop_area = 0
    active_listings = 0
    pending_offers = 0

    for farm in farms:
        livestock = LivestockAsset.query.filter_by(farm_id=farm.id).all()
        total_livestock += len(livestock)
        for animal in livestock:
            if animal.estimated_weight_kg:
                total_biomass_kg += animal.estimated_weight_kg

        crops = CropAsset.query.filter_by(farm_id=farm.id).all()
        for crop in crops:
            if crop.area:
                total_crop_area += crop.area

        active_listings += MarketplaceListing.query.filter_by(
            seller_id=current_user.id, farm_id=farm.id, status='active'
        ).count()

    pending_offers = MarketplaceOffer.query.join(MarketplaceListing).filter(
        MarketplaceListing.seller_id == current_user.id,
        MarketplaceOffer.status == 'pending'
    ).count()

    recent_scans = VisionScan.query.filter_by(user_id=current_user.id)\
        .order_by(VisionScan.created_at.desc()).limit(5).all()

    return render_template('dashboard.html',
                           farms=farms,
                           total_livestock=total_livestock,
                           total_biomass_kg=round(total_biomass_kg, 1),
                           total_crop_area=round(total_crop_area, 2),
                           active_listings=active_listings,
                           pending_offers=pending_offers,
                           recent_scans=recent_scans)


@agriculture_bp.route('/api/dashboard')
@login_required
def api_dashboard():
    farms = Farm.query.filter_by(owner_id=current_user.id).all()
    farm_ids = [f.id for f in farms]

    total_livestock = LivestockAsset.query.filter(
        LivestockAsset.farm_id.in_(farm_ids)
    ).count() if farm_ids else 0

    total_crop_area = db.session.query(db.func.sum(CropAsset.area)).filter(
        CropAsset.farm_id.in_(farm_ids)
    ).scalar() or 0

    active_listings = MarketplaceListing.query.filter_by(
        seller_id=current_user.id, status='active'
    ).count()

    return jsonify({
        'success': True,
        'data': {
            'farms': len(farms),
            'total_livestock': total_livestock,
            'total_crop_area': float(total_crop_area),
            'active_listings': active_listings
        }
    })
