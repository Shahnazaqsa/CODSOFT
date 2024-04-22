from flask import (
    Flask,
    render_template,
    flash,
    request,
    redirect,
    url_for,
    send_from_directory,
)
from flask_sqlalchemy import SQLAlchemy
from webforms import RegisterForm, LoginForm, PostForm, SearchForm
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename
import os
import uuid
from datetime import datetime
from flask_login import (
    UserMixin,
    login_required,
    login_user,
    logout_user,
    LoginManager,
    current_user,
)
from sqlalchemy.orm import relationship
from flask_ckeditor import CKEditor
from sqlalchemy import desc

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://root@localhost/blogger"
db = SQLAlchemy(app)
# ----------------------------------------------Ckeditor Configuration
app.config["CKEDITOR_PKG_TYPE"] = "full"
ckeditor = CKEditor(app)
# app.config["CKEDITOR_CONFIGS"] = {
#     "ckeditor": {
#         "imageUploadCallback": "function(imgData) { imgData.element.addClass('content-img'); }"
#     }
# }

# ---------------------------------------- secret key for web forms
app.config["SECRET_KEY"] = "@hiiamshahnaz"

# -------------------------------------------- Upload Folders
UPLOAD_FOLDER = "static/img"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
# ---------------------------------------------login Configuration
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"


@login_manager.user_loader
def load_user(user_id):
    return Register.query.get(int(user_id))


# DATABASE MODELS
class Register(db.Model, UserMixin):
    id = db.Column(db.Integer(), primary_key=True, nullable=False)
    name = db.Column(db.VARCHAR(255), unique=False, nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    username = db.Column(db.VARCHAR(255), unique=True, nullable=False)
    password = db.Column(db.String(), unique=False, nullable=False)
    about = db.Column(db.VARCHAR(255), unique=False, nullable=True)
    profile = db.Column(db.String(), unique=False, nullable=False)
    date = db.Column(db.DateTime(), nullable=False, default=datetime.now())
    # One to many Relation one user cas have multiple posts
    posts = relationship("Posts", backref="poster", cascade="all , delete-orphan")


# posts Model


class Posts(db.Model):
    id = db.Column(db.Integer(), primary_key=True, nullable=False)
    title = db.Column(db.String(), unique=False, nullable=False)
    category = db.Column(db.String(), unique=False, nullable=False)
    slug = db.Column(db.String(), unique=True, nullable=False)
    author = db.Column(db.String(), unique=False, nullable=False)
    content = db.Column(db.Text(), unique=False, nullable=False)
    thumbnail = db.Column(db.String(), unique=False, nullable=True)
    date = db.Column(db.DateTime(), nullable=False, default=datetime.now())
    poster_id = db.Column(db.Integer(), db.ForeignKey("register.id"), nullable=False)


# ----------------------------------------------USER_POST
@app.route("/register", methods=["GET", "POST"])
def add_user():
    form = RegisterForm()
    if form.validate_on_submit():
        # validate the unique email and username
        user_query = Register.query.filter_by(username=form.username.data).first()
        email_query = Register.query.filter_by(email=form.email.data).first()

        if user_query is None and email_query is None:
            final_pic = ""
            if "profile" in request.files:
                profile_pic = request.files["profile"]
                if profile_pic.filename == "":
                    final_pic = "static/img/defaultuser.png"
                else:
                    final_pic = str(uuid.uuid4()) + secure_filename(
                        profile_pic.filename
                    )
                    profile_path = os.path.join(app.config["UPLOAD_FOLDER"], final_pic)
                    profile_pic.save(profile_path)
                    profile_path = os.path.join(app.config["UPLOAD_FOLDER"], final_pic)
                    profile_pic.save(profile_path)

            final_about = (
                form.about.data if form.about.data else "Nothing About The User"
            )

            entry = Register(
                name=form.name.data,
                email=form.email.data,
                username=form.username.data,
                about=final_about,
                password=generate_password_hash(form.password.data),
                profile=final_pic,
            )
            db.session.add(entry)
            db.session.commit()
            flash("Registration successful!", "success")
            return render_template("dashboared.html", form=form)
        else:
            flash(
                "Username or Email Already Exist. Change your username or email",
                "danger",
            )
            return render_template("register.html", form=form)

    return render_template("register.html", form=form)


# ----------------------------------------------Index_Route
@app.route("/")
def index():
    allpost = Posts.query.order_by(Posts.date.desc()).all()[:4]
    latestpost = Posts.query.order_by(Posts.date.desc()).all()[:3]
    newposts = Posts.query.order_by(Posts.date.desc()).all()[:1]
    page = request.args.get("page", default=1, type=int)
    per_page = 4
    posts = (
        db.session.query(Posts)
        .order_by(desc(Posts.id))
        .paginate(page=page, per_page=per_page)
    )
    cat_query = db.session.query(Posts.category).distinct().all()
    cat_list = [cat[0] for cat in cat_query]
    return render_template(
        "index.html",
        post=allpost,
        latestpost=latestpost,
        newposts=newposts,
        posts=posts,
        cat_list=cat_list,
    )


# ----------------------------------------------ADD _ POST
@app.route("/addpost", methods=["GET", "POST"])
@login_required
def addpost():
    form = PostForm()
    if form.validate_on_submit():
        slug_query = Posts.query.filter_by(slug=form.slug.data).first()
        if slug_query is None:
            thumb_pic = ""
            if "thumbnail" in request.files:
                thumb = request.files["thumbnail"]
                if thumb.filename == "":
                    thumb_pic = "static/img/default.png"
                else:
                    thumb_pic = str(uuid.uuid4()) + secure_filename(thumb.filename)
                    thumb_path = os.path.join(app.config["UPLOAD_FOLDER"], thumb_pic)
                    thumb.save(thumb_path)
                post_entry = Posts(
                    title=form.title.data,
                    slug=form.slug.data,
                    author=form.author.data,
                    category=form.category.data,
                    content=form.content.data,
                    thumbnail=thumb_pic,
                    date=datetime.now(),
                    poster_id=current_user.id,
                )
                db.session.add(post_entry)
                db.session.commit()
                flash(
                    "Post Successfully Published",
                    "success",
                )
                return redirect(url_for("index"))
        else:
            flash(
                "Slug Already Exists",
                "danger",
            )
            return render_template("addpost.html", form=form)
    return render_template("addpost.html", form=form)


# ----------------------------------------------Edit _ Post
@app.route("/edit_post/<string:slug>", methods=["GET", "POST"])
@login_required
def edit_post(slug):
    post = Posts.query.filter_by(slug=slug).first_or_404()
    if post.poster_id == current_user.id:
        form = PostForm(obj=post)
        if form.validate_on_submit():
            form.populate_obj(post)
            if (
                "thumbnail" in request.files
                and request.files["thumbnail"].filename != ""
            ):
                thumbnail = request.files["thumbnail"]
                filename = secure_filename(thumbnail.filename)
                thumbnail_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
                thumbnail.save(thumbnail_path)
                post.thumbnail = filename
            db.session.commit()
            flash("Post updated successfully", "success")
            return redirect(url_for("dashboared"))
        return render_template("edit_post.html", form=form, post=post)
    else:
        flash("You can only edit your post", "danger")
        return redirect("/")


# ------------------------------------------------------------ Blog page
@app.route("/blog")
def blog():
    page = request.args.get("page", default=1, type=int)
    per_page = 6
    posts = (
        db.session.query(Posts)
        .order_by(Posts.date.desc())
        .paginate(page=page, per_page=per_page)
    )
    return render_template("blog.html", posts=posts)


# --------------------------------------------------------display Thumbnail picture
@app.route("/display_image/<filename>")
def display_image(filename):
    return send_from_directory(app.config["UPLOAD_FOLDER"], filename)


# ----------------------------------------------View Post
@app.route("/post_view/<string:slug>", methods=["GET"])
def post_view(slug):
    posts = Posts.query.filter_by(slug=slug).first()
    return render_template("post_view.html", post=posts)


# ----------------------------------------------404 Error page
@app.errorhandler(404)
def not_found(error):
    return render_template("error.html")


# -------------------------------------------------Login Route
@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = Register.query.filter_by(email=form.email.data).first()
        if user is None:
            flash("Email does not exist, Check Email and try again", "danger")
            return render_template("login.html", form=form)
        else:
            if user.email == form.email.data and check_password_hash(
                user.password, form.password.data
            ):
                login_user(user)
                flash("Logged in Successfully", "success")
                return render_template("dashboared.html", form=form)
            else:
                flash("Invalid Email or Password", "danger")
                return render_template("login.html", form=form)

    return render_template("login.html", form=form)


# ----------------------------------------------Edit User Profile
@app.route("/edit_user/<int:id>", methods=["GET", "POST"])
@login_required
def edit_user(id):
    form = RegisterForm()
    if current_user.id == id:
        user = Register.query.filter_by(id=id).first()
        if form.validate_on_submit():
            user.name = form.name.data
            user.email = form.email.data
            user.about = form.about.data
            user.username = form.username.data
            if form.password.data:
                user.password = generate_password_hash(form.password.data)

            if "profile" in request.files and request.files["profile"].filename != "":
                profile_pic = request.files["profile"]
                filename = secure_filename(profile_pic.filename)
                final_pic = str(uuid.uuid4()) + filename
                profile_path = os.path.join(app.config["UPLOAD_FOLDER"], final_pic)
                profile_pic.save(profile_path)
                user.profile = final_pic
            else:
                user.profile = "defaultuser.png"

            db.session.commit()
            flash("Save Changes Successfully", "success")
            return redirect(url_for("dashboared"))

        form.name.data = user.name
        form.email.data = user.email
        form.about.data = user.about
        form.username.data = user.username
    else:
        flash("NOT ALLOWED, you can only access your own id", "danger")
        return redirect("/")
    return render_template("edit_user.html", form=form)


# ----------------------------------------------Delete Post Route-----------------------------------------
@app.route("/delete_post/<string:slug>")
@login_required
def delete_post(slug):
    post = Posts.query.filter_by(slug=slug).first_or_404()
    if current_user.id == post.poster_id:
        db.session.delete(post)
        db.session.commit()
        flash("Post removed successfully", "success")
        return render_template("dashboared.html")
    else:
        flash(
            "You can only edit your post",
            "danger",
        )
        return render_template("dashboared.html")


# ----------------------------------------------Logout Route-----------------------------------------
@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Logout Successfully ", "success")
    return redirect("/")


# ----------------------------------------------Dashboared Route-----------------------------------------
@app.route("/dashboared")
@login_required
def dashboared():
    posts = (
        db.session.query(Posts)
        .filter_by(poster_id=current_user.id)
        .order_by(desc(Posts.id))
    )
    return render_template("dashboared.html", posts=posts)


# ----------------------------------------------Search Route-----------------------------------------


@app.context_processor
def layout():
    form = SearchForm()
    return dict(form=form)


@app.route("/search", methods=["GET", "POST"])
def search():
    form = SearchForm()
    searched = ""
    posts = ""
    if form.validate_on_submit():
        posts = Posts.query
        searched = form.searched.data
        # print("Search Query:", searched)  # Debugging statement
        posts = posts.filter(Posts.content.like(f"%{searched}%")).order_by(
            desc(Posts.id)
        )
        # print("Posts Count:", posts.count())  # Debugging statement
        return render_template("search.html", form=form, searched=searched, posts=posts)

    return render_template("search.html", form=form, searched=searched, posts=posts)


# ----------------------------------------------Category Route-----------------------------------------


@app.route("/category")
def category():
    cat_query = db.session.query(Posts).order_by(desc(Posts.id))
    cat_list = []
    for items in cat_query:
        cat = items.category
        if cat in cat_list:
            continue
        else:
            cat_list.append(cat)

    # print(cat_list)
    return render_template("category.html", cat_list=cat_list)


@app.route("/category/<string:cat>")
def view(cat):
    post = db.session.query(Posts).filter_by(category=cat).order_by(desc(Posts.id))
    per_page = 4
    page = request.args.get("page", default=1, type=int)
    posts = post.paginate(per_page=per_page, page=page)
    return render_template("category-view.html", cat=cat, posts=posts)


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)
