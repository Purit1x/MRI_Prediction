from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity
from app.models import Doctor, Administrator
from app import db
from datetime import datetime, timedelta

bp = Blueprint('auth', __name__)

@bp.route('/doctor/login', methods=['POST'])
def doctor_login():
    data = request.get_json()
    
    if not all(k in data for k in ['job_number', 'password']):
        return jsonify({'error': '缺少必要字段'}), 400
    
    doctor = Doctor.query.filter_by(job_number=data['job_number']).first()
    
    if doctor and doctor.check_password(data['password']):
        access_token = create_access_token(identity=doctor.doctor_id)
        refresh_token = create_refresh_token(identity=doctor.doctor_id)
        return jsonify({
            'access_token': access_token,
            'refresh_token': refresh_token,
            'doctor': {
                'id': doctor.doctor_id,
                'name': doctor.doctor_name,
                'job_number': doctor.job_number
            }
        })
    
    return jsonify({'error': '工号或密码错误'}), 401

@bp.route('/admin/login', methods=['POST'])
def admin_login():
    data = request.get_json()
    
    if not all(k in data for k in ['admin_id', 'password']):
        return jsonify({'error': '缺少必要字段'}), 400
    
    admin = Administrator.query.get(data['admin_id'])
    
    if admin and admin.check_password(data['password']):
        access_token = create_access_token(identity=admin.admin_id)
        refresh_token = create_refresh_token(identity=admin.admin_id)
        return jsonify({
            'access_token': access_token,
            'refresh_token': refresh_token,
            'admin_id': admin.admin_id
        })
    
    return jsonify({'error': '管理员ID或密码错误'}), 401