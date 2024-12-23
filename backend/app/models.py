from datetime import datetime, timedelta
from app import db
from werkzeug.security import generate_password_hash, check_password_hash
import random

class Doctor(db.Model):
    __tablename__ = 'doctors'
    
    doctor_id = db.Column(db.String(64), primary_key=True)
    name = db.Column(db.String(64), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    department = db.Column(db.String(64), nullable=False)
    password_hash = db.Column(db.String(256))
    login_attempts = db.Column(db.Integer, default=0)  # 登录尝试次数
    locked_until = db.Column(db.DateTime)  # 账户锁定截止时间
    
    def set_password(self, password):
        """设置密码"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """验证密码"""
        return check_password_hash(self.password_hash, password)
    
    def is_locked(self):
        """检查账户是否被锁定"""
        if self.locked_until is None:
            return False
        return datetime.utcnow() < self.locked_until
    
    def increment_login_attempts(self):
        """增加登录尝试次数，如果超过限制则锁定账户"""
        self.login_attempts += 1
        if self.login_attempts >= 5:  # 5次失败后锁定账户
            self.locked_until = datetime.utcnow() + timedelta(minutes=30)  # 锁定30分钟
    
    def reset_login_attempts(self):
        """重置登录尝试次数"""
        self.login_attempts = 0
        self.locked_until = None

class Administrator(db.Model):
    __tablename__ = 'administrators'
    
    admin_id = db.Column(db.Integer, primary_key=True)
    password_hash = db.Column(db.String(128), nullable=False)
    
    def set_password(self, password):
        """设置密码"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """验证密码"""
        return check_password_hash(self.password_hash, password)

class MRISequence(db.Model):
    __tablename__ = 'mri_sequences'
    
    seq_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    seq_dir = db.Column(db.String(255), nullable=False)

class MRISeqItem(db.Model):
    __tablename__ = 'mri_seq_items'
    
    item_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    item_name = db.Column(db.String(255), nullable=False)
    seq_id = db.Column(db.Integer, db.ForeignKey('mri_sequences.seq_id'), nullable=False)

class Patient(db.Model):
    __tablename__ = 'patients'
    
    patient_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    patient_name = db.Column(db.String(50), nullable=False)
    sex = db.Column(db.String(10), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    id_number = db.Column(db.String(18), unique=True, nullable=False)

class PredRecord(db.Model):
    __tablename__ = 'pred_records'
    
    pred_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    pred_time = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    result_name = db.Column(db.String(255), nullable=False)

# 关联表
pred_doctor = db.Table('pred_doctor',
    db.Column('pred_id', db.Integer, db.ForeignKey('pred_records.pred_id'), primary_key=True),
    db.Column('doctor_id', db.String(64), db.ForeignKey('doctors.doctor_id'), primary_key=True)
)

pred_mri_item = db.Table('pred_mri_item',
    db.Column('pred_id', db.Integer, db.ForeignKey('pred_records.pred_id'), primary_key=True),
    db.Column('item_id', db.Integer, db.ForeignKey('mri_seq_items.item_id'), primary_key=True)
)

sequence_item = db.Table('sequence_item',
    db.Column('seq_id', db.Integer, db.ForeignKey('mri_sequences.seq_id'), primary_key=True),
    db.Column('item_id', db.Integer, db.ForeignKey('mri_seq_items.item_id'), primary_key=True)
)