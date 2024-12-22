from datetime import datetime
from app import db
from werkzeug.security import generate_password_hash, check_password_hash

class Doctor(db.Model):
    __tablename__ = 'doctors'
    doctor_id = db.Column(db.Integer, primary_key=True)
    doctor_name = db.Column(db.String(50), nullable=False)
    job_number = db.Column(db.String(10), nullable=False, unique=True)
    password = db.Column(db.String(70), nullable=False)
    
    predictions = db.relationship('PredRecord', secondary='pred_doctor', back_populates='doctor')
    
    def set_password(self, password):
        self.password = generate_password_hash(password, method='sha256')
    
    def check_password(self, password):
        return check_password_hash(self.password, password)

class Administrator(db.Model):
    __tablename__ = 'administrators'
    admin_id = db.Column(db.Integer, primary_key=True)
    password = db.Column(db.String(70), nullable=False)
    
    def set_password(self, password):
        self.password = generate_password_hash(password, method='sha256')
    
    def check_password(self, password):
        return check_password_hash(self.password, password)

class MRISequence(db.Model):
    __tablename__ = 'mri_sequences'
    seq_id = db.Column(db.Integer, primary_key=True)
    seq_dir = db.Column(db.String(500), nullable=False)
    
    # 关联
    items = db.relationship('MRISeqItem', secondary='sequence_item', back_populates='sequences')
    patient = db.relationship('Patient', secondary='patient_sequence', back_populates='sequences')

class MRISeqItem(db.Model):
    __tablename__ = 'mri_seq_items'
    item_id = db.Column(db.Integer, primary_key=True)
    item_name = db.Column(db.String(256), nullable=False)
    
    # 关联
    sequences = db.relationship('MRISequence', secondary='sequence_item', back_populates='items')
    predictions = db.relationship('PredRecord', secondary='pred_mri_item', back_populates='mri_item')

class SequenceItem(db.Model):
    __tablename__ = 'sequence_item'
    item_id = db.Column(db.Integer, db.ForeignKey('mri_seq_items.item_id'), primary_key=True)
    seq_id = db.Column(db.Integer, db.ForeignKey('mri_sequences.seq_id'), nullable=False)

class Patient(db.Model):
    __tablename__ = 'patients'
    patient_id = db.Column(db.Integer, primary_key=True)
    patient_name = db.Column(db.String(50), nullable=False)
    sex = db.Column(db.String(15), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    IDNumber = db.Column(db.String(20), nullable=False, unique=True)
    
    # 关联
    sequences = db.relationship('MRISequence', secondary='patient_sequence', back_populates='patient')

class PatientSequence(db.Model):
    __tablename__ = 'patient_sequence'
    seq_id = db.Column(db.Integer, db.ForeignKey('mri_sequences.seq_id'), primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.patient_id'), nullable=False)

class PredRecord(db.Model):
    __tablename__ = 'pred_records'
    pred_id = db.Column(db.Integer, primary_key=True)
    pred_time = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    result_name = db.Column(db.String(800), nullable=False)
    
    # 关联
    doctor = db.relationship('Doctor', secondary='pred_doctor', back_populates='predictions')
    mri_item = db.relationship('MRISeqItem', secondary='pred_mri_item', back_populates='predictions')

class PredDoctor(db.Model):
    __tablename__ = 'pred_doctor'
    pred_id = db.Column(db.Integer, db.ForeignKey('pred_records.pred_id'), primary_key=True)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctors.doctor_id'), nullable=False)

class PredMRIItem(db.Model):
    __tablename__ = 'pred_mri_item'
    pred_id = db.Column(db.Integer, db.ForeignKey('pred_records.pred_id'), primary_key=True)
    item_id = db.Column(db.Integer, db.ForeignKey('mri_seq_items.item_id'), nullable=False)