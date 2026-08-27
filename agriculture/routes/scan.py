"""
Computer Vision Scan routes.
"""

import json
from datetime import datetime, timezone
from flask import render_template, request, jsonify
from flask_login import login_required, current_user
from models import db, VisionScan, LivestockAsset, CropAsset
from agriculture import agriculture_bp


@agriculture_bp.route('/scan')
@login_required
def scan_page():
    return render_template('scan.html')


@agriculture_bp.route('/scan/history')
@login_required
def scan_history():
    scans = VisionScan.query.filter_by(user_id=current_user.id)\
        .order_by(VisionScan.created_at.desc()).limit(50).all()
    return render_template('scan_history.html', scans=scans)


@agriculture_bp.route('/api/scan', methods=['POST'])
@login_required
def api_scan_save():
    data = request.get_json() or {}
    scan_type = data.get('scan_type', '')

    if scan_type not in ('LIVESTOCK_WEIGHT', 'CROP_DISEASE', 'CROP_HEALTH'):
        return jsonify({'success': False, 'error': {'message': 'Invalid scan type'}}), 400

    scan = VisionScan(
        user_id=current_user.id,
        farm_id=data.get('farm_id'),
        livestock_id=data.get('livestock_id'),
        crop_id=data.get('crop_id'),
        scan_type=scan_type,
        image_reference=data.get('image_reference', ''),
        model_name=data.get('model_name', 'unknown'),
        model_version=data.get('model_version', '1.0'),
        result_json=json.dumps(data.get('result', {})),
        confidence=data.get('confidence', 0)
    )
    db.session.add(scan)

    # Update asset if linked
    if scan_type == 'LIVESTOCK_WEIGHT' and data.get('livestock_id'):
        animal = LivestockAsset.query.get(data['livestock_id'])
        if animal and animal.owner_id == current_user.id:
            result = data.get('result', {})
            animal.estimated_weight_kg = result.get('weight_kg')
            animal.weight_margin_kg = result.get('margin_kg')
            animal.weight_confidence = data.get('confidence')
            animal.verification_status = 'ai_estimated'

    if scan_type == 'CROP_DISEASE' and data.get('crop_id'):
        crop = CropAsset.query.get(data['crop_id'])
        if crop and crop.owner_id == current_user.id:
            result = data.get('result', {})
            crop.disease_status = result.get('diagnosis', '')
            crop.health_score = 1.0 - result.get('severity', 0)

    db.session.commit()

    return jsonify({
        'success': True,
        'data': {
            'scan_id': scan.id,
            'confidence': scan.confidence,
            'created_at': scan.created_at.isoformat()
        }
    }), 201


@agriculture_bp.route('/api/scan/<int:scan_id>')
@login_required
def api_scan_detail(scan_id):
    scan = VisionScan.query.get_or_404(scan_id)
    if scan.user_id != current_user.id:
        return jsonify({'success': False, 'error': {'message': 'Access denied'}}), 403

    result = json.loads(scan.result_json) if scan.result_json else {}
    return jsonify({
        'success': True,
        'data': {
            'id': scan.id,
            'scan_type': scan.scan_type,
            'confidence': scan.confidence,
            'model_name': scan.model_name,
            'model_version': scan.model_version,
            'result': result,
            'created_at': scan.created_at.isoformat()
        }
    })
