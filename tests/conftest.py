import os
import tempfile
import pytest
from flaskr import create_app
from flaskr.db import get_db, init_db

with open(os.path.join(os.path.dirname(__file__), "data.sql"), "rb") as f:
    _data_sql = f.read().decode("utf8")
    

@pytest.fixture
def app():
    # 创建并打开一个临时文件，返回该文件对象和路径
    db_fd, db_path = tempfile.mkstemp()
    
    app = create_app({
        "TESTING": True,  # 告诉FLASK应用现在是在测试模式
        "DATABASE": db_path,  # 测试数据库文件位置，这样就不会指向instance路径
    })
    
    with app.app_context():
        init_db()  # 初始化数据库
        get_db().executescript(_data_sql)  # 插入数据
        
    yield app
    
    # 关闭删除临时文件
    os.close(db_fd)
    os.unlink(db_path)
    
@pytest.fixture
def client(app):
    return app.test_client()  # 运行测试客户端

@pytest.fixture
def runner(app):
    return app.test_cli_runner()  # 测试固件


# 用于测试登录模块
class AuthActions(object):
    def __init__(self, client):
        self._client = client  # 客户端
        
    def login(self, username="test", password="test"):
        return self._client.post(
            "/auth/login",
            data={"username": username, "password": password}
        )  # 模拟post请求登录，并传参
    
    def logout(self):
        # 模拟注销
        return self._client.get("/auth/logout")
    
    
@pytest.fixture
def auth(client):  # 测试验证的代码
    return AuthActions(client)  # 返回测试验证的固件
    

## 后面test_文件内的test_函数内的client、app、auth/login都是从这里得到的
        
    