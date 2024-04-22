from flask_wtf import FlaskForm
from wtforms.validators import DataRequired, EqualTo, Length
from wtforms import (
    StringField,
    EmailField,
    SubmitField,
    TextAreaField,
    PasswordField,
    FileField,
)
from flask_ckeditor import CKEditorField


# User-Registration-form
class RegisterForm(FlaskForm):
    name = StringField("Enter Name", validators=[DataRequired()])
    email = EmailField("Enter Email", validators=[DataRequired()])
    username = StringField("Enter username", validators=[DataRequired()])
    password = PasswordField(
        "Enter Password",
        validators=[
            DataRequired(),
            EqualTo("confirm_password"),
            Length(min=6, max=8, message="password must be atleast 6 characters"),
        ],
    )
    confirm_password = PasswordField("Confirm Password", validators=[DataRequired()])
    about = StringField("About User", validators=[DataRequired()])
    profile = FileField("Add picture")
    submit = SubmitField()


class LoginForm(FlaskForm):
    email = EmailField("Enter Email", validators=[DataRequired()])
    password = PasswordField("Enter Password", validators=[DataRequired()])
    submit = SubmitField()


class PostForm(FlaskForm):
    title = StringField("Title", validators=[DataRequired()])
    category = StringField("Category", validators=[DataRequired()])
    author = StringField("Author", validators=[DataRequired()])
    slug = StringField("slug", validators=[DataRequired()])
    content = CKEditorField("Write your post here", validators=[DataRequired()])
    thumbnail = FileField("Add Thumbnail", validators=[DataRequired()])
    submit = SubmitField()


class SearchForm(FlaskForm):
    searched = StringField(validators=[DataRequired()])
