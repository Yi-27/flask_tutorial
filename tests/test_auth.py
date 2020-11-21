import pytest
from flask import g, session
from flaskr.db import get_db

def test_register(client, app):
    # 模拟get访问注册页面
    assert client.get("/auth/register").status_code == 200
    # 模拟post访问注册页面，注册用户a
    response = client.post(
        "auth/register", data={"username": "a", "password": "a"}
    )
    # 断言这个网址能正确访问
    assert "http://localhost/auth/login" == response.headers["Location"]
    
    # 模拟一个Flask项目运行的上下文，然后查找这个用户a，断言能获取到
    with app.app_context():
        assert get_db().execute(
            "SELECT * FROM user WHERE username = ?;", ("a", )
        ).fetchone() is not None
        

# 测试注册
@pytest.mark.parametrize(("username", "password", "message"),(
        ("", "", "需要填写用户名！".encode()),  # 不加参数默认是utf-8
        ("a", "", "需要填写密码".encode("utf-8")),  # 这里需要给正文字符串转成字节
        ("test", "test", "用户已经注册过了！".encode("utf-8")),
))  # 测试注册时输入框的问题
def test_register_validate_input(client, username, password, message):
    # 模拟post访问测试页面，输入信息用上面的装饰器中的信息，三条都会测试一遍
    response = client.post(
        "/auth/register",
        data={"username": username, "password": password}
    )
    # message不是放在flash中的吗
    assert message in response.data
    
    
# 测试登录
@pytest.mark.parametrize(("username", "password", "message"), (
        ("abc", "test", "用户名为空或不正确！".encode("utf-8")),
        ("test", "abc", "密码为空或不正确！".encode("utf-8")),
))
def test_login_validate_input(auth, username, password, message):
    # 模拟登陆
    response = auth.login(username, password)
    # 判断可有返回消息 这里的返回消息是上面的b""中的字符串
    # 是字节比较
    assert message in response.data
    
    
def test_logout(client, auth):
    auth.login()  # 模拟登陆

    # 用with可以在响应返回之后操作环境变量
    # 通常，在请求之外操作 session 会引发一个异常。
    with client:
        # 模拟登陆
        auth.logout()
        # 注销之后， session 应当不包含 user_id 。
        assert "user_id" not in session