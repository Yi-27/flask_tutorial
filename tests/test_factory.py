from flaskr import create_app

# 测试 配置的传递
def test_config():
    assert not create_app().testing
    assert create_app({"TESTING": True}).testing
    

def test_hello(client):
    response = client.get("/hello")  # 模拟浏览器访问hello
    assert response.data == b'Hello, World!'