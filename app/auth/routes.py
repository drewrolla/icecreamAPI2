from flask import Blueprint, render_template, request, redirect, url_for, flash
from .forms import EditProfileForm, LoginForm, UserCreationForm
from werkzeug.security import check_password_hash, generate_password_hash

from flask_login import login_user, logout_user, login_required, current_user

from app.models import User, db

auth=Blueprint('auth', __name__, template_folder='authtemplates')

@auth.route('/login', methods=["GET", "POST"])
def logMeIn():
    form = LoginForm()
    if request.method == "POST":
        if form.validate():
            username = form.username.data
            password = form.password.data

            user = User.query.filter_by(username=username).first()
            if user:
                if check_password_hash(user.password, password):
                    flash('Log in successful.', 'success')
                    login_user(user)
                    return redirect(url_for('search.searchIceCream'))
            else:
                flash('Incorrect password', 'danger')
        else:
            flash('Account does not exist.', 'danger')
    return render_template('login.html', form=form)


@auth.route('/logout', methods=["GET", "POST"])
def logMeOut():
    flash("See you later!", 'success')
    logout_user()
    return redirect(url_for('auth.logMeIn'))



@auth.route('/signup', methods=["GET", "POST"])
def SignMeUp():
    form = UserCreationForm()
    if request.method == "POST":
        print('POST req made')
        if form.validate():
            username = form.username.data
            email = form.email.data
            password = form.password.data

            user = User(username, email, password)

            db.session.add(user)
            db.session.commit()

            flash('Account created.', 'success')
            return redirect(url_for('auth.logMeIn'))
        else:
            flash('Invalid input. Please try again.', 'danger')
    else:
        print('GET req made')
    return render_template('signup.html', form=form)

@auth.route('/profile', methods=["GET","POST"])
def editProfile():
    form = EditProfileForm()
    user = User.query.filter_by(id = current_user.id).first()
    if request.method == "POST":
        if form.validate():
            username = form.username.data
            email = form.email.data
            password = form.password.data
            if username != "":
                user.username = username
            if email != "":
                user.email = email
            if password != "":
                user.password = generate_password_hash(password)

            db.session.add(user)
            db.session.commit()
            flash('Profile updated!', 'success')
            return redirect(url_for('auth.logMeIn'))
        else:
            flash('Validation failed.', 'danger')
    return render_template('profile.html', form=form)

@auth.route('/profile/delete', methods=["GET", "POST"])
def delProfile():
    user = User.query.filter_by(id = current_user.id).first()
    if request.method == "POST":
        if user:
            db.session.delete(user)
            db.session.commit()
            flash('Account successfully deleted.', 'success')
            return redirect(url_for('auth.logMeIn'))
    return render_template('delete.html')




#################API#################
@auth.route('/api/signup', methods=["POST"])
def apiSignUp():
    data = request.json

    username = data['username']
    email = data['email']
    password = data['password']

    user = User(username,email,password)

    db.session.add(user)
    db.session.commit()
    return {
        'status': 'ok',
        'message': f"Successfully created user {username}"
    }

from app.apiauthhelper import basic_auth, token_auth

@auth.route('/token', methods=["POST"])
@basic_auth.login_required
def getToken():
    user = basic_auth.current_user()
    return {
        'status': 'ok',
        'message': 'Login successful',
        'data': user.to_dict()
    }


@auth.route('/api/login', methods=["POST"])
def apiLogIn():
    data = request.json
    
    username = data['username']
    password = data['password']

    user = User.query.filter_by(username=username).first()

    if user:
        if check_password_hash(user.password, password):
            return {
                'status': 'ok',
                'message': 'Successfully logged in',
                'data': user.to_dict()
            }
        return {
            'status': 'not ok',
            'message': 'Incorrect password'
        }
    return {
        'status': 'not ok',
        'message': 'Invalid username'
    }
