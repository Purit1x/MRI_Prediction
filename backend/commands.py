import click
from flask.cli import with_appcontext
from app.models import Administrator
from app import db

@click.command('create-admin')
@click.argument('admin_id')
@click.argument('password')
@with_appcontext
def create_admin(admin_id, password):
    """创建管理员账户"""
    try:
        admin = Administrator(admin_id=admin_id)
        admin.set_password(password)
        db.session.add(admin)
        db.session.commit()
        click.echo(f'成功创建管理员账户 {admin_id}')
    except Exception as e:
        db.session.rollback()
        click.echo(f'创建管理员账户失败: {str(e)}') 