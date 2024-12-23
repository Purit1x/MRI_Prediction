import requests
import json
import logging
import time
from datetime import datetime

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DoctorRegistrationTest:
    def __init__(self, base_url="http://localhost:5001"):
        self.base_url = base_url
        self.headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
    
    def test_register_basic(self):
        """测试基本注册流程"""
        logger.info("测试基本注册流程")
        
        # 第一步：提交注册信息
        data = {
            "doctor_name": "张医生",
            "job_number": "DR001",
            "email": "test@example.com",
            "password": "Test123!@#"
        }
        
        response = requests.post(
            f"{self.base_url}/api/auth/doctor/register",
            json=data,
            headers=self.headers
        )
        
        logger.info(f"注册响应: {response.status_code}")
        logger.info(f"响应内容: {response.text}")
        
        if response.status_code != 201:
            logger.error("注册失败")
            return False
        
        # 保存医生ID用于后续验证
        doctor_id = response.json()['doctor']['id']
        
        # 第二步：验证邮箱（这里假设我们知道验证码是什么，实际中需要从邮箱获取）
        verify_data = {
            "doctor_id": doctor_id,
            "code": "123456"  # 实际中这个验证码应该从邮箱中获取
        }
        
        response = requests.post(
            f"{self.base_url}/api/auth/doctor/verify",
            json=verify_data,
            headers=self.headers
        )
        
        logger.info(f"验证响应: {response.status_code}")
        logger.info(f"响应内容: {response.text}")
        
        return response.status_code == 200
    
    def test_invalid_email(self):
        """测试无效的邮箱格式"""
        logger.info("测试无效的邮箱格式")
        
        data = {
            "doctor_name": "李医生",
            "job_number": "DR002",
            "email": "invalid-email",
            "password": "Test123!@#"
        }
        
        response = requests.post(
            f"{self.base_url}/api/auth/doctor/register",
            json=data,
            headers=self.headers
        )
        
        logger.info(f"响应状态码: {response.status_code}")
        logger.info(f"响应内容: {response.text}")
        
        return response.status_code == 400 and "邮箱格式不正确" in response.text
    
    def test_weak_password(self):
        """测试弱密码"""
        logger.info("测试弱密码")
        
        data = {
            "doctor_name": "王医生",
            "job_number": "DR003",
            "email": "test3@example.com",
            "password": "123456"  # 弱密码
        }
        
        response = requests.post(
            f"{self.base_url}/api/auth/doctor/register",
            json=data,
            headers=self.headers
        )
        
        logger.info(f"响应状态码: {response.status_code}")
        logger.info(f"响应内容: {response.text}")
        
        return response.status_code == 400 and "密码" in response.text
    
    def test_duplicate_registration(self):
        """测试重复注册"""
        logger.info("测试重复注册")
        
        # 先注册一个医生
        data = {
            "doctor_name": "赵医生",
            "job_number": "DR004",
            "email": "test4@example.com",
            "password": "Test123!@#"
        }
        
        response = requests.post(
            f"{self.base_url}/api/auth/doctor/register",
            json=data,
            headers=self.headers
        )
        
        # 尝试使用相同的工号再次注册
        response = requests.post(
            f"{self.base_url}/api/auth/doctor/register",
            json=data,
            headers=self.headers
        )
        
        logger.info(f"响应状态码: {response.status_code}")
        logger.info(f"响应内容: {response.text}")
        
        return response.status_code == 400 and "已存在" in response.text
    
    def test_resend_code(self):
        """测试重发验证码"""
        logger.info("测试重发验证码")
        
        # 先注册一个医生
        data = {
            "doctor_name": "钱医生",
            "job_number": "DR005",
            "email": "test5@example.com",
            "password": "Test123!@#"
        }
        
        response = requests.post(
            f"{self.base_url}/api/auth/doctor/register",
            json=data,
            headers=self.headers
        )
        
        if response.status_code != 201:
            logger.error("注册失败")
            return False
        
        doctor_id = response.json()['doctor']['id']
        
        # 立即尝试重发验证码
        resend_data = {
            "doctor_id": doctor_id
        }
        
        response = requests.post(
            f"{self.base_url}/api/auth/doctor/resend-code",
            json=resend_data,
            headers=self.headers
        )
        
        logger.info(f"重发验证码响应: {response.status_code}")
        logger.info(f"响应内容: {response.text}")
        
        return response.status_code == 429 and "请等待" in response.text

def run_tests():
    """运行所有测试"""
    test = DoctorRegistrationTest()
    
    # 运行测试并收集结果
    results = {
        "基本注册流程": test.test_register_basic(),
        "无效邮箱格式": test.test_invalid_email(),
        "弱密码": test.test_weak_password(),
        "重复注册": test.test_duplicate_registration(),
        "重发验证码限制": test.test_resend_code()
    }
    
    # 打印测试结果
    logger.info("\n测试结果汇总:")
    for test_name, result in results.items():
        status = "通过" if result else "失败"
        logger.info(f"{test_name}: {status}")
    
    # 计算通过率
    passed = sum(1 for result in results.values() if result)
    total = len(results)
    pass_rate = (passed / total) * 100
    
    logger.info(f"\n测试通过率: {pass_rate:.2f}% ({passed}/{total})")

if __name__ == "__main__":
    run_tests() 