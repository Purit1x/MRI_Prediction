import os
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required
from app.models import MRISequence, PredRecord, MRISeqItem
from app import db
import json

bp = Blueprint('prediction', __name__)

@bp.route('', methods=['POST'])
@jwt_required()
def create_prediction():
    data = request.get_json()
    
    # 验证必要字段
    if not all(k in data for k in ['sequence_id', 'image_path', 'prostate_region', 'needle_positions']):
        return jsonify({'error': '缺少必要字段'}), 400
    
    # 验证序列是否存在
    sequence = MRISequence.query.get(data['sequence_id'])
    if not sequence:
        return jsonify({'error': '序列不存在'}), 404
    
    # 验证图像是否存在
    image_path = os.path.join(current_app.config['UPLOAD_FOLDER'], data['image_path'])
    if not os.path.exists(image_path):
        return jsonify({'error': '图像文件不存在'}), 404
    
    # TODO: 调用预测模型
    # 这里应该调用实际的预测模型，获取预测结果
    # 为了演示，我们假设预测结果是保存在一个新的图像文件中
    
    # 生成预测结果图像路径
    result_filename = f"prediction_{sequence.seq_id}_{os.path.basename(data['image_path'])}"
    result_path = os.path.join('predictions', result_filename)
    full_result_path = os.path.join(current_app.config['UPLOAD_FOLDER'], result_path)
    
    # 确保预测结果目录存在
    os.makedirs(os.path.dirname(full_result_path), exist_ok=True)
    
    # 创建预测记录
    prediction = PredRecord(
        result_name=result_path
    )
    
    db.session.add(prediction)
    db.session.commit()
    
    return jsonify({
        'message': '预测完成',
        'prediction': {
            'id': prediction.pred_id,
            'result_name': prediction.result_name,
            'pred_time': prediction.pred_time.isoformat()
        }
    }), 201

@bp.route('/sequence/<int:sequence_id>', methods=['GET'])
@jwt_required()
def get_sequence_predictions(sequence_id):
    # 验证序列是否存在
    sequence = MRISequence.query.get_or_404(sequence_id)
    
    # 获取序列的所有预测记录
    predictions = PredRecord.query.join(MRISeqItem).filter(MRISeqItem.seq_id == sequence_id).all()
    
    return jsonify({
        'predictions': [{
            'id': pred.pred_id,
            'result_name': pred.result_name,
            'pred_time': pred.pred_time.isoformat()
        } for pred in predictions]
    })

@bp.route('/<int:id>', methods=['GET'])
@jwt_required()
def get_prediction(id):
    prediction = PredRecord.query.get_or_404(id)
    
    return jsonify({
        'id': prediction.pred_id,
        'result_name': prediction.result_name,
        'pred_time': prediction.pred_time.isoformat()
    })

@bp.route('/compare', methods=['POST'])
@jwt_required()
def compare_predictions():
    data = request.get_json()
    
    # 验证必要字段
    if 'prediction_ids' not in data or not isinstance(data['prediction_ids'], list):
        return jsonify({'error': '缺少预测ID列表'}), 400
    
    # 获取所有预测记录
    predictions = []
    for pred_id in data['prediction_ids']:
        prediction = PredRecord.query.get(pred_id)
        if prediction:
            predictions.append({
                'id': prediction.pred_id,
                'result_name': prediction.result_name,
                'pred_time': prediction.pred_time.isoformat()
            })
    
    if not predictions:
        return jsonify({'error': '没有找到有效的预测记录'}), 404
    
    return jsonify({
        'predictions': predictions
    }) 