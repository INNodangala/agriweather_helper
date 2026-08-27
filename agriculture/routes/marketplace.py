"""
Marketplace routes.
"""

from datetime import datetime, timezone
from flask import render_template, request, jsonify, redirect, url_for, flash
from flask_login import login_required, current_user
from models import db, MarketplaceListing, MarketplaceOffer, LivestockAsset
from agriculture import agriculture_bp


@agriculture_bp.route('/marketplace')
def marketplace():
    page = request.args.get('page', 1, type=int)
    category = request.args.get('category', '')
    species = request.args.get('species', '')
    search = request.args.get('search', '')

    query = MarketplaceListing.query.filter_by(status='active')

    if category:
        query = query.filter_by(category=category)
    if species:
        query = query.filter(MarketplaceListing.description.ilike(f'%{species}%'))
    if search:
        query = query.filter(
            db.or_(
                MarketplaceListing.title.ilike(f'%{search}%'),
                MarketplaceListing.description.ilike(f'%{search}%')
            )
        )

    listings = query.order_by(MarketplaceListing.created_at.desc())\
        .paginate(page=page, per_page=12, error_out=False)

    return render_template('marketplace.html',
                           listings=listings,
                           category=category,
                           species=species,
                           search=search)


@agriculture_bp.route('/marketplace/<int:listing_id>')
def listing_detail(listing_id):
    listing = MarketplaceListing.query.get_or_404(listing_id)
    offers = MarketplaceOffer.query.filter_by(listing_id=listing.id)\
        .order_by(MarketplaceOffer.created_at.desc()).all()
    return render_template('listing_detail.html',
                           listing=listing, offers=offers)


@agriculture_bp.route('/marketplace/new', methods=['GET', 'POST'])
@login_required
def listing_new():
    if request.method == 'POST':
        listing = MarketplaceListing(
            seller_id=current_user.id,
            farm_id=request.form.get('farm_id', type=int),
            asset_id=request.form.get('asset_id', type=int),
            asset_type=request.form.get('asset_type', 'livestock'),
            category=request.form.get('category', ''),
            title=request.form.get('title', '').strip(),
            description=request.form.get('description', '').strip(),
            quantity=request.form.get('quantity', type=float),
            unit=request.form.get('unit', ''),
            asking_price=request.form.get('asking_price', type=float),
            currency='ZAR',
            location=request.form.get('location', '').strip(),
            verified_weight=request.form.get('verified_weight', type=float),
            verified_grade=request.form.get('verified_grade', ''),
            verification_badge='AI WEIGHT VERIFIED' if request.form.get('verified_weight') else None
        )
        db.session.add(listing)
        db.session.commit()
        flash('Listing created!', 'success')
        return redirect(url_for('agriculture.listing_detail', listing_id=listing.id))

    from models import Farm
    farms = Farm.query.filter_by(owner_id=current_user.id).all()
    livestock = LivestockAsset.query.filter_by(owner_id=current_user.id).all()
    return render_template('listing_form.html', farms=farms, livestock=livestock)


@agriculture_bp.route('/marketplace/<int:listing_id>/offer', methods=['POST'])
@login_required
def make_offer(listing_id):
    listing = MarketplaceListing.query.get_or_404(listing_id)
    if listing.seller_id == current_user.id:
        flash('Cannot offer on your own listing.', 'danger')
        return redirect(url_for('agriculture.listing_detail', listing_id=listing_id))

    offer = MarketplaceOffer(
        listing_id=listing.id,
        buyer_id=current_user.id,
        amount=request.form.get('amount', type=float),
        message=request.form.get('message', '').strip(),
        status='pending'
    )
    db.session.add(offer)
    db.session.commit()
    flash('Offer submitted!', 'success')
    return redirect(url_for('agriculture.listing_detail', listing_id=listing_id))


@agriculture_bp.route('/api/marketplace/<int:listing_id>/offers/<int:offer_id>/respond', methods=['POST'])
@login_required
def api_respond_offer(listing_id, offer_id):
    listing = MarketplaceListing.query.get_or_404(listing_id)
    if listing.seller_id != current_user.id:
        return jsonify({'success': False, 'error': {'message': 'Access denied'}}), 403

    offer = MarketplaceOffer.query.get_or_404(offer_id)
    data = request.get_json() or {}
    action = data.get('action', '')

    if action == 'accept':
        offer.status = 'accepted'
        listing.status = 'sold'
    elif action == 'reject':
        offer.status = 'rejected'
    else:
        return jsonify({'success': False, 'error': {'message': 'Invalid action'}}), 400

    db.session.commit()
    return jsonify({'success': True, 'data': {'status': offer.status}})
