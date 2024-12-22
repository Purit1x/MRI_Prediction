# MRI 预测系统后端

这是一个基于 Flask 的 MRI 预测系统后端，提供用户认证、患者管理、MRI 序列管理和预测功能的 RESTful API。

## 功能特性

- 用户认证（注册、登录、修改密码、邮箱绑定）
- 患者管理（添加、查询、更新、删除患者信息）
- MRI 序列管理（上传、查询、删除 MRI 序列）
- 预测功能（选择图像、标注区域、获取预测结果）
- 预测结果比较

## 技术栈

- Python 3.8+
- Flask
- SQLAlchemy
- JWT
- MySQL
- PyTorch
- OpenCV

## 安装

1. 克隆项目：

```bash
git clone [项目地址]
cd mri
```

2. 使用Conda创建环境：

```bash
conda env create -f environment.yml
```

3. 激活环境：

```bash
conda activate mri
```

4. 配置环境变量：

创建 `.env` 文件并设置以下变量：

```
SECRET_KEY=your-secret-key
JWT_SECRET_KEY=your-jwt-secret-key
DATABASE_URL=mysql+pymysql://username:password@localhost/mri_db
```

5. 初始化数据库：

```bash
flask db init
flask db migrate
flask db upgrade
```

## 运行

```bash
flask run
```

## API 文档

### 认证相关

#### 注册
- POST `/api/auth/register`
- 参数：username, email, password, verification_code

#### 登录
- POST `/api/auth/login`
- 参数：email, password

#### 发送验证码
- POST `/api/auth/send-verification-code`
- 参数：email, purpose

#### 修改密码
- POST `/api/auth/change-password`
- 参数：current_password, new_password, verification_code

#### 绑定邮箱
- POST `/api/auth/bind-email`
- 参数：email, verification_code

### 患者管理

#### 创建患者
- POST `/api/patients`
- 参数：id_card, name, gender, photo

#### 获取患者列表
- GET `/api/patients`
- 参数：page, per_page, search

#### 获取患者详情
- GET `/api/patients/<id>`

#### 更新患者信息
- PUT `/api/patients/<id>`
- 参数：name, gender, photo

#### 删除患者
- DELETE `/api/patients/<id>`

### MRI 序列管理

#### 上传序列
- POST `/api/mri/sequences`
- 参数：patient_id, sequence_name, files

#### 获取患者的序列列表
- GET `/api/mri/sequences/<patient_id>`

#### 删除序列
- DELETE `/api/mri/sequences/<id>`

#### 获取序列文件列表
- GET `/api/mri/sequences/<id>/files`

### 预测功能

#### 创建预测
- POST `/api/predictions`
- 参数：sequence_id, image_path, prostate_region, needle_positions

#### 获取序列的预测记录
- GET `/api/predictions/sequence/<sequence_id>`

#### 获取预测详情
- GET `/api/predictions/<id>`

#### 比较预测结果
- POST `/api/predictions/compare`
- 参数：prediction_ids

## 注意事项

1. 所有需要认证的 API 请求都需要在 Header 中携带 JWT token：
```
Authorization: Bearer <access_token>
```

2. 文件上传大小限制为 16MB

3. 支持的图像格式：
- 患者照片：jpg, jpeg, png
- MRI 序列：dcm, dicom

## 开发说明

1. 代码结构：
```
mri/
  ├── app/
  │   ├── auth/
  │   ├── patient/
  │   ├── mri/
  │   ├── prediction/
  │   └── models.py
  ├── migrations/
  ├── uploads/
  ├── config.py
  ├── app.py
  └── environment.yml
```

2. 数据库迁移：
- 创建迁移：`flask db migrate -m "migration message"`
- 应用迁移：`flask db upgrade`

3. Conda环境管理：
- 更新环境：`conda env update -f environment.yml`
- 删除环境：`conda env remove -n mri`
- 查看环境列表：`conda env list`