# 一个小的Flask小项目

## 应用设置

一个 Flask 应用是一个 Flask类的实例。应用的所有东西（例如配置 和 URL ）都会和这个实例一起注册。

创建一个 Flask 应用最粗暴直接的方法是在代码的最开始创建一个全局 Flask实例。有的情况下这样做是简单和有效的，但是当项目越来越大的时候就会有些力不从心了。

可以在一个**函数内部**创建 Flask实例来代替创建全局实例。这个函数被 称为 *应用工厂* 。所有应用相关的配置、注册和其他设置都会在函数内部完成， 然后返回这个应用。



## 应用工厂

创建 `flaskr` 文件夹并且文件夹内添加 `__init__.py` 文件。

 `__init__.py` 有两个作用：

+ 一是包含**应用工厂**；
+ 二是 告诉 Python `flaskr` 文件夹应当视作为一个包。

```python
import os
from flask import Flask

# create_app 是一个应用工厂函数
def create_app(test_config=None):
    # 用于创建和配置Flask应用
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY="dev",
        DATABASE=os.path.join(app.instance_path, "flask.sqlite"),
        # 这里定义了数据库的路径和名称
    )
    
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
        return "Hello world!"

    return app
```

`create_app` 是一个应用工厂函数

1. `app = Flask(__name__, instance_relative_config=True)` 创建 `Flask` 实例。
    - `__name__` 是当前 Python 模块的名称。应用需要知道在哪里设置路径， 使用 `__name__` 是一个方便的方法。
    - `instance_relative_config=True` 告诉应用配置文件是相对于`instance folder`的相对路径。**实例文件夹（默认名字是instance）**在 `flaskr` 包的外面**（flask-tutorial目录下）**，用于存放本地数据（例如配置密钥和数据库），不应当提交到版本控制系统。
2. `app.config.from_mapping()`设置一个应用的 缺省配置：
    - `SECRET_KEY`是被 Flask 和扩展用于保证数据安全的。在开发过程中， 为了方便可以设置为 `'dev'` ，但是在**发布的时候应当使用一个随机值来重载它**。
    - `DATABASE` SQLite 数据库文件存放在路径。它位于 Flask 用于存放实例的 `app.instance_path`之内。
3. `app.config.from_pyfile()`使用 `config.py` 中的值来重载缺省配置，如果 `config.py` 存在的话。 例如，当正式部署的时候，用于设置一个正式的 `SECRET_KEY` 。
    - `test_config` 也会被传递给工厂，并且会替代实例配置。这样可以实现测试和开发的配置分离，相互独立。
4. `os.makedirs()`存在。 Flask 不会自动创建实例文件夹，但是必须确保创建这个文件夹，因为 SQLite 数据库文件会被 保存在里面。
5. `@app.route()`创建一个简单的路由。它创建了 URL `/hello` 和一个函数之间 的关联。这个函数会返回一个响应，即一个 `'Hello, World!'` 字符串。



## 运行应用

现在可以通过使用 `flask` 命令来运行应用。在终端中告诉 Flask 你的应用在哪里， 然后在开发模式下运行应用。

现在还是应当在最顶层的``flask-tutorial`` 目录下，不是在 `flaskr` 包里面。

在Windows下

```
> set FLASK_APP=flaskr 
> set FLASK_ENV=development
> flask run
```

当没指定Flask项目的路径时，会抛异常

```
Could not locate a Flask application.
You did not provide the "FLASK_APP"environment variable, and a "wsgi.py" or "app.py" module was not found in the current directory.
```

意思就是没办法定位到你的项目，指定项目所在的项目文件夹

Flask命令会自动找到`flaskr`包下的`__init__,py`文件，通过工厂函数获得Flask运行实例，并运行它。





## 定义和操作数据库

应用使用一个 SQLite数据库来储存用户和博客内容。 Python 内置了 SQLite 数据库支持，相应的模块为 `sqlite3`。

### 连接数据里

当使用 SQLite 数据库（包括其他多数数据库的 Python 库）时，第一件事就是创建 一个数据库的连接。所有查询和操作都要通过该连接来执行，完事后该连接关闭。

在网络应用中连接往往与请求绑定。在处理请求的某个时刻，连接被创建。在发送响应 之前连接被关闭。

```java
import sqlite3

import click
from flask import current_app, g
from flask.cli import  with_appcontext

# 获取连接
def get_db():
    if "db" not in g:  # g也是用来存储数据
        g.db = sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row

    return g.db

# 关闭连接
def close_db(e=None):
    db = g.pop('db', None)  # 从g中弹出连接
    if db is not None:
        db.close()
```

`g`是一个特殊对象，独立于每一个请求。在处理请求过程中，它可以用于储存 可能**多个函数都会用到的数据**。把**连接储存于其中**，可以多次使用，而不用在同一个 请求中每次调用 `get_db` 时都创建一个新的连接。

`current_app`是另一个特殊对象，**该对象指向处理请求的 Flask 应用**。这里使用了应用工厂，那么在其余的代码中就不会出现应用对象。当应用创建后，在处理一个请求时， `get_db` 会被调用。这样就需要使用 `current_app`。

`sqlite3.connect()` 建立一个数据库连接，该连接指向配置中的 `DATABASE` 指定的文件。这个文件现在还没有建立，后面会在初始化数据库的时候建立该文件。

`sqlite3.Row`告诉连接返回类似于字典的行，这样可以通过列名称来操作 数据。

`close_db` 通过检查 `g.db` 来确定连接是否已经建立。如果连接已建立，那么 就关闭连接。以后会在应用工厂中告诉应用 `close_db` 函数，这样每次请求后就会 调用它。



### 创建表

在 SQLite 中，数据储存在 *表* 和 *列* 中。在储存和调取数据之前需要先创建它们。 Flaskr 会把用户数据储存在 `user` 表中，把博客内容储存在 `post` 表中。下面创建一个文件储存用于创建空表的 SQL 命令：

```sqlite
-- 如果存在这两张表先删除掉
DROP TABLE IF EXISTS user;
DROP TABLE IF EXISTS post;

CREATE TABLE user(
  id INTEGER PRIMARY KEY AUTOINCREMENT, -- int型主键自增
  username TEXT UNIQUE NOT NULL,
  password TEXT NOT NULL
);

CREATE TABLE post(
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  author_id INTEGER NOT NULL,
  created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ,
  title TEXT NOT NULL,
  body TEXT NOT NULL,
  FOREIGN KEY (author_id) REFERENCES user(id)
);
```

在 `db.py` 文件中添加 Python 函数，用于运行这个 SQL 命令：

```python
# 初始化数据库
def init_db():
    # 获取连接
    db = get_db()
    
    # 打开sql文件
    with current_app.open_resource('schema.sql') as f:
        # 读取文件中sql语句，然后执行它
        db.executescript(f.read().decode("utf8"))


@click.command("init-db")
@with_appcontext  # ？？？不知道干啥用的 # 应该是用于获取当前应用运行的上下文环境
def init_db_command():
    # 初始化数据库（若已存在表就删除）
    init_db()
    click.echo("初始化数据库！")
```

`open_resource()`打开一个文件，该文件名是相对于 `flaskr` 包的。这样就不需要考虑以后应用具体部署在哪个位置。 `get_db` 返回一个数据库连接，用于执行文件中的命令。

`click.command()`定义一个名为 `init-db` 命令行，它调用 `init_db` 函数，并为用户显示一个成功的消息。 



## 在应用中注册

`close_db` 和 `init_db_command` 函数需要在应用实例中注册，否则无法使用。 然而，既然我们使用了工厂函数，那么在写函数的时候应用实例还无法使用。代替地， 我们写一个函数，把应用作为参数，在函数中进行注册。

```python
# 注册到应用中
def init_app(app):
    app.teardown_appcontext(close_db)  # 注册关闭数据库连接的函数
    app.cli.add_command(init_db_command)  # 注册初始化数据库的命令
```

`app.teardown_appcontext()`告诉 Flask 在返回响应后进行清理的时候调用此函数。

`app.cli.add_command()`添加一个新的 可以与 `flask` 一起工作的命令。命令行中的`flask`是小写的。

在`__init__.py`工厂中导入并调用这个函数。在工厂函数中把**新的代码放到函数的尾部**，返回**应用代码的前面**。

```python
def create_app():
    app = ...
    # ...
    
    from . import db
    # db.init_app(app)  # 这样就把初始化数据库命令和关闭连接函数注册到应用中了
    # 这样是不是也行呢？
    app.teardown_appcontext(db.close_db)  # 注册关闭数据库连接的函数
    app.cli.add_command(db.init_db_command)  # 注册初始化数据库的命令
    
    return app
```



### 初始化数据库文件

现在 `init-db` 已经在应用中注册好了，可以与 `flask` 命令一起使用了。 使用的方式与前面的 `run` 命令类似。

`flask init-db`

现在会有一个 `flaskr.sqlite` 文件出现在项目所在文件夹的 `instance` 文件夹中。



## 蓝图和视图

视图是一个应用**对请求进行响应的函数**，常称为**视图函数**。

Flask 通过模型（templates，也即HTML文件）把进来的请求 URL 匹配到对应的处理视图。

视图返回数据， Flask把数据变成出去的响应。

Flask 也可以反过来，根据**视图的名称**和**参数**生成URL 。



### 创建蓝图

`Blueprint`是一种**组织一组相关视图**及**其他代码**的方式。

与把视图及其他代码直接注册到应用的方式不同

蓝图方式是**把它们注册到蓝图**，然后**在工厂函数中把蓝图注册到应用**。

Flaskr有两个蓝图，一个用于**认证功能**，另一个用于**博客帖子管理**。每个蓝图的代码都在一个单独的模块中。使用博客首先需要认证，因此先写认证蓝图。

```python
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
bp = Blueprint("auth", __name__, url_prefix="/auth")
```

这里创建了一个名称为 `'auth'` 的 `Blueprint`。和应用对象一样， 蓝图需要知道是在哪里定义的，因此把 `__name__` 作为函数的第二个参数。 `url_prefix` 会添加到所有与该蓝图关联的 URL 前面。

使用 `app.register_blueprint()`导入并注册蓝图。新的代码放在工厂函数的尾部返回应用之前。



认证蓝图将包括**注册新用户**、**登录**和**注销**三个视图。

#### 注册视图函数

当用访问 `/auth/register` URL 时，`register` 视图会返回用于填写注册内容的表单的HTML。当用户提交表单时，视图会验证表单内容，然后要么再次 显示表单并显示一个出错信息，要么创建新用户并显示登录页面。

```python
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
        if not username:
            error = "需要填写用户名！"
        elif not password:
            error = "需要填写密码"
        elif db.execute(
            "SELECT id FROM user WHERE username = ?", (username, )
        ).fetchone() is not None:  # fetchone()用于获取数据库返回数据中的一条数据
            error = "用户已经登录了！"
            
        if error is None:  # 说明是注册，向数据库中添加该user
            db.execute(
                "INSERT INTO user(username, password) VALUES(?, ?)",
                (username, generate_password_hash(password))  # 将密码hash一下，不明文存
            )
            db.commit()  # 提交事务
            return redirect(url_for("auth.login"))  # 重定向回登录页面
        
        flash(error)  # 闪存当前error，只有获取一次
        
    return render_template("auth/register.html")
```

这个 `register` 视图做了以下工作：

1. `@bp.route`关联了 URL `/register` 和 `register` 视图函数。当 Flask 收到一个指向 `/auth/register` 的请求时就会调用 `register` 视图并把其返回值作为响应。

2. 如果用户提交了表单，那么 `request.method`将会是 `'POST'` 。这咱情况下 会开始验证用户的输入内容。

3. `request.form`是一个特殊类型的 `dict` ，其映射了提交表单的键和值。表单中，用户将会输入其 `username` 和 `password` 。

4. 验证 `username` 和 `password` 不为空。

5. 通过查询数据库，检查是否有查询结果返回来验证 `username` 是否已被注册。 `db.execute`使用了带有 `?` 占位符 的 SQL 查询语句。**占位符可以代替后面的元组参数中相应的值**。使用占位符的 好处是会自动帮你转义输入值，以抵御 *SQL 注入攻击* 。

    `fetchone()`根据查询返回**一个**记录行。 如果查询没有结果，则返回 `None` 。后面还用到 `fetchall()` ，它返回包括**所有**结果的列表。

6. 如果验证成功，那么在数据库中插入新用户数据。为了安全原因，不能把密码明文储存在数据库中。相代替的，使用 `generate_password_hash()`生成安全的哈希值并储存到数据库中。查询修改了数据库是的数据后使用 meth:db.commit() <sqlite3.Connection.commit> 保存修改。

7. 用户数据保存后将转到登录页面。 `url_for()`**根据登录视图的名称生成相应的 URL** 。与写固定的 URL 相比， 这样做的好处是如果以后需要修改该视图相应的 URL ，那么不用修改所有涉及到 URL 的代码。 `redirect()` 为生成的 URL 生成一个重定向响应。

8. 如果验证失败，那么会向用户显示一个出错信息。 `flash()`用于储存在渲染模块时可以调用的信息。

9. 当用户最初访问 `auth/register` 时，或者注册出错时，应用显示一个注册表单。 `render_template()`会渲染一个包含 HTML 的模板。



### 登录视图函数

```python
@bp.route('/login', methods=("GET", "POST"))
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
    
        # 获取数据库连接
        db = get_db()
        
        error = None

        user = db.execute(
            "SELECT username, password FROM user WHERE username = ?", (username, )
        ).fetchone()
        
        if user is None:
            error = "用户名为空或不正确！"
        elif not check_password_hash(user['password'], password):
            error = "密码为空或不正确！"
        
        if error is None:
            session.clear()  # 清空session
            session["user_id"] = user['id']  # 记录用户的id
            return redirect(url_for("index"))  # 重定向到主页
        
        flash(error)
        
    return render_template("auth/login.html")
```

与 `register` 有以下不同之处：

1. 首先需要查询用户并存放在变量中，以备后用。
2. `check_password_hash()`以相同的方式哈希提交的密码并安全的比较哈希值。如果匹配成功，那么密码就是正确的。
3. `session`，它用于储存**横跨请求**的值。当验证 成功后，用户的 `id` 被储存于一个新的会话中。会话数据被储存到一个向浏览器发送的 *cookie* 中，**在后继请求中，浏览器会返回它**。 Flask 会安全的对数据进行 *签名* 以防数据被篡改。

现在用户的 `id` 已被储存在 `session`中，可以被后续的请求使用。 请每个请求的开头，如果用户已登录，那么其用户信息应当被载入，以使其可用于其他视图。

```python
@bp.before_app_request
def load_logged_in_user():
    user_id = session.get("user_id")
    
    if user_id is None:
        g.user = None
    else:
        # 将该用户的信息加载到g中
        g.user = get_db().execute(
            "SELECT * FROM user WHERE id = ?", (user_id, )
        ).fetchone()
```

`bp.before_app_request()`注册一个在**视图函数之前运行的函数**，不论其URL是什么。 `load_logged_in_user` 检查用户 id 是否已经储存在 `session`中，并从数据库中获取用户数据，然后储存在 `g.user`中。 `g.user`的持续时间比请求要长。 如果没有用户 id ，或者 id 不存在，那么 `g.user` 将会是 `None` 。



### 注销视图

注销的时候需要把用户 id 从 `session`中移除。 然后 `load_logged_in_user` 就不会在后继请求中载入用户了。

```python
@bp.route("/logout")
def logout():
    session.clear()  # 清除会话
    return redirect(url_for("index"))
```

在登录的地方也继续会话清除了，只是为了确保被清除了



### 其他视图函数中的验证

用户登录以后才能创建、编辑和删除博客帖子。在每个视图中可以使用 *装饰器* 来完成这个工作。

```python
# 其他视图的验证
# 定义装饰器
def login_required(view):  # view为原视图
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:  # 其他视图因为要用user的具体信息，所以用g来判断而不是session，session中只是user_id
            return redirect(url_for("auth.login"))  # 当没有这个用户说明没登录
        
        return view(**kwargs)  # 如果有这个user，原视图继续
    
    return wrapped_view  # 返回这个内函数
```

装饰器返回一个新的视图，该视图包含了传递给装饰器的**原视图**。新的函数检查用户 是否已载入。

如果已载入，那么就继续正常执行原视图，否则就重定向到登录页面。 会在博客视图中使用这个装饰器。



### 端点和URL

`url_for()`函数根据视图名称和发生成 URL 。**视图相关联的名称**亦称为 *端点* ，缺省情况下，端点名称与视图函数名称相同。

例如，上面被加入应用工厂的 `hello()` **视图端点**为 `'hello'` ，可以使用 `url_for('hello')` 来连接。如果视图有参数who，那么可使用 `url_for('hello', who='World')` 连接。

当使用蓝图的时候，蓝图的名称会添加到函数名称的前面。上面的 `login` 函数的**端点**为 `'auth.login'` ，因为它已被加入 `'auth'` 蓝图中。



## 模板

应用已经写好验证视图，但是如果现在运行服务器的话，无论访问哪个 URL ，都会 看到一个 `TemplateNotFound` 错误。这是因为视图调用了 `render_template()`，但是模板还没有写。

模板文件会储存在 `flaskr` 包内的 `templates` 文件夹内。

模板是包含**静态数据**和**动态数据占位符**的文件。模板使用指定的数据生成最终的文档。 Flask 使用 **Jinja2模板**库来渲染模板。

在 Flask 中， Jinja 被配置为 *自动转义* HTML 模板中的任何数据。即**渲染用户的输入是安全的**。 任何用户输入的可能出现歧意的字符，如 `<` 和 `>` ，会被 *转义* ，替换为 *安全* 的值。这些值在浏览器中看起来一样，但是没有副作用。**即在页面是还是显示 `<` 和 `>` ，而不是渲染成HTML标签。**

Jinja 看上去并且运行地很像 Python 。 Jinja 语句与模板中的静态数据通过特定的 **分界符分隔**。 任何位于 `{{` 和 `}}` 之间的东西是一个会输出到最终文档的**静态式**。 `{%` 和 `%}` 之间的东西表示**流程控制**语句，如 `if` 和 `for` 。与 Python 不同，代码块使用分界符分隔，而不是使用缩进分隔。因为代码块内的 静态文本可以会改变缩进。

### 基础布局

应用中的每一个页面主体不同，但是基本布局是相同的。每个模板会 *扩展*（或继承） 同一个 基础模板并重载相应的小节，而不是重写整个 HTML 结构。

**base.html**

```html
<!DOCTYPE html>
<title>{% block title %}{% endblock%} -Flaskr</title>
<link rel="stylesheet" href="{{ url_for('static', filename='style.css') }}">
<nav>
    <h1>Flaskr</h1>
    <ul>
        {% if g.user%}
            <li><span>{{ g.user["username" }}</span></li>
            <li><a href="{{ url_for('auth.logout' }}">Log Out</a></li>
        {% else %}
            <li><a href="{{ url_for('auth.register' }}">Register</a></li>
            <li><a href="{{ url_for('auth.login' }}">Log In</a></li>
        {% endif %}
    </ul>
</nav>
<section class="content">
    <header>
        {% block header %}{% endblock %}
    </header>
    {% for message in get_flashed_message() %}
        <div class="flash">{{ message }}</div>
    {% endfor %}
    {% block content %}{% endblock %}
</section>
```

[`g`](https://dormousehole.readthedocs.io/en/latest/api.html#flask.g) 在模板中自动可用。 根据 `g.user` 是否被设置（在 `load_logged_in_user` 中进行），要么显示 用户名和注销连接，要么显示注册和登录连接。 

`url_for()`也是自动可用的，可用于生成视图的 URL ，而不用手动来指定。

在标题下面，正文内容前面，模板会循环显示 `get_flashed_messages()`返回 的每个消息。在视图中使用 `flash()`来处理出错信息，在模板中就可以这样 显示出出来。

模板中定义三个块，这些块会被其他模板重载。

1. `{% block title %}` 会改变显示在浏览器标签和窗口中的标题。
2. `{% block header %}` 类似于 `title` ，但是会改变页面的标题。
3. `{% block content %}` 是每个页面的具体内容，如登录表单或者博客帖子。

其他模板直接放在 `templates` 文件夹内。为了更好地管理文件，属于某个蓝图的模板会被放在与蓝图同名的文件夹内（文件夹也是在templates中的）。



### 注册模板页面

```html
{% extends 'base.html' %}
{% block header %}
    <!-- 不但可以设置 `title` 块，还可以把其值作为 `header` 块的内容-->
    <h1>{% block title %}Register{% endblock %}</h1>
{% endblock %}

{% block content %}
    <form method="post">
        <label for="username">Username</label>
        <!--required 表示该表单必填-->
        <input type="text" name="username" id="username" required>
        <label for="password">Password</label>
        <input type="password" name="password" id="password" required>
        <input type="submit" value="注册">
    </form>
{% endblock %}
```

`{% extends 'base.html' %}` 告诉 Jinja 这个模板基于基础模板，并且需要**替换相应的块**。所有替换的内容必须位于 `{% block %}` 标签之内。

一个实用的模式是把 `{% block title %}` 放在 `{% block header %}` 内部。 这里不但可以设置 `title` 块，还可以把其值作为 `header` 块的内容， 一举两得。

`input` 标记使用了 `required` 属性。这是告诉浏览器这些字段是必填的。 如果用户使用不支持这个属性的旧版浏览器或者不是浏览器的东西创建的请求， 那么还是要在视图中验证输入数据。

**总是在服务端中完全验证数据**，即使客户端已经做了一些验证，这一点非常重要。



### 登录

```html
{% extends "base.html" %}

{% block header %}
    <h1>{% block title %}Log In{% endblock %}</h1>
{% endblock %}

{% block content %}
<form method="post">
    <label for="username">Username</label>
    <!--required 表示该表单必填-->
    <input type="text" name="username" id="username" required>
    <label for="password">Password</label>
    <input type="password" name="password" id="password" required>
    <input type="submit" value="登录">
</form>
{% endblock %}
```

在不填写表单的情况，尝试点击 “Register” 按钮，浏览器会显示出错信息。

在 `register.html` 中删除 `required` 属性后再次点击 “Register” 按钮。 页面会重载并显示来自于视图中的 `flash()`的出错信息，而不是浏览器显示 出错信息。

填写用户名和密码后会重定向到登录页面。尝试输入错误的用户名，或者输入正常的 用户名和错误的密码。如果登录成功，那么会看到一个出错信息，因为还没有写登录 后要转向的 `index` 视图。



## 静态文件

验证视图和模板已经可用了，但是看上去很朴素。可以使用一些CSS给 HTML 添加点样式。样式不会改变，所以应当使用 *静态文件* ，而不是模板。

Flask 自动添加一个 `static` 视图，视图使用相对于 `flaskr/static` 的相对路径。 `base.html` 模板已经使用了一个 `style.css` 文件连接：

```
{{ url_for('static', filename='style.css') }}
```

除了 CSS ，其他类型的静态文件可以是 JavaScript 函数文件或者 logo 图片。它们 都放置于 `flaskr/static` 文件夹中，并使用 `url_for('static', filename='...')` 引用。



## 博客蓝图

博客蓝图与验证蓝图所使用的技术一样。博客页面应当列出所有的帖子，允许已登录 用户创建帖子，并允许帖子作者修改和删除帖子。



定义博客蓝图并注册到应用工厂。

**blog.py**

```python
from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from flaskr.auth import login_required
from flaskr.db import get_db

bp = Blueprint("blog", __name__)
```

使用 `app.register_blueprint()`在工厂中 导入和注册蓝图。将新代码放在工厂函数的尾部，返回应用之前。

```python
from . import blog
app.register_blueprint(blog.bp)
app.add_url_rule("/", endpoint="index")
```

与验证蓝图不同，博客蓝图没有 `url_prefix` （想有也可以加，但没必要）。因此 `index` 视图会用于 `/` ， `create` 会用于 `/create` ，以此类推。博客是 Flaskr 的主要功能，因此把博客索引作为主索引是合理的。（即博客主页，作为主页）

但是， `index` 视图的端点会被定义为 `blog.index` 。一些验证视图会指定向普通的 `index` 端点。 我们使用 `app.add_url_rule()` 关联端点名称 `'index'` 和 `/` URL ，**这样 `url_for('index')` 或 `url_for('blog.index')` 都会有效，会生成同样的 `/` URL 。**

在其他应用中，可能会在工厂中给博客蓝图一个 `url_prefix` 并定义一个独立的 `index` 视图，类似前文中的 `hello` 视图。在这种情况下 `index` 和 `blog.index` 的端点和 URL 会有所不同。



## 索引

索引会显示所有帖子，最新的会排在最前面。为了在结果中包含 `user` 表中的作者信息，使用了一个 `JOIN` 。

**blog.py**

```python
@bp.route("/")
def index():
    db = get_db()
    # 查找所有博客
    posts = db.execute(
        """SELECT p.id, title, body, created, author_id, username
           FROM post p join user u on p.author_id = u_id
           ORDER BY created DESC;
        """
    ).fetchall()
    
    return render_template("blog/index.html", posts=posts)
```

**index.html**

```html
{% extends "base.html" %}

{% block header %}
    <h1>{% block title %}博客{% endblock %}</h1>
    {% if g.user%}
        <a class="action" href="{{ url_for('blog.create') }}">写博客</a>
    {% endif %}
{% endblock %}

{% block content %}
    {% for post in posts %}
        <article class="post">
            <header>
                <!-- 标题头写明 博客标题 和 作者 和 日期-->
                <div>
                    <h1>{{ post['title'] }}</h1>
                    <div class="about">由 {{ post["username"] }} 于 {{ post["created"].strftime("%Y-%m-%d") }}</div>
                </div>
                {% if g.user["id"] == post["author_id"] %}
                    <a class="action" href="{{ url_for('blog.update', post_id=post['id']) }}">编辑</a>
                {% endif %}
            </header>
            <p class="body">{{ post['body'] }}</p>
        </article>

        <!--判断可是最后一篇博客，不是就是加一条线，隔开两篇博客-->
        {% if not loop.last %}
            <hr>
        {% endif %}
    {% endfor %}
{% endblock %}
```

当用户登录后， `header` 块添加了一个指向 `create` 视图的连接。当用户是 博客作者时，可以看到一个“ 编辑”连接，指向 `update` 视图。 `loop.last` 是一个 Jinja for 循环内部可用的特殊变量，它用于在每个博客帖子后面显示一条线来分隔帖子，最后一个帖子除外。



### 创建博文

`create` 视图与 `register` 视图原理相同。要么显示表单，要么发送内容已通过验证且内容已加入数据库，或者显示一个出错信息。

先前写的 `login_required` 装饰器用在了博客视图中，这样用户必须登录以后才能访问这些视图，否则会被重定向到登录页面。

**blog.py**

```python
@bp.route('/create', methods=("GET", "POST"))
@login_required  # 检查登录状态
def create():
    if request.method == "POST":
        title = request.form["title"]
        body = request.form["body"]
        error = None
        
        if not title:
            error = "请写标题"
        
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
```

**create.html**

```html
{% extends 'base.html' %}

{% block header %}
    <h1>{% block title %}新增博文{% endblock %}</h1>
{% endblock %}

{% block content %}
    <form method="post">
        <label for="title">标题</label>
        <!--required 表示该表单必填-->
        <input type="text" name="title" id="title" value="{{ request.form['title'] }}" required>
        <label for="body">正文</label>
        <textarea name="body" id="body">{{ request.form['body'] }}</textarea>
        <input type="submit" value="发表">
    </form>
{% endblock %}
```

### 重新编辑博文

`update` 和 `delete` 视图都需要通过 `id` 来获取一个 `post` ，并且检查作者与登录用户是否一致。为避免重复代码，可以写一个函数来获取 `post` ， 并在每个视图中调用它。

**blog.py**

```python
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
        abort(403)  # 返回禁止访问
    
    return post
```

`abort()`会引发一个特殊的异常，返回一个 HTTP 状态码。它有一个可选参数， 用于显示出错信息，若不使用该参数则返回缺省出错信息。 `404` 表示“未找到”， `403` 代表“禁止访问”。（ `401` 表示“未授权”，但是我们重定向到登录 页面来代替返回这个状态码）

`check_author` 参数的作用是函数可以用于在不检查作者的情况下获取一个 `post` 。这主要用于显示一个独立的帖子页面的情况，因为这时用户是谁没有关系， 用户不会修改帖子。

**blog.py**

```python
# 重新编辑博文
@bp.route('/<int:post_id>/update', methods=("GET", "POST"))
@login_required
def update(post_id):
    post = get_post(post_id)
    
    if request.method == "POST":
        title = request.form["title"]
        body = request.form["body"]
        error = None
        
        if not title:
            error = "请写标题"
        
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
```

和所有以前的视图不同， `update` 函数有一个 `post_id` 参数。该参数对应路由中 的 `<int:post_id>` 。

使用起来比如， `/1/update` 。 

+ Flask 会捕捉到 URL 中的 `1` ，确保其为一个 `int`，并将其作为 `post_id` 参数传递给视图。 
+ 如果没有指定 `int:` 而是仅仅写了 `<id>` ，那么将会传递一个字符串。
+ 要生成一个指向重新编辑页面的 URL ，需要传递 `post_id` 参数给 `url_for()`： `url_for('blog.update', id=post['id'])` 。前文的 `index.html` 文件中同样如此。

`create` 和 `update` 视图看上去是相似的。 主要的不同之处在于 `update` 视图使用了一个 `post` 对象和一个 `UPDATE` 查询代替了一个 `INSERT` 查询。**这是可以整合在一起的，类似JDBC里学的那样**。

**update.html**

```html
{% extends 'base.html' %}

{% block header %}
    <h1>{% block title %}重写编辑 “{{ post['title'] }}”{% endblock %}</h1>
{% endblock %}

{% block content %}

    <form method="post">
        <label for="title">标题</label>
        <!--required 表示该表单必填-->
        <input type="text" name="title" id="title" value="{{ request.form['title'] }}" required>
        <label for="body">正文</label>
        <textarea name="body" id="body">{{ request.form['body'] or post['body'] }}</textarea>
        <input type="submit" value="发表">
    </form>
    <hr>
    <form action="{{ url_for('blog.delete', post_id=post['id']) }}" method="post">
        <input class="danger" type="submit" value="删除" onclick="return confirm('你确定吗？');">
    </form>
{% endblock %}
```

这个模板有两个表单。第一个提交已编辑过的数据给当前页面（ `/<post_id>/update` ）。 另一个表单只包含一个按钮。它指定一个 `action` 属性，指向删除视图。这个按钮 使用了一些 JavaScript 用以在提交前显示一个确认对话框。

参数 `{{ request.form['title'] or post['title'] }}` 用于选择在表单显示什么 数据。当表单还未提交时，显示**原** `post` 数据。但是，如果提交了**非法数据**，然后需要显示这些非法数据以便于用户修改时，就显示 `request.form` 中的数据。 (比如标题没提交，就要保证正文内容不被清空，但这是在没有require的情况下)。这里当前项目并没有做一些非法数据检查

`request`是又一个自动在模板中可用的变量。



### 删除

删除视图没有自己的模板。删除按钮已包含于 `update.html` 之中，该按钮指向 `/<post_id>/delete` URL 。既然没有模板，该视图只处理 `POST` 方法并重定向到 `index` 视图。

**blog.py**

```python
# 删除博文
@bp.route('/<int:post_id/delete', methods=["POST",])  # 注意这里
@login_required
def delete(post_id):
    get_post(post_id)  # 这里获取一遍只为了确保是用户本人删除自己的文章
    db = get_db()
    db.execute("DELETE FROM post WHERE id = ?", (id, ))
    db.commit()
    return redirect(url_for("blog.index"))
```

**注意：**methods=["POST",]

就算只有一种请求方法，也要这样写

而且更准确的写法是用元组，即**("POST", )**





## 项目可安装化

项目可安装化是指创建一个项目 *发行* 文件，以使用项目可以安装到其他环境， 就像在你的项目中安装 Flask 一样。这样可以使你的项目如同其他库一样进行部署， 可以使用标准的 Python 工具来管理项目。

可安装化还可以带来如下好处：

- 现在， Python 和 Flask 能够理解如何 `flaskr` 包，是因为你是在项目文件夹中运行的。可安装化后，可以从任何地方导入项目并运行。
- 可以和其他包一样管理项目的依赖，即使用 `pip install yourproject.whl` 来安装项目并安装相关依赖。
- 测试工具可以分离测试环境和开发环境。



### 描述项目

`setup.py` 文件描述项目及其从属的文件。

```python
from setuptools import find_packages, setup
print(find_packages())
"""
Obtaining file:///C:/Users/Jarvis/Desktop/Python%E5%90%8E%E7%AB%AF%E5%AD%A6%E4%B
9%A0/flask_tutorial

"""
setup(
    name="flaskr",
    version="1.0.0",
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        "flask",
    ],
)
```

`packages` 告诉 Python 包所包括的文件夹（及其所包含的 Python 文件）。

 `find_packages()` 自动找到这些文件夹，这样就不用手动写出来。

 为了包含其他文件夹，如静态文件和模板文件所在的文件夹，需要设置 `include_package_data` 。 Python 还需要一个名为 `MANIFEST.in` 文件来说明这些文件有哪些。

```
include flaskr/schema.sql
graft flaskr/static
graft flaskr/templates
global-exclude *.pyc
```

这告诉 Python 复制所有 `static` 和 `templates` 文件夹中的文件， `schema.sql` 文件，但是排除所有字节文件。



## 安装项目

使用 `pip` 在虚拟环境中安装项目。

```
$ pip install -e .
```

这个命令告诉 pip 在当前文件夹中寻找 `setup.py` 并在 *编辑* 或 *开发* 模式下安装。编辑模式是指当改变本地代码后，只需要重新项目。比如改变了项目 依赖之类的元数据的情况下。 **？？？**

可以通过 `pip list` 来查看项目的安装情况。

```
Flask                             1.1.2
flaskr                            1.0.0        c:\users\jarvis\desktop\python后
端学习\flask_tutorial
```

至此，没有改变项目运行的方式， `FLASK_APP` 还是被设置为 `flaskr` ， 还是使用 `flask run` 运行应用。不同的是可以在任何地方运行应用，而不仅仅 是在 `flask-tutorial` 目录下。





## 测试覆盖

为应用写单元测试可以检查代码是否按预期执行。 Flask 提供了测试客户端， 可以模拟向应用发送请求并返回响应数据。

应当尽可能多地进行测试。函数中的代码只有在函数被调用的情况下才会运行。 分支中的代码，如 `if` 块中的代码，只有在符合条件的情况下才会运行。测试 应当覆盖每个函数和每个分支。

越接近 100% 的测试覆盖，越能够保证修改代码后不会出现意外。但是 100% 测试 覆盖不能保证应用没有错误。通常，测试不会覆盖用户如何在浏览器中与应用进行 交互。尽管如此，在开发过程中，测试覆盖仍然是非常重要的。

使用 pytest和 coverage来进行测试和衡量代码。先安装它们：

```
pip install pytest coverage
```

### 配置和固件

测试代码位于 `tests` 文件夹中，该文件夹位于 `flaskr` 包的 *旁边* ， 而不是里面。 `tests/conftest.py` 文件包含名为 *fixtures* （固件）的配置函数。每个测试都会用到这里的函数。

测试位于 Python 模块中，以 `test_` 开头， 并且模块中的每个测试函数也以 `test_` 开头。

每个测试会创建一个新的临时数据库文件，并产生一些用于测试的数据。写一个 SQL 文件来插入数据。

```sql
-- 每个测试会创建一个新的临时数据库文件，
-- 并产生一些用于测试的数据。这个 SQL 文件用来插入数据。
INSERT INTO user(username, password)
VALUES
  ('test', 'pbkdf2:sha256:50000$TCI4GzcX$0de171a4f4dac32e3364c7ddc7c14f3e2fa61f2d17574483f7ffbb431b4acb2f'),
  ('other', 'pbkdf2:sha256:50000$kJPKsz6N$d2d4784f1b030a9761f5ccaeeaca413f27f2ecb76d6168407af962ddce849f79');

INSERT INTO post (title, body, author_id, created)
VALUES
  ('test title', 'test' || x'0a' || 'body', 1, '2018-01-01 00:00:00');
```

`app` 固件会调用工厂并为测试传递 `test_config` 来配置应用和数据库，而 不使用本地的开发配置。

**tests/conftest.py**

```python
import os
import tempfile
import pytest
from flaskr import create_app
from flaskr.db import get_db, init_db

with open(os.path.join(os.path.dirname(__file__), "data.sql"), "rb") as f:
    _data_sql = f.read().decode("utf8")
    

@pytest.fixture
def app():
    
    db_fd, db_path = tempfile.mkstemp()
    
    app = create_app({
        "TESTING": True,
        "DATABASE": db_path,  # 测试数据库文件位置
    })
    
    with app.app_context():
        init_db()  # 初始化数据库
        get_db().executescript(_data_sql)  # 插入数据
        
    yield app
    
    os.close(db_fd)
    os.unlink(db_path)
    
@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def runner(app):
    return app.test_cli_runner()
```

`tempfile.mkstemp()`创建并打开一个临时文件，返回该文件对象和路径。 `DATABASE` 路径被重载，这样它会指向临时路径，而不是实例文件夹。设置好路径之后，数据库表被创建，然后插入数据。测试结束后，临时文件会被关闭并删除。

`TESTING`告诉 Flask 应用处在测试模式下。 Flask 会改变一些内部行为 以方便测试。其他的扩展也可以使用这个标志方便测试。

`client` 固件调用 `app.test_client()`由 `app` 固件创建的应用 对象。测试会使用客户端来向应用发送请求，而不用启动服务器。

`runner` 固件类似于 `client` 。 `app.test_cli_runner()`创建一个运行器， 可以调用应用注册的 Click 命令。

Pytest 通过匹配固件函数名称和测试函数的参数名称来使用固件。例如 下面要写 `test_hello` 函数有一个 `client` 参数。 Pytest 会匹配 `client` 固件函数，调用该函数，把返回值传递给测试函数。

### 工厂

工厂本身没有什么好测试的，其大部分代码会被每个测试用到。因此如果工厂代码 有问题，那么在进行其他测试时会被发现。

唯一可以改变的行为是传递测试配置。如果没传递配置，那么会有一些缺省配置可 用，否则配置会被重载。

**tests/test_factory.py**

```python
from flaskr import create_app

# 测试 配置的传递
def test_config():
    assert not create_app().testing
    assert create_app({"TESTING", True}).testing
    

def test_hello(client):
    response = client.get("/hello")  # 模拟浏览器访问hello
    assert response.data == b'Hello, World!'
```

工厂中添加了一个 `hello` 路由作为示例。它返回 “Hello, World!” ，因此测试响应数据是否匹配。



### 数据库

在一个应用环境中，每次调用 `get_db` 都应当返回相同的连接。退出环境后， 连接应当已关闭。

**tests/test_db.py**

```python
import sqlite3
import pytest
from flaskr.db import get_db

def test_get_close_db(app):
    with app.app_context():
        db = get_db()
        assert db is get_db()  # 如果创好了db 就会存在g里，那么重新获取db都是会返回同一个
        
    with pytest.raises(sqlite3.ProgrammingError) as e:
        db.execute("SELECT 1")
    
        assert "closed" in str(e.value)  # 断言有closed字符串在e中
```

`init-db` 命令应当调用 `init_db` 函数并输出一个信息。

**tests/test_db.py**

```python
# 测试init-db命令行       
def test_init_db_command(runner, monkeypatch):
    class Recorder(object):
        called =False
        
    def fake_init_db():
        Recorder.called = True
        
    monkeypatch.setattr("flaskr.db.init_db", fake_init_db)
    result = runner.invoke(args=["init-db"])  
    assert "初始化" in result.output  # click.echo("初始化数据库！")  # 可用于测试获得
    assert Recorder.called
```

这个测试使用 Pytest’s `monkeypatch` 固件来替换 `init_db` 函数。 

前文写的 `runner` 固件用于通过名称调用 `init-db` 命令。



### 验证

对于大多数视图，用户需要登录。在测试中最方便的方法是使用**客户端**制作一个 `POST` 请求发送给 `login` 视图。与其每次都写一遍，不如写一个类，用类的方法来做这件事，并使用一个**固件**把它传递给每个测试的客户端。

**tests/conftest.py**

```python
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
    return AuthActions(client)  # 返回测试登录的固件
```

通过 `auth` 固件，可以在调试中调用 `auth.login()` 登录为 `test` 用户。这个用户的数据已经在 `app` 固件中写入了数据。（最刚开始的SQL语句中写明了将这个用户数据插入数据库中

`register` 视图应当在 `GET` 请求时渲染成功。 在 `POST` 请求中，表单数据合法时，该视图应当重定向到登录 URL ，并且用户 的数据已在数据库中保存好。数据非法时，应当显示出错信息。

**tests/test_auth.py**

```python
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
        ("", "", "需要填写用户名！".encode("utf-8")),
        ("a", "", "需要填写密码".encode("utf-8")),
        ("test", "test", "用户已经注册过了！".encode("utf-8")),
))
def test_register_validate_input(client, username, password, message):
    response = client.post(
        "/auth/register",
        data={"username": username, "password": password}
    )
    # message不是放在flash中的吗
    assert message in response.data
```

`client.get()`制作一个 `GET` 请求并 由 Flask 返回 `Response`对象。类似的 `client.post()`制作一个 `POST` 请求， 转换 `data` 字典为表单数据。

为了测试页面是否渲染成功，制作一个简单的请求，并检查是否返回 一个 `200 OK` `status_code`。如果渲染失败， Flask 会返回一个 `500 Internal Server Error` 代码。

当注册视图重定向到登录视图时， `headers`会有一个包含登录 URL 的 `Location` 头部。

`data`以字节方式包含响应的身体。如果想要检测渲染页面中的 某个值，请 `data` 中检测。字节值只能与字节值作比较，如果想比较 Unicode 文本，请使用 `get_data(as_text=True)`

`pytest.mark.parametrize` 告诉 Pytest 以不同的参数运行同一个测试。 这里用于测试不同的非法输入和出错信息，避免重复写三次相同的代码。

`login` 视图的测试与 `register` 的非常相似。后者是测试数据库中的数据， 前者是测试登录之后 `session`应当包含 `user_id` 。

**tests/test_auth.py**

```python
# 测试登录
@pytest.mark.parametrize(("username", "password", "message"), (
        ("a", "test", "用户名为空或不正确！".encode("utf-8")),
        ("test", "a", "密码为空或不正确！".encode("utf-8")),
))
def test_login_validate_input(auth, username, password, message):
    # 模拟登陆
    response = auth.login(username, password)
    # 判断可有返回消息 这里的返回消息是上面的b""中的字符串
    # 是字节比较
    assert message in response.data
```



在 `with` 块中使用 `client` ，可以在响应返回之后操作环境变量，比如 `session`。 通常，在请求之外操作 `session` 会引发一个异常。

`logout` 测试与 `login` 相反。注销之后， `session`应当不包含 `user_id` 。

**tests/test_auth.py**

```python
def test_logout(client, auth):
    auth.login()  # 模拟登陆

    # 用with可以在响应返回之后操作环境变量
    # 通常，在请求之外操作 session 会引发一个异常。
    with client:
        # 模拟登陆
        auth.logout()
        # 注销之后， session 应当不包含 user_id 。
        assert "user_id" not in session
```

### 博客

所有博客视图使用之前所写的 `auth` 固件。调用 `auth.login()` ，并且客户端的后继请求会登录为 `test` 用户。

`index` 索引视图应当显示已添加的测试帖子数据。作为作者登录之后，应当有 编辑博客的连接。

当测试 `index` 视图时，还可以测试更多验证行为。当没有登录时，每个页面 显示登录或注册连接。当登录之后，应当有一个注销连接。

**tests/test_blog.py**

```python
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
    assert b"href='/1/update'" in response
    
```



用户必须登录后才能访问 `create` 、 `update` 和 `delete` 视图。帖子 作者才能访问 `update` 和 `delete` 。否则返回一个 `403 Forbidden` 状态码。如果要访问 `post` 的 `id` 不存在，那么 `update` 和 `delete` 应当返回 `404 Not Found` 。

**tests/test_blog.py**

```python
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
```

对于 `GET` 请求， `create` 和 `update` 视图应当渲染和返回一个 `200 OK` 状态码。当 `POST` 请求发送了合法数据后， `create` 应当在 数据库中插入新的帖子数据， `update` 应当修改数据库中现存的数据。当数据 非法时，两者都应当显示一个出错信息。

**tests/test_blog.py**

```python
# 测试新建博文
def test_create(client, auth, app):
    auth.login()  # 模拟登陆
    # 能顺利get进新建博文界面
    assert client.get("/create").status_code == 200
    # 模拟post一条博文
    client.post("/create", data={"title": "createed", "body":""})
    
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
    response = client.post(path, data={"title": "", "boby": "",})
    assert "请写标题".encode("utf-8") in response.data
    
```

`delete` 视图应当重定向到索引 URL ，并且帖子应当从数据库中删除。

```python
# 测试删除博文，并且会重定向会index页
def test_delete(client, auth, app):
    auth.login()
    response = client.post("/1/delete")
    assert response.headers["Location"] == 'http://localhost/'
    
    with app.app_context():
        db = get_db()
        # 上面成功的话，这里应该是查不出来这个博文的
        post = db.execute("SELECT * FROM post WHERE id = 1;")
        assert post is None
```



### 运行测试

额外的配置可以添加到项目的 `setup.cfg` 文件。这些配置不是必需的，但是 可以使用测试更简洁明了。

```cfg
[tool:pytest]
testpaths = tests

[coverage:run]
branch = True
source = flaskr
```

使用 `pytest` 来运行测试。该命令会找到并且运行所有测试。

```
======================================================================== 
						test session starts ========================================================================
platform win32 -- Python 3.6.4, pytest-6.1.2, py-1.9.0, pluggy-0.13.1
rootdir: C:\Users\Jarvis\Desktop\Python后端学习\flask_tutorial, configfile: setup.cfg, testpaths: tests
collected 21 items                                                                                                                                                   
tests\test_auth.py .......                                               [ 33%]
tests\test_blog.py ..........                  		                    [ 80%]
tests\test_db.py ..                                                     [ 90%]
tests\test_factory.py ..              	                                [100%]

======================================================================== 
						21 passed in 0.95s =========================================================================

```

如果有测试失败， pytest 会显示引发的错误。可以使用 `pytest -v` 得到每个测试的列表，而不是一串点。

可以使用 `coverage` 命令代替直接使用 pytest 来运行测试，这样可以衡量测试 覆盖率。

**coverage run -m pytest**

在终端中，可以看到一个简单的覆盖率报告：

**coverage report**

```
Name                 Stmts   Miss Branch BrPart  Cover
------------------------------------------------------
flaskr\__init__.py      24      0      2      0   100%
flaskr\auth.py          54      0     22      1    99%
flaskr\blog.py          54      1     16      1    97%
flaskr\db.py            25      0      4      0   100%
------------------------------------------------------
TOTAL                  157      1     44      2    99%
```

还可以生成 HTML 报告，可以看到每个文件中测试覆盖了哪些行：

**coverage html**

这个命令在 `htmlcov` 文件夹中生成测试报告，然后在浏览器中打开 `htmlcov/index.html` 查看。



## 部署产品

假设要把应用部署到一个服务器上。下面只是给出如何创建发行文件并进行安装的概览，但是不会具体讨论使用哪种服务器或者软件。可以在用于开发的电脑中设置一个新的虚拟环境，以便于尝试下面的内容。但是建议不要用于部署一个真正的公开应用。

## 构建和安装

当需要把应用部署到其他地方时，需要构建一个发行文件。当前 Python 的标准发行 文件是 *wheel* 格式的，扩展名为 `.whl` 。先确保已经安装好 wheel 库：

```
$ pip install wheel
```

用 Python 运行 `setup.py` 会得到一个命令行工具，以使用构建相关命令。 `bdist_wheel` 命令会构建一个 wheel 发行文件。

```
$ python setup.py bdist_wheel
```

构建的文件为 `dist/flaskr-1.0.0-py3-none-any.whl` 。文件名由项目名称、版 本号和一些关于项目安装要求的标记组成。

复制这个文件到另一台机器， 创建一个新的虚拟环境，然后用 `pip` 安装这个文件。

```
$ pip install flaskr-1.0.0-py3-none-any.whl
```

Pip 会安装项目和相关依赖。

既然这是一个不同的机器，那么需要再次运行 `init-db` 命令，在实例文件夹中 创建数据库。

```
$ export FLASK_APP=flaskr
$ flask init-db
```

当 Flask 探测到它已被安装（不在编辑模式下），它会与前文不同，使用 `venv/var/flaskr-instance` 作为实例文件夹。**（而不是在外部，不是开始时的flask-tutorial）**



### 配置秘钥

在教程开始的时候给了 `SECRET_KEY`一个缺省值。在产品中我们应当设置一 些随机内容。否则网络攻击者就可以使用公开的 `'dev'` 键来修改会话 cookie ，或者其他任何使用密钥的东西。

可以使用下面的命令输出一个随机密钥：

```
$ python -c 'import os; print(os.urandom(16))'

b'_5#y2L"F4Q8z\n\xec]/'
```

在实例文件夹创建一个 `config.py` 文件。工厂会读取这个文件，如果该文件存 在的话。提制生成的值到该文件中。

```
venv/var/flaskr-instance/config.py
SECRET_KEY = b'_5#y2L"F4Q8z\n\xec]/'
```

其他必须的配置也可以写入该文件中。 Flaskr 只需要 `SECRET_KEY` 即可。

## 运行产品服务器

当运行公开服务器而不是进行开发的时候，应当不使用内建的开发服务器 （ `flask run` ）。开发服务器由 Werkzeug 提供，目的是为了方便开发，但是 不够高效、稳定和安全。

替代地，应当选用一个产品级的 WSGI 服务器。例如，使用 Waitress。首先在 虚拟环境中安装它：

```
$ pip install waitress
```

需要把应用告知 Waitree ，但是方式与 `flask run` 那样使用 `FLASK_APP` 不同。需要告知 Waitree 导入并调用应用工厂来得到一个应用对象。

```
$ waitress-serve --call 'flaskr:create_app'

Serving on http://0.0.0.0:8080
```

以多种不同方式部署应用的列表参见 部署方式。使用 Waitress 只是一个示例，选择它是因为它同时支持 Windows 和 Linux 。还有其他许多 WSGI 服务器和部署选项可供选择。



# **我没部署成功！！！**

真奇怪啊