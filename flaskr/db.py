import sqlite3

import click
from flask import current_app, g
from flask.cli import with_appcontext


# 初始化数据库
def init_db():
    # 获取连接
    db = get_db()
    
    # 打开sql文件
    with current_app.open_resource('schema.sql') as f:
        # 读取文件中sql语句，然后执行它
        db.executescript(f.read().decode("utf8"))


# 定义一个名为 init-db 命令行，
# 它调用 init_db 函数，并为用户显示一个成功的消息。
@click.command("init-db")
@with_appcontext  # 应该是用于获取当前应用运行的上下文环境
def init_db_command():
    # 初始化数据库（若已存在表就删除）
    init_db()
    click.echo("初始化数据库！")  # 可用于测试获得
    """
    `click.command()`定义一个名为 `init-db` 命令行，
     它调用 `init_db` 函数，并为用户显示一个成功的消息。
    """

# 获取连接
def get_db():
    if "db" not in g:  # g也是用来存储数据
        # 创建个连接然并放进g中
        g.db = sqlite3.connect(
            # 这里因为没办法直接用工厂函数return的app
            # 所以需要用current_app来指向这个app，好对它进行操作
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row  # 告诉连接返回类似于字典的行，这样可以通过列名称来操作 数据

    return g.db

# 关闭连接
def close_db(e=None):
    db = g.pop('db', None)  # 从g中弹出连接
    if db is not None:
        db.close()


# 注册到应用中
def init_app(app):
    # 告诉 Flask 在返回响应后进行清理的时候调用此函数
    app.teardown_appcontext(close_db)  # 注册关闭数据库连接的函数
    # 添加一个新的 可以与 `flask`一起工作的命令。命令行中的`flask`是小写的
    app.cli.add_command(init_db_command)  # 注册初始化数据库的命令
    
    
    
    
    