import unittest
import requests
import logging
import time
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app, db
from app.models import Doctor

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DoctorRegistrationTest(unittest.TestCase):
    BASE_URL = 'http://localhost:5000/api'
    
    def setUp(self):
        """测试前的准备工作"""
        self.session = requests.Session()
        # 设置测试环境配置
        app = create_app()
        app.config['TESTING'] = True
        app.config['MAIL_SUPPRESS_SEND'] = True  # 禁用邮件发送
        app.config['VERIFICATION_CODE_RESEND_INTERVAL'] = 0  # 禁用重发间隔
        self.app = app
        self.app_context = app.app_context()
        self.app_context.push()
        
        # 清理数据库
        db.drop_all()
        db.create_all()
        
        # 启动测试服务器
        self.app.testing = True
        self.client = self.app.test_client()
    
    def tearDown(self):
        """测试后的清理工作"""
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
    
    def test_register_basic(self):
        """测试基本注册流程"""
        # 1. 发送注册请求
        register_data = {
            'doctor_id': '12345',
            'name': '测试医生',
            'password': 'Test123456!',
            'email': 'test@example.com',
            'department': '放射科'
        }
        
        response = self.client.post(
            '/api/auth/doctor/register',
            json=register_data
        )
        
        print(f"Server response: {response.data.decode()}")  # 打印服务器响应
        self.assertEqual(response.status_code, 200)
        result = response.get_json()
        self.assertTrue(result['success'])
        self.assertIn('verification_id', result)
        
        # 2. 验证邮箱验证码
        verification_data = {
            'verification_id': result['verification_id'],
            'code': '123456'  # 这里假设验证码是123456
        }
        
        response = self.client.post(
            '/api/auth/doctor/verify',
            json=verification_data
        )
        
        print(f"Verify response: {response.data.decode()}")  # 打印验证响应
        self.assertEqual(response.status_code, 200)
        result = response.get_json()
        self.assertTrue(result['success'])
    
    def test_invalid_email(self):
        """测试无效邮箱格式"""
        register_data = {
            'doctor_id': '12346',
            'name': '测试医生2',
            'password': 'Test123456!',
            'email': 'invalid_email',
            'department': '放射科'
        }
        
        response = self.client.post(
            '/api/auth/doctor/register',
            json=register_data
        )
        
        self.assertEqual(response.status_code, 400)
        result = response.get_json()
        self.assertFalse(result['success'])
        self.assertIn('Invalid email', result['message'])
    
    def test_weak_password(self):
        """测试弱密码"""
        register_data = {
            'doctor_id': '12347',
            'name': '测试医生3',
            'password': '123456',
            'email': 'test3@example.com',
            'department': '放射科'
        }
        
        response = self.client.post(
            '/api/auth/doctor/register',
            json=register_data
        )
        
        self.assertEqual(response.status_code, 400)
        result = response.get_json()
        self.assertFalse(result['success'])
        self.assertIn('Password', result['message'])  # 修改断言，检查大写的Password
    
    def test_duplicate_registration(self):
        """测试重复注册"""
        register_data = {
            'doctor_id': '12348',
            'name': '测试医生4',
            'password': 'Test123456!',
            'email': 'test4@example.com',
            'department': '放射科'
        }
        
        # 第一次注册
        response = self.client.post(
            '/api/auth/doctor/register',
            json=register_data
        )
        
        self.assertEqual(response.status_code, 200)
        result = response.get_json()
        verification_id = result['verification_id']
        
        # 完成第一次注册
        verification_data = {
            'verification_id': verification_id,
            'code': '123456'
        }
        response = self.client.post(
            '/api/auth/doctor/verify',
            json=verification_data
        )
        self.assertEqual(response.status_code, 200)
        
        # 第二次注册
        response = self.client.post(
            '/api/auth/doctor/register',
            json=register_data
        )
        
        self.assertEqual(response.status_code, 400)
        result = response.get_json()
        self.assertFalse(result['success'])
        self.assertIn('already exists', result['message'])
    
    def test_resend_code(self):
        """测试重发验证码的限制"""
        register_data = {
            'doctor_id': '12349',
            'name': '测试医生5',
            'password': 'Test123456!',
            'email': 'test5@example.com',
            'department': '放射科'
        }
        
        # 注册获取verification_id
        response = self.client.post(
            '/api/auth/doctor/register',
            json=register_data
        )
        
        self.assertEqual(response.status_code, 200)
        result = response.get_json()
        verification_id = result['verification_id']
        
        # 重发验证码
        response = self.client.post(
            '/api/auth/doctor/resend-code',
            json={'verification_id': verification_id}
        )
        
        self.assertEqual(response.status_code, 200)
        result = response.get_json()
        self.assertTrue(result['success'])
    
    def run_tests(self):
        """��行所有测试并打印结果"""
        test_loader = unittest.TestLoader()
        test_suite = test_loader.loadTestsFromTestCase(DoctorRegistrationTest)
        test_runner = unittest.TextTestRunner(verbosity=2)
        test_result = test_runner.run(test_suite)
        
        total_tests = test_result.testsRun
        passed_tests = total_tests - len(test_result.failures) - len(test_result.errors)
        pass_rate = (passed_tests / total_tests) * 100
        
        logger.info(f'测试完成')
        logger.info(f'总测试数: {total_tests}')
        logger.info(f'通过测试数: {passed_tests}')
        logger.info(f'通过率: {pass_rate:.2f}%')

if __name__ == '__main__':
    test = DoctorRegistrationTest()
    test.run_tests() 