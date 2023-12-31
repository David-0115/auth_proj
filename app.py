from flask import Flask, render_template, redirect, session, flash
from flask_debugtoolbar import DebugToolbarExtension
from models import User, Feedback, connect_db, db
from forms import RegisterForm, LoginForm, FeedbackForm
from sqlalchemy.orm import defer


app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql:///auth_proj"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ECHO"] = True
app.config["SECRET_KEY"] = "abc123"
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

connect_db(app)
toolbar = DebugToolbarExtension(app)


@app.route("/")
def home_page():
    return redirect("/register")


@app.route("/register", methods=["GET", "POST"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        u = form.username.data
        pwd = form.password.data
        eml = form.email.data
        f_nm = form.first_name.data
        l_nm = form.last_name.data

        user = User.sign_up(u, pwd, eml, f_nm, l_nm)
        db.session.add(user)
        db.session.commit()

        flash("Account successfully created", "success")
        session['username'] = user.username
        return redirect(f"/users/{user.username}")

    return render_template("register.html", form=form)


@app.route("/users/<username>")
def show_user(username):
    if User.is_logged_in(username):
        u = session['username']
        user_data = db.session.query(User).options(
            defer(User.password)).filter(User.username == u).first()
        feedback = Feedback.query.filter_by(username=user_data.username).all()

        return render_template(f"user.html", user=user_data, feedback=feedback)
    else:
        flash("Please login to view this page", "danger")
        return redirect("/login")


@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        u = form.username.data
        pwd = form.password.data
        user = User.authenticate(u, pwd)
        if user:
            flash(f"Welcome back, {user.first_name}", "info")
            session['username'] = user.username
            return redirect(f"/users/{user.username}")
        else:
            form.username.errors = ["Invalid username/password"]
    return render_template("login.html", form=form)


@app.route("/logout")
def logout():
    session.pop('username')
    return redirect("/login")


@app.route("/users/<username>/delete", methods=["POST"])
def delete_user(username):
    if User.is_logged_in(username):
        msg = User.delete_user(username)
        if "deleted" in msg:
            flash(f"{msg}", "success")
        else:
            flash(f"msg", "warning")
        return redirect("/")

    else:
        flash(f"{username} must be logged in to perform this action", "danger")
        if session['username']:
            session.pop('username')
        return redirect("/login")


@app.route("/users/<username>/feedback/add", methods=["GET", "POST"])
def add_feedback(username):
    if User.is_logged_in(username):
        form = FeedbackForm()
        if form.validate_on_submit():
            title = form.title.data
            content = form.content.data
            new_feedback = Feedback(
                title=title, content=content, username=username)
            db.session.add(new_feedback)
            db.session.commit()
            flash("Thank you for your feedback", "success")
            return redirect(f"/users/{username}")

        return render_template("feedback.html", form=form)

    else:
        flash(f"{username} must be logged in to perform this action", "danger")
        return redirect("/login")


@app.route("/feedback/<feedback_id>/update", methods=["GET", "POST"])
def edit_feedback(feedback_id):
    feedback = Feedback.query.get_or_404(feedback_id)
    if User.is_logged_in(feedback.username):
        form = FeedbackForm(obj=feedback)
        if form.validate_on_submit():
            feedback.title = form.title.data
            feedback.content = form.content.data
            db.session.add(feedback)
            db.session.commit()
            flash("Your feedback has been updated", "success")
            return redirect(f"/users/{feedback.username}")
        return render_template("update.html", form=form)

    else:
        flash(f"{feedback.username} must be logged in to perform this action", "danger")
        return redirect("/login")


@app.route("/feedback/<feedback_id>/delete", methods=["POST"])
def delete_feedback(feedback_id):
    feedback = Feedback.query.get_or_404(feedback_id)
    u = feedback.username
    if User.is_logged_in(u):
        feedback.delete()
        flash("Your feedback has been deleted", "success")
        return redirect(f"/users/{u}")

    else:
        flash(f"{feedback.username} must be logged in to perform this action", "danger")
        return redirect("/login")
