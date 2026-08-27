"""
Farm and Asset routes.
"""

import json
from datetime import datetime, timezone
from flask import render_template, request, jsonify, redirect, url_for, flash
from flask_login import login_required, current_user
from models import db, Farm, LivestockAsset, CropAsset
from agriculture import agriculture_bp


@agriculture_bp.route('/farms')
@login_required
def farms_list():
    farms = Farm.query.filter_by(owner_id=current_user.id).order_by(Farm.created_at.desc()).all()
    return render_template('farms.html', farms=farms)


@agriculture_bp.route('/farms/new', methods=['GET', 'POST'])
@login_required
def farm_new():
    if request.method == 'POST':
        farm = Farm(
            owner_id=current_user.id,
            name=request.form.get('name', '').strip(),
            location=request.form.get('location', '').strip(),
            latitude=request.form.get('latitude', type=float),
            longitude=request.form.get('longitude', type=float),
            farm_size=request.form.get('farm_size', type=float),
            farm_size_unit=request.form.get('farm_size_unit', 'hectares'),
            soil_type=request.form.get('soil_type', '').strip()
        )
        db.session.add(farm)
        db.session.commit()
        flash('Farm created successfully!', 'success')
        return redirect(url_for('agriculture.farm_detail', farm_id=farm.id))

    return render_template('farm_form.html')


@agriculture_bp.route('/farms/<int:farm_id>')
@login_required
def farm_detail(farm_id):
    farm = Farm.query.get_or_404(farm_id)
    if farm.owner_id != current_user.id:
        flash('Access denied.', 'danger')
        return redirect(url_for('agriculture.farms_list'))

    livestock = LivestockAsset.query.filter_by(farm_id=farm.id)\
        .order_by(LivestockAsset.created_at.desc()).all()
    crops = CropAsset.query.filter_by(farm_id=farm.id)\
        .order_by(CropAsset.created_at.desc()).all()

    total_biomass = sum(a.estimated_weight_kg or 0 for a in livestock)

    return render_template('farm_detail.html',
                           farm=farm,
                           livestock=livestock,
                           crops=crops,
                           total_biomass=round(total_biomass, 1))


@agriculture_bp.route('/farms/<int:farm_id>/edit', methods=['GET', 'POST'])
@login_required
def farm_edit(farm_id):
    farm = Farm.query.get_or_404(farm_id)
    if farm.owner_id != current_user.id:
        flash('Access denied.', 'danger')
        return redirect(url_for('agriculture.farms_list'))

    if request.method == 'POST':
        farm.name = request.form.get('name', farm.name).strip()
        farm.location = request.form.get('location', farm.location).strip()
        farm.latitude = request.form.get('latitude', type=float)
        farm.longitude = request.form.get('longitude', type=float)
        farm.farm_size = request.form.get('farm_size', type=float)
        farm.farm_size_unit = request.form.get('farm_size_unit', farm.farm_size_unit)
        farm.soil_type = request.form.get('soil_type', farm.soil_type).strip()
        db.session.commit()
        flash('Farm updated.', 'success')
        return redirect(url_for('agriculture.farm_detail', farm_id=farm.id))

    return render_template('farm_form.html', farm=farm)


@agriculture_bp.route('/livestock/new/<int:farm_id>', methods=['GET', 'POST'])
@login_required
def livestock_new(farm_id):
    farm = Farm.query.get_or_404(farm_id)
    if farm.owner_id != current_user.id:
        flash('Access denied.', 'danger')
        return redirect(url_for('agriculture.farms_list'))

    if request.method == 'POST':
        animal = LivestockAsset(
            farm_id=farm.id,
            owner_id=current_user.id,
            species=request.form.get('species', 'cattle'),
            breed=request.form.get('breed', '').strip(),
            sex=request.form.get('sex', ''),
            age=request.form.get('age', type=float),
            age_unit=request.form.get('age_unit', 'years'),
            health_status=request.form.get('health_status', 'healthy'),
            estimated_weight_kg=request.form.get('estimated_weight_kg', type=float),
            valuation_amount=request.form.get('valuation_amount', type=float)
        )
        db.session.add(animal)
        db.session.commit()
        flash('Livestock added.', 'success')
        return redirect(url_for('agriculture.farm_detail', farm_id=farm.id))

    return render_template('livestock_form.html', farm=farm)


@agriculture_bp.route('/livestock/<int:animal_id>')
@login_required
def livestock_detail(animal_id):
    animal = LivestockAsset.query.get_or_404(animal_id)
    if animal.owner_id != current_user.id:
        flash('Access denied.', 'danger')
        return redirect(url_for('agriculture.farms_list'))
    return render_template('livestock_detail.html', animal=animal)


@agriculture_bp.route('/crops/new/<int:farm_id>', methods=['GET', 'POST'])
@login_required
def crop_new(farm_id):
    farm = Farm.query.get_or_404(farm_id)
    if farm.owner_id != current_user.id:
        flash('Access denied.', 'danger')
        return redirect(url_for('agriculture.farms_list'))

    if request.method == 'POST':
        planting_date = request.form.get('planting_date')
        harvest_date = request.form.get('expected_harvest_date')
        crop = CropAsset(
            farm_id=farm.id,
            owner_id=current_user.id,
            crop_type=request.form.get('crop_type', '').strip(),
            variety=request.form.get('variety', '').strip(),
            area=request.form.get('area', type=float),
            area_unit=request.form.get('area_unit', 'hectares'),
            planting_date=datetime.strptime(planting_date, '%Y-%m-%d').date() if planting_date else None,
            expected_harvest_date=datetime.strptime(harvest_date, '%Y-%m-%d').date() if harvest_date else None,
            health_status=request.form.get('health_status', 'healthy')
        )
        db.session.add(crop)
        db.session.commit()
        flash('Crop added.', 'success')
        return redirect(url_for('agriculture.farm_detail', farm_id=farm.id))

    return render_template('crop_form.html', farm=farm)


# API endpoints
@agriculture_bp.route('/api/farms', methods=['POST'])
@login_required
def api_farm_create():
    data = request.get_json() or {}
    farm = Farm(
        owner_id=current_user.id,
        name=data.get('name', ''),
        location=data.get('location', ''),
        latitude=data.get('latitude'),
        longitude=data.get('longitude'),
        farm_size=data.get('farm_size'),
        farm_size_unit=data.get('farm_size_unit', 'hectares'),
        soil_type=data.get('soil_type', '')
    )
    db.session.add(farm)
    db.session.commit()
    return jsonify({'success': True, 'data': {'id': farm.id, 'name': farm.name}}), 201


@agriculture_bp.route('/api/livestock', methods=['POST'])
@login_required
def api_livestock_create():
    data = request.get_json() or {}
    farm = Farm.query.get(data.get('farm_id'))
    if not farm or farm.owner_id != current_user.id:
        return jsonify({'success': False, 'error': {'message': 'Invalid farm'}}), 400

    animal = LivestockAsset(
        farm_id=farm.id,
        owner_id=current_user.id,
        species=data.get('species', 'cattle'),
        breed=data.get('breed', ''),
        sex=data.get('sex', ''),
        age=data.get('age'),
        age_unit=data.get('age_unit', 'years'),
        health_status=data.get('health_status', 'healthy'),
        estimated_weight_kg=data.get('estimated_weight_kg'),
        valuation_amount=data.get('valuation_amount')
    )
    db.session.add(animal)
    db.session.commit()
    return jsonify({'success': True, 'data': {'id': animal.id}}), 201


@agriculture_bp.route('/api/crops', methods=['POST'])
@login_required
def api_crop_create():
    data = request.get_json() or {}
    farm = Farm.query.get(data.get('farm_id'))
    if not farm or farm.owner_id != current_user.id:
        return jsonify({'success': False, 'error': {'message': 'Invalid farm'}}), 400

    crop = CropAsset(
        farm_id=farm.id,
        owner_id=current_user.id,
        crop_type=data.get('crop_type', ''),
        variety=data.get('variety', ''),
        area=data.get('area'),
        area_unit=data.get('area_unit', 'hectares'),
        health_status=data.get('health_status', 'healthy')
    )
    db.session.add(crop)
    db.session.commit()
    return jsonify({'success': True, 'data': {'id': crop.id}}), 201
