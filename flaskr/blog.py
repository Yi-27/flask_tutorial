from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from flaskr.auth import login_required  # 导入检查登录的装饰器
from flaskr.db import get_db

bp = Blueprint("blog", __name__)

@bp.route("/")
def index():
    db = get_db()
    # 查找所有博客
    posts = db.execute("""SELECT p.id, title, body, created, author_id, username
           FROM post p join user u on p.author_id = u.id
           ORDER BY created DESC;
        """).fetchall()
    
    return render_template("blog/index.html", posts=posts)

@bp.route('/create', methods=("GET", "POST"))
@login_required  # 检查登录状态
def create():
    if request.method == "POST":
        title = request.form["title"]
        body = request.form["body"]
        error = None
        
        if not title or title == "":
            error = "kongtitle"
        
        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                "INSERT INTO post(title, body, author_id) VALUES(?, ?, ?)",
                (title, body, g.user['id'])
            )
            db.commit()
            return redirect(url_for("blog.index"))
    
    return render_template("blog/create.html")


# 获取博文
def get_post(post_id, check_author=True):
    
    # 通过博文的id来获取博文
    post = get_db().execute(
        """
        SELECT p.id, title, body, created, author_id, username
        FROM post p JOIN user u ON p.author_id = u.id
        WHERE p.id = ?;
        """,
        (post_id, )
    ).fetchone()
    
    if post is None:
        abort(404, "%s 博文 不存在"%post_id)
    
    if check_author and post["author_id"] != g.user["id"]:
        abort(403)  # 返回没权限
    
    return post


# 重新编辑博文
@bp.route('/<int:post_id>/update', methods=("GET", "POST"))
@login_required
def update(post_id):
    post = get_post(post_id)
    
    if request.method == "POST":
        title = request.form["title"]
        body = request.form["body"]
        error = None
        
        if not title or title == "":
            error = "kongtitle"
        
        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                """
                UPDATE post set title = ?, body = ?
                WHERE id = ?;
                """,
                (title, body, post_id)
            )
            db.commit()
            return redirect(url_for("blog.index"))
        
    return render_template("blog/update.html", post=post)


# 删除博文
@bp.route('/<int:post_id>/delete', methods=["POST",])
@login_required
def delete(post_id):
    get_post(post_id)  # 这里获取一遍只为了确保是用户本人删除自己的文章
    db = get_db()
    db.execute("DELETE FROM post WHERE id = ?", (post_id, ))
    db.commit()
    return redirect(url_for("blog.index"))