from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from flask_mail import Mail
from config import Config
import os

db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()
mail = Mail()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # 初始化扩展
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    mail.init_app(app)
    CORS(app)
    
    # 确保上传文件夹存在
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    # 注册蓝图
    from app.auth import bp as auth_bp
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    
    from app.patient import bp as patient_bp
    app.register_blueprint(patient_bp, url_prefix='/api/patients')
    
    from app.mri import bp as mri_bp
    app.register_blueprint(mri_bp, url_prefix='/api/mri')
    
    from app.prediction import bp as prediction_bp
    app.register_blueprint(prediction_bp, url_prefix='/api/predictions')
    
    @app.route('/test')
    def test():
        return 'Hello, World!'
    
    return app 