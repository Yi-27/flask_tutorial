import pytest
from flaskr.db import get_db

def test_index(client, auth):
    response = client.get("/")  # 模拟访问主页
    assert b"Log In" in response.data
    assert b"Register" in response.data
    
    # 模拟登陆
    auth.login()
    response = client.get("/")
    # 数据库中已经有一条test用户的博文了
    assert b"Log Out" in response.data  # 页面的数据都在响应的data中了
    assert b"test title" in response.data  # data就是响应对象
    assert "由 test 于 2018-01-01".encode("utf-8") in response.data
    assert b"test\nbody" in response.data
    assert b'href="/1/update"' in response.data
    
    
@pytest.mark.parametrize("path", (
    "/create",
    "/1/update",
    "/1/delete",
))
def test_login_required(client, path):  # 测试必须登陆才能访问这三个页面
    response = client.post(path)
    assert response.headers["Location"] == "http://localhost/auth/login"
    

# 测试博文作者
def test_author_required(app, client, auth):
    with app.app_context():
        db = get_db()
        db.execute("UPDATE post SET author_id = 2 WHERE id = 1")
        db.commit()
        
    auth.login()  # 模拟登陆
    # 当前用户不能修改和删除别的用户的博文
    assert client.post("/1/update").status_code == 403
    assert client.post("/1/delete").status_code == 403
    # 当前用户不能看到别人博文的修改连接
    assert b"href='/1/update'" not in client.get("/").data

@pytest.mark.parametrize("path",(
    "/2/update",
    "/2/delete"
))
def text_exists_required(client, auth, path):
    auth.login()  # 模拟登陆
    # 不存在的博文返回404
    assert client.post(path).status_code == 404


# 测试新建博文
def test_create(client, auth, app):
    auth.login()  # 模拟登陆
    # 能顺利get进新建博文界面
    assert client.get("/create").status_code == 200
    # 模拟post一条博文
    client.post("/create", data={"title": "created", "body":""})
    
    # 模拟flask项目环境
    with app.app_context():
        db = get_db()
        count = db.execute("SELECT COUNT(id) FROM post").fetchone()[0]
        assert count == 2  # 原本就有一条博文，现在又加了一条
    
    
# 测试更新博文
def test_update(client, auth, app):
    auth.login()
    # 能正常访问更新页面
    assert client.get("/1/update").status_code == 200
    # 测试更新页面的post请求
    client.post("/1/update", data={"title": "update", "body": "",})
    
    with app.app_context():
        # 获取数据库连接
        db = get_db()
        # 获取第一条博文信息
        post = db.execute("SELECT * FROM post WHERE id = 1").fetchone()
        # 判断它title字段是不是update，是的话上面的post请求就成功了
        assert post["title"] == "update"
        
    
@pytest.mark.parametrize("path", (
    "/create",
    "/1/update"
))
def test_create_update_validate(client, auth, path):
    auth.login()
    # 测试空标题可能得到想要的提示信息
    response = client.post(path, data={"title": "", "body": "",})
    assert b"kongtitle" in response.data
    

# 测试删除博文，并且会重定向会index页
def test_delete(client, auth, app):
    auth.login()
    response = client.post("/1/delete")
    # 判断是否跳转回主页
    assert response.headers["Location"] == 'http://localhost/'  # 不能忘了最后的 / 啊
    
    with app.app_context():
        db = get_db()
        # 上面成功的话，这里应该是查不出来这个博文的
        post = db.execute("SELECT * FROM post WHERE id = 1;").fetchone()
        assert post is None
        