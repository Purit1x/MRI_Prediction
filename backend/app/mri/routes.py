import os
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required
from werkzeug.utils import secure_filename
from app.models import Patient, MRISequence
from app import db

bp = Blueprint('mri', __name__)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'dcm', 'dicom'}

@bp.route('/sequences', methods=['POST'])
@jwt_required()
def create_sequence():
    # 获取表单数据
    patient_id = request.form.get('patient_id')
    sequence_name = request.form.get('sequence_name')
    files = request.files.getlist('files')
    
    # 验证必要字段
    if not all([patient_id, sequence_name, files]):
        return jsonify({'error': '缺少必要字段'}), 400
    
    # 验证患者是否存在
    patient = Patient.query.get(patient_id)
    if not patient:
        return jsonify({'error': '患者不存在'}), 404
    
    # 验证序列名是否已存在
    if MRISequence.query.filter_by(patient_id=patient_id, sequence_name=sequence_name).first():
        return jsonify({'error': '序列名称已存在'}), 400
    
    # 创建序列文件夹
    folder_path = os.path.join('sequences', f'patient_{patient_id}', sequence_name)
    full_folder_path = os.path.join(current_app.config['UPLOAD_FOLDER'], folder_path)
    os.makedirs(full_folder_path, exist_ok=True)
    
    # 保存文件
    saved_files = []
    for file in files:
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(full_folder_path, filename)
            file.save(file_path)
            saved_files.append(filename)
    
    if not saved_files:
        return jsonify({'error': '没有有效的DICOM文件上传'}), 400
    
    # 创建序列记录
    sequence = MRISequence(
        patient_id=patient_id,
        sequence_name=sequence_name,
        folder_path=folder_path
    )
    
    db.session.add(sequence)
    db.session.commit()
    
    return jsonify({
        'message': '序列创建成功',
        'sequence': {
            'id': sequence.id,
            'patient_id': sequence.patient_id,
            'sequence_name': sequence.sequence_name,
            'folder_path': sequence.folder_path,
            'file_count': len(saved_files)
        }
    }), 201

@bp.route('/sequences/<int:patient_id>', methods=['GET'])
@jwt_required()
def get_sequences(patient_id):
    # 验证患者是否存在
    patient = Patient.query.get_or_404(patient_id)
    
    # 获取患者的所有序列
    sequences = MRISequence.query.filter_by(patient_id=patient_id).all()
    
    return jsonify({
        'sequences': [{
            'id': seq.id,
            'sequence_name': seq.sequence_name,
            'folder_path': seq.folder_path,
            'created_at': seq.created_at.isoformat()
        } for seq in sequences]
    })

@bp.route('/sequences/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_sequence(id):
    sequence = MRISequence.query.get_or_404(id)
    
    # 删除序列文件夹
    folder_path = os.path.join(current_app.config['UPLOAD_FOLDER'], sequence.folder_path)
    if os.path.exists(folder_path):
        for file in os.listdir(folder_path):
            os.remove(os.path.join(folder_path, file))
        os.rmdir(folder_path)
    
    # 删除序列记录
    db.session.delete(sequence)
    db.session.commit()
    
    return jsonify({'message': '序列删除成功'})

@bp.route('/sequences/<int:id>/files', methods=['GET'])
@jwt_required()
def get_sequence_files(id):
    sequence = MRISequence.query.get_or_404(id)
    
    # 获取序列文件夹中的所有文件
    folder_path = os.path.join(current_app.config['UPLOAD_FOLDER'], sequence.folder_path)
    if not os.path.exists(folder_path):
        return jsonify({'error': '序列文件夹不存在'}), 404
    
    files = []
    for filename in os.listdir(folder_path):
        if allowed_file(filename):
            file_path = os.path.join(sequence.folder_path, filename)
            files.append({
                'name': filename,
                'path': file_path
            })
    
    return jsonify({
        'sequence_id': sequence.id,
        'sequence_name': sequence.sequence_name,
        'files': files
    }) 