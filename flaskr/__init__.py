import os
from flask import Flask


# create_app 是一个应用工厂函数
def create_app(test_config=None):
    # 用于创建和配置Flask应用
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY="dev",
        DATABASE=os.path.join(app.instance_path, "flask.sqlite"),  # 这里定义了数据库的路径和名称
    )
    # print(app.instance_path)
    # C:\Users\Jarvis\Desktop\Python后端学习\flask_tutorial\instance
    
    if test_config is None:
        # 如果测试配置参数没给就加载已有测试文件
        app.config.from_pyfile("config.py", silent=True)
    else:
        # 给了就加载配置
        app.config.from_mapping(test_config)
    
    # 确保应用的文件夹时存在的
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass
    
    # hello页面
    @app.route('/hello')
    def hello():
        return "Hello, World!"
    
    
    # 注册数据库相关
    from . import db
    db.init_app(app)  # 这样就把初始化数据库命令和关闭连接函数注册到应用中了
    
    # 这样是不是也行呢？
    app.teardown_appcontext(db.close_db)  # 注册关闭数据库连接的函数
    app.cli.add_command(db.init_db_command)  # 注册初始化数据库的命令


    # 注册蓝图相关
    from . import auth
    app.register_blueprint(auth.bp)
    
    from . import blog
    app.register_blueprint(blog.bp)
    app.add_url_rule("/", endpoint="index")  # 这样`url_for('index')` 或 `url_for('blog.index')` 都会有效，会生成同样的 `/` URL 。

    return app


# if __name__ == '__main__':
#     create_app().run()