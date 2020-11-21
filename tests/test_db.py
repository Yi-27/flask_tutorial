import sqlite3
import pytest
from flaskr.db import get_db

# 测试获取和关闭数据库
def test_get_close_db(app):
    with app.app_context():
        db = get_db()
        assert db is get_db()  # 如果创好了db 就会存在g里，那么重新获取db都是会返回同一个
        
    with pytest.raises(sqlite3.ProgrammingError) as e:
        db.execute("SELECT 1")
    
        assert "closed" in str(e.value)  # 断言有closed字符串在e中
        
# 测试init-db命令行
def test_init_db_command(runner, monkeypatch):
    class Recorder(object):
        called =False
        
    def fake_init_db():
        Recorder.called = True
        
    monkeypatch.setattr("flaskr.db.init_db", fake_init_db)
    result = runner.invoke(args=["init-db"])  # 通过名称
    assert "初始化" in result.output  # click.echo("初始化数据库！")  # 可用于测试获得  # 这里result.output是字符串不是字节
    assert Recorder.called