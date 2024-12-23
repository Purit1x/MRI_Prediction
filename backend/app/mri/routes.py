import os
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.utils import secure_filename
from app.models import Patient, MRISequence, MRISeqItem, Doctor, Administrator
from app import db
from datetime import datetime

bp = Blueprint('mri', __name__)

def allowed_file(filename):
    """检查文件类型是否允许"""
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'dcm', 'dicom'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def create_sequence_directory(patient_id, seq_name):
    """创建序列文件夹"""
    base_dir = current_app.config['UPLOAD_FOLDER']
    patient_dir = os.path.join(base_dir, f'patient_{patient_id}')
    seq_dir = os.path.join(patient_dir, secure_filename(seq_name))
    
    # 确保目录存在
    os.makedirs(seq_dir, exist_ok=True)
    return seq_dir

def get_user_type(user_id):
    """获取用户类型"""
    if user_id.startswith('admin_'):
        return 'admin', int(user_id.replace('admin_', ''))
    return 'doctor', user_id

@bp.route('/patients/<int:patient_id>/sequences', methods=['POST'])
@jwt_required()
def create_sequence(patient_id):
    """创建新的MRI序列"""
    # 验证用户身份
    current_user_id = get_jwt_identity()
    user_type, user_id = get_user_type(current_user_id)
    
    # 检查患者是否存在
    patient = Patient.query.get(patient_id)
    if not patient:
        return jsonify({
            'success': False,
            'message': '患者不存在',
            'should_create_patient': True
        }), 404
    
    # 获取序列名称
    if 'seq_name' not in request.form:
        return jsonify({
            'success': False,
            'message': '缺少序列名称'
        }), 400
    
    seq_name = request.form['seq_name']
    
    # 检查序列名称是否已存在
    existing_sequence = MRISequence.query.filter_by(
        patient_id=patient_id,
        seq_name=seq_name
    ).first()
    
    if existing_sequence:
        return jsonify({
            'success': False,
            'message': '序列名称已存在'
        }), 400
    
    # 检查是否上传了文件
    if 'files[]' not in request.files:
        return jsonify({
            'success': False,
            'message': '未上传任何文件'
        }), 400
    
    files = request.files.getlist('files[]')
    if not files or not any(file.filename for file in files):
        return jsonify({
            'success': False,
            'message': '未选择任何文件'
        }), 400
    
    try:
        # 创建序列目录
        seq_dir = create_sequence_directory(patient_id, seq_name)
        
        # 创建序列记录
        sequence = MRISequence(
            seq_name=seq_name,
            seq_dir=seq_dir,
            patient_id=patient_id
        )
        db.session.add(sequence)
        db.session.flush()  # 获取sequence_id
        
        # 保存文件
        uploaded_files = []
        for file in files:
            if file and file.filename and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file_path = os.path.join(seq_dir, filename)
                
                # 确保文件名唯一
                base, ext = os.path.splitext(filename)
                counter = 1
                while os.path.exists(file_path):
                    filename = f"{base}_{counter}{ext}"
                    file_path = os.path.join(seq_dir, filename)
                    counter += 1
                
                file.save(file_path)
                
                # 创建��列项记录
                seq_item = MRISeqItem(
                    item_name=filename,
                    file_path=file_path,
                    seq_id=sequence.seq_id
                )
                db.session.add(seq_item)
                uploaded_files.append(filename)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '序列创建成功',
            'sequence': {
                'id': sequence.seq_id,
                'name': sequence.seq_name,
                'files': uploaded_files,
                'created_at': sequence.created_at.isoformat()
            }
        })
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error in create_sequence: {str(e)}")
        return jsonify({
            'success': False,
            'message': '序列创建失败，请稍后重试'
        }), 500

@bp.route('/patients/<int:patient_id>/sequences/<int:seq_id>', methods=['GET'])
@jwt_required()
def get_sequence(patient_id, seq_id):
    """获取序列详情"""
    sequence = MRISequence.query.filter_by(
        seq_id=seq_id,
        patient_id=patient_id
    ).first()
    
    if not sequence:
        return jsonify({
            'success': False,
            'message': '序列不存在'
        }), 404
    
    return jsonify({
        'success': True,
        'sequence': {
            'id': sequence.seq_id,
            'name': sequence.seq_name,
            'created_at': sequence.created_at.isoformat(),
            'items': [{
                'id': item.item_id,
                'name': item.item_name,
                'uploaded_at': item.uploaded_at.isoformat()
            } for item in sequence.items]
        }
    })

@bp.route('/patients/<int:patient_id>/sequences', methods=['GET'])
@jwt_required()
def list_sequences(patient_id):
    """获取患者的所有序列"""
    patient = Patient.query.get(patient_id)
    if not patient:
        return jsonify({
            'success': False,
            'message': '患者不存在'
        }), 404
    
    sequences = MRISequence.query.filter_by(patient_id=patient_id).all()
    
    return jsonify({
        'success': True,
        'sequences': [{
            'id': seq.seq_id,
            'name': seq.seq_name,
            'created_at': seq.created_at.isoformat(),
            'item_count': len(seq.items)
        } for seq in sequences]
    }) 