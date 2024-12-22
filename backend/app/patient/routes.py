import os
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required
from werkzeug.utils import secure_filename
from app.models import Patient
from app import db

bp = Blueprint('patient', __name__)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg'}

@bp.route('', methods=['POST'])
@jwt_required()
def create_patient():
    # 获取表单数据
    id_card = request.form.get('id_card')
    name = request.form.get('name')
    gender = request.form.get('gender')
    photo = request.files.get('photo')
    
    # 验证必要字段
    if not all([id_card, name, gender]):
        return jsonify({'error': '缺少必要字段'}), 400
    
    # 验证性别格式
    if gender not in ['M', 'F']:
        return jsonify({'error': '性别格式错误'}), 400
    
    # 验证身份证号是否已存在
    if Patient.query.filter_by(id_card=id_card).first():
        return jsonify({'error': '该身份证号已存在'}), 400
    
    # 处理照片上传
    photo_path = None
    if photo and allowed_file(photo.filename):
        filename = secure_filename(f"{id_card}_{photo.filename}")
        photo_path = os.path.join('patients', filename)
        os.makedirs(os.path.join(current_app.config['UPLOAD_FOLDER'], 'patients'), exist_ok=True)
        photo.save(os.path.join(current_app.config['UPLOAD_FOLDER'], photo_path))
    
    # 创建患者记录
    patient = Patient(
        id_card=id_card,
        name=name,
        gender=gender,
        photo_path=photo_path
    )
    
    db.session.add(patient)
    db.session.commit()
    
    return jsonify({
        'message': '患者信息创建成功',
        'patient': {
            'id': patient.id,
            'id_card': patient.id_card,
            'name': patient.name,
            'gender': patient.gender,
            'photo_path': patient.photo_path
        }
    }), 201

@bp.route('', methods=['GET'])
@jwt_required()
def get_patients():
    # 获取查询参数
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    search = request.args.get('search', '')
    
    # 构建查询
    query = Patient.query
    if search:
        query = query.filter(
            (Patient.name.ilike(f'%{search}%')) |
            (Patient.id_card.ilike(f'%{search}%'))
        )
    
    # 执行分页查询
    pagination = query.order_by(Patient.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    # 构建响应数据
    patients = [{
        'id': patient.id,
        'id_card': patient.id_card,
        'name': patient.name,
        'gender': patient.gender,
        'photo_path': patient.photo_path,
        'created_at': patient.created_at.isoformat()
    } for patient in pagination.items]
    
    return jsonify({
        'patients': patients,
        'total': pagination.total,
        'pages': pagination.pages,
        'current_page': page
    })

@bp.route('/<int:id>', methods=['GET'])
@jwt_required()
def get_patient(id):
    patient = Patient.query.get_or_404(id)
    
    return jsonify({
        'id': patient.id,
        'id_card': patient.id_card,
        'name': patient.name,
        'gender': patient.gender,
        'photo_path': patient.photo_path,
        'created_at': patient.created_at.isoformat()
    })

@bp.route('/<int:id>', methods=['PUT'])
@jwt_required()
def update_patient(id):
    patient = Patient.query.get_or_404(id)
    
    # 获取表单数据
    name = request.form.get('name')
    gender = request.form.get('gender')
    photo = request.files.get('photo')
    
    # 更新基本信息
    if name:
        patient.name = name
    if gender:
        if gender not in ['M', 'F']:
            return jsonify({'error': '性别格式错误'}), 400
        patient.gender = gender
    
    # 处理照片更新
    if photo and allowed_file(photo.filename):
        # 删除旧照片
        if patient.photo_path:
            old_photo_path = os.path.join(current_app.config['UPLOAD_FOLDER'], patient.photo_path)
            if os.path.exists(old_photo_path):
                os.remove(old_photo_path)
        
        # 保存新照片
        filename = secure_filename(f"{patient.id_card}_{photo.filename}")
        photo_path = os.path.join('patients', filename)
        photo.save(os.path.join(current_app.config['UPLOAD_FOLDER'], photo_path))
        patient.photo_path = photo_path
    
    db.session.commit()
    
    return jsonify({
        'message': '患者信息更新成功',
        'patient': {
            'id': patient.id,
            'id_card': patient.id_card,
            'name': patient.name,
            'gender': patient.gender,
            'photo_path': patient.photo_path
        }
    })

@bp.route('/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_patient(id):
    patient = Patient.query.get_or_404(id)
    
    # 删除患者照片
    if patient.photo_path:
        photo_path = os.path.join(current_app.config['UPLOAD_FOLDER'], patient.photo_path)
        if os.path.exists(photo_path):
            os.remove(photo_path)
    
    db.session.delete(patient)
    db.session.commit()
    
    return jsonify({'message': '患者信息删除成功'}) 