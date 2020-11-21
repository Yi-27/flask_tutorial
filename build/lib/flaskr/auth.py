import functools

# 导入能用到的flask的包
from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)

from werkzeug.security import check_password_hash, generate_password_hash

from flaskr.db import get_db
# 因为当前的python库的搜索路径时从flask_tutorial开始的
# 所以不能直接from db import get_db，Python的虚拟环境是在flask_tutorial下的


# 创建蓝图
# 第一个参数为 蓝图的名称
# 第二个参数为 蓝图定义的地方
# 第三个参数为 蓝图下所有URL的前缀 比如/auth/abc  /auth/def
bp = Blueprint("auth", __name__, url_prefix="/auth")


# 认证蓝图将包括注册新用户、登录和注销视图。
@bp.route('/register', methods=("GET", "POST"))
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        
        # 获取数据库连接
        db = get_db()
        error = None
        
        # 填没填写其实应该前端来检验，这里只是这样写而已
        if not username or username == "":
            error = "需要填写用户名！"
        elif not password or password == "":
            error = "需要填写密码"
        elif db.execute(
            "SELECT id FROM user WHERE username = ?", (username, )
        ).fetchone() is not None:  # fetchone()用于获取数据库返回数据中的一条数据
            error = "用户已经注册过了！"
            
        if error is None:  # 说明是注册，向数据库中添加该user
            db.execute(
                "INSERT INTO user(username, password) VALUES(?, ?)",
                (username, generate_password_hash(password))  # 将密码hash一下，不明文存
            )
            db.commit()  # 提交事务

            # 重定向回登录页面
            return redirect(url_for("auth.login"))  # 这里url_for()中的参数是login视图函数，这样做就可以自动获取登录的url了，而不是写死它
        
        flash(error)  # 闪存当前error，只有获取一次
        
    return render_template("auth/register.html")


@bp.route('/login', methods=("GET", "POST"))
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
    
        # 获取数据库连接
        db = get_db()
        
        error = None

        user = db.execute(
            "SELECT * FROM user WHERE username = ?", (username, )
        ).fetchone()
        
        if user is None or user == "":  # 这里为用户名为"" 空字符串时也不为空
            error = "用户名为空或不正确！"
        elif not check_password_hash(user['password'], password):
            error = "密码为空或不正确！"
        
        if error is None:
            session.clear()  # 清空session
            session["user_id"] = user['id']  # 记录用户的id
            return redirect(url_for("index"))  # 重定向到主页
        
        flash(error)
        
    return render_template("auth/login.html")


@bp.before_app_request
def load_logged_in_user():
    user_id = session.get("user_id")
    
    if user_id is None:
        g.user = None
    else:
        # 将该用户的信息加载到g中
        # 这里Session只存了user的id，但是g中存了user的所有信息
        g.user = get_db().execute(
            "SELECT * FROM user WHERE id = ?", (user_id, )
        ).fetchone()
        
        
@bp.route("/logout")
def logout():
    session.clear()  # 清除会话
    return redirect(url_for("index"))


# 其他视图的验证
# 定义装饰器，用于检查登录
def login_required(view):  # view为原视图
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:  # 其他视图因为要用user的具体信息，所以用g来判断而不是session，session中只是user_id
            return redirect(url_for("auth.login"))  # 当没有这个用户说明没登录
        
        return view(**kwargs)  # 如果有这个user，原视图继续
    
    return wrapped_view  # 返回这个内函数

