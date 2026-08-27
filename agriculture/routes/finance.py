"""
Finance, Credit Scoring, and Valuation routes.
"""

import json
from datetime import datetime, timezone
from flask import render_template, request, jsonify
from flask_login import login_required, current_user
from models import db, Farm, LivestockAsset, CropAsset, VisionScan, MarketplaceListing, MarketplaceOffer
from agriculture import agriculture_bp


def calculate_credit_score(user_id):
    """Calculate an explainable credit score for a farmer."""
    farms = Farm.query.filter_by(owner_id=user_id).all()
    farm_ids = [f.id for f in farms]

    if not farm_ids:
        return {
            'score': 300,
            'band': 'LOW',
            'factors': [{'name': 'No Farms Registered', 'contribution': 0,
                         'explanation': 'Register a farm to start building your profile.'}]
        }

    factors = []
    total_score = 300  # base

    # Factor 1: Verified Livestock Assets
    livestock_count = LivestockAsset.query.filter(
        LivestockAsset.farm_id.in_(farm_ids)
    ).count()
    verified_count = LivestockAsset.query.filter(
        LivestockAsset.farm_id.in_(farm_ids),
        LivestockAsset.verification_status == 'ai_estimated'
    ).count()
    livestock_score = min(150, (livestock_count * 10) + (verified_count * 15))
    total_score += livestock_score
    factors.append({
        'name': 'Livestock Assets',
        'contribution': livestock_score,
        'explanation': f'{livestock_count} animals registered, {verified_count} AI-verified.'
    })

    # Factor 2: Crop Activity
    crop_count = CropAsset.query.filter(CropAsset.farm_id.in_(farm_ids)).count()
    crop_score = min(100, crop_count * 20)
    total_score += crop_score
    factors.append({
        'name': 'Crop Activity',
        'contribution': crop_score,
        'explanation': f'{crop_count} crop assets registered.'
    })

    # Factor 3: Scan History
    scan_count = VisionScan.query.filter_by(user_id=user_id).count()
    scan_score = min(100, scan_count * 10)
    total_score += scan_score
    factors.append({
        'name': 'Verified Scans',
        'contribution': scan_score,
        'explanation': f'{scan_count} AI scans performed.'
    })

    # Factor 4: Marketplace Activity
    listing_count = MarketplaceListing.query.filter_by(seller_id=user_id).count()
    sold_count = MarketplaceListing.query.filter_by(seller_id=user_id, status='sold').count()
    marketplace_score = min(100, (listing_count * 10) + (sold_count * 25))
    total_score += marketplace_score
    factors.append({
        'name': 'Marketplace Activity',
        'contribution': marketplace_score,
        'explanation': f'{listing_count} listings, {sold_count} completed sales.'
    })

    # Factor 5: Farm Consistency
    farm_score = min(100, len(farms) * 30)
    total_score += farm_score
    factors.append({
        'name': 'Farm Registration',
        'contribution': farm_score,
        'explanation': f'{len(farms)} farms registered and active.'
    })

    total_score = min(850, total_score)

    if total_score >= 700:
        band = 'EXCELLENT'
    elif total_score >= 600:
        band = 'GOOD'
    elif total_score >= 450:
        band = 'FAIR'
    else:
        band = 'LOW'

    return {
        'score': total_score,
        'band': band,
        'factors': factors,
        'disclaimer': 'This is an agricultural risk indicator, not a guaranteed credit decision.'
    }


def calculate_valuation(animal):
    """Estimate livestock value."""
    species_prices = {
        'cattle': 25000,
        'goats': 4000,
        'sheep': 3500,
        'pigs': 8000,
        'poultry': 350
    }
    base_price = species_prices.get(animal.species, 5000)

    weight_factor = (animal.estimated_weight_kg or 200) / 200
    age_factor = max(0.5, 1.0 - ((animal.age or 3) * 0.05))
    health_factor = 1.0 if animal.health_status == 'healthy' else 0.8

    value = base_price * weight_factor * age_factor * health_factor
    return round(value, 2)


@agriculture_bp.route('/finance')
@login_required
def finance_dashboard():
    credit = calculate_credit_score(current_user.id)

    farms = Farm.query.filter_by(owner_id=current_user.id).all()
    farm_ids = [f.id for f in farms]

    total_valuation = 0
    if farm_ids:
        animals = LivestockAsset.query.filter(LivestockAsset.farm_id.in_(farm_ids)).all()
        for a in animals:
            a.valuation_amount = calculate_valuation(a)
            total_valuation += a.valuation_amount
        db.session.commit()

    listings_sold = MarketplaceListing.query.filter_by(
        seller_id=current_user.id, status='sold'
    ).count()

    eligible_range = {
        'min': round(credit['score'] * 10, 2),
        'max': round(credit['score'] * 50, 2)
    }

    return render_template('finance.html',
                           credit=credit,
                           total_valuation=round(total_valuation, 2),
                           eligible_range=eligible_range,
                           listings_sold=listings_sold)


@agriculture_bp.route('/api/finance/score')
@login_required
def api_credit_score():
    return jsonify({'success': True, 'data': calculate_credit_score(current_user.id)})


@agriculture_bp.route('/api/finance/valuation/<int:animal_id>')
@login_required
def api_valuation(animal_id):
    animal = LivestockAsset.query.get_or_404(animal_id)
    if animal.owner_id != current_user.id:
        return jsonify({'success': False, 'error': {'message': 'Access denied'}}), 403

    value = calculate_valuation(animal)
    animal.valuation_amount = value
    db.session.commit()

    return jsonify({
        'success': True,
        'data': {
            'asset_id': animal.id,
            'species': animal.species,
            'breed': animal.breed,
            'estimated_weight_kg': animal.estimated_weight_kg,
            'valuation_amount': value,
            'currency': 'ZAR',
            'methodology': 'Weight-based with age and health adjustments'
        }
    })
