from flask import Blueprint, render_template, request, flash, redirect, url_for, current_app, session
from .models import User, FamilyMember, Photo
from werkzeug.security import generate_password_hash, check_password_hash
from . import db
from flask_login import login_user, login_required, logout_user, current_user
import requests
import random
import json
from .models import Favorite, Family
from . import db
from sqlalchemy import func
from .code_generator import generate_code
import string
import time
from werkzeug.utils import secure_filename
import os


auth = Blueprint('auth', __name__)


@auth.after_request
def add_header(response):
    session.permanent = False
    response.headers["Cache-Control"] = "no-store, max-age=0"
    return response


@auth.route('/main')
def main():
    # csrf_token = generate_csrf()
    # session['csrf_token'] = csrf_token
    return render_template('main.html', css_file='styles.css')


@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()
        if user:
            if check_password_hash(user.password, password):
                login_user(user, remember=True)
                return redirect(url_for('auth.home'))
            else:
                flash('Incorrect password, try again.', category='error')
        else:
            flash('Email does not exist. Please sign up to continue',
                  category='error')

    return render_template("login.html", user=current_user)


@auth.route('/home')
@login_required
def home():
    return render_template('home.html', user=current_user)


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.main'))


@auth.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        email = request.form.get('email')
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')
        user = User.query.filter_by(email=email).first()
        if user:
            flash('Email already exists.', category='error')
        elif len(email) < 4:
            flash('Email must be greater than 4 characters', category='error')
        elif len(first_name) < 2:
            flash('First name must be greater than 2 character', category='error')
        elif password1 != password2:
            flash('Error, password mismatch', category='error')
        elif len(password2) < 7:
            flash('Password must be more than 7 characters', category='error')
        else:
            new_user = User(email=email, first_name=first_name, last_name=last_name,
                            password=generate_password_hash(password1, method='sha256'))
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user, remember=True)
            flash('Account created!', category='success')
            return redirect(url_for('auth.home'))

    return render_template("signup.html", user=current_user)


@auth.route('/movies', methods=['GET', 'POST'])
@login_required
def movies():

    random_page = random.randint(0, 100)

    url1 = "https://api.themoviedb.org/3/discover/movie?api_key=28dd9fa4c4a210cd3dc589981c8fb66a&language=en-US&region=US&sort_by=popularity.desc&include_adult=false&include_video=false&page=" + \
        str(random_page) + "&with_watch_monetization_types=flatrate"
    request1 = requests.get(url1)

    data1 = request1.json()

    titles = data1.get('results')
    random_title = random.choice(titles)
    random_id = random_title.get('id')

    print(random_id)

    random_title_image = random_title.get('poster_path')
    url_append = "https://image.tmdb.org/t/p/original"
    full_path_random_title_image = url_append + random_title_image
    print(full_path_random_title_image)

    over_view = random_title.get('overview')

    title = random_title.get('title')

    print(title)

    print(over_view)

    return render_template("movies.html", user=current_user, full_path_random_title_image=full_path_random_title_image, title=title, over_view=over_view)


@auth.route('/add_favorite_movie', methods=['GET', 'POST'])
@login_required
def add_favorite_movie():
    title = request.form['movie_title']
    image = request.form['movie_image_url']
    user_id = request.form['current_user']
    favorite_exists = Favorite.query.filter_by(
        user_id=current_user.id, title=title).first()
    if favorite_exists:
        flash('title as already been added to playlst', category='error')
        return redirect(url_for('auth.movies'))
    global favorites
    new_favorite = Favorite(title=title,
                            user_id=current_user.id, image=image)
    if new_favorite:
        db.session.add(new_favorite)
        db.session.commit()
        flash('Added to Watchlist!', category='success')
        return redirect(url_for('auth.movies'))

    return render_template('favorites.html', user=current_user, favorites=favorites)


@auth.route('/tvshows', methods=['GET', 'POST'])
@login_required
def tvshows():
    random_page = random.randint(0, 50)

    url2 = "https://api.themoviedb.org/3/discover/tv?api_key=28dd9fa4c4a210cd3dc589981c8fb66a&language=en-US&sort_by=popularity.desc&page=" + \
        str(random_page) + "&timezone=America%2FNew_York&include_null_first_air_dates=false&watch_region=US&with_watch_monetization_types=flatrate&with_status=0&with_type=0"

    request1 = requests.get(url2)

    data1 = request1.json()

    titles = data1.get('results')
    random_title = random.choice(titles)
    random_id = random_title.get('id')

    print(random_id)

    random_title_image = random_title.get('poster_path')
    url_append = "https://image.tmdb.org/t/p/original"
    full_path_random_title_image = url_append + random_title_image
    print(full_path_random_title_image)

    over_view = random_title.get('overview')

    title = random_title.get('name')

    print(title)

    print(over_view)

    return render_template("tvshows.html", user=current_user, full_path_random_title_image=full_path_random_title_image, title=title, over_view=over_view)


@auth.route('/add_favorite_tv_show', methods=['GET', 'POST'])
@login_required
def add_favorite_tv_show():
    title = request.form['tv_show_title']
    image = request.form['tv_show_image_url']
    user_id = request.form['current_user']
    favorite_exists = Favorite.query.filter_by(
        user_id=current_user.id, title=title).first()
    if favorite_exists:
        flash('title as already been added to playlst', category='error')
        return redirect(url_for('auth.tvshows'))
    new_favorite = Favorite(title=title, image=image, user_id=current_user.id)
    if new_favorite:
        db.session.add(new_favorite)
        db.session.commit()
        flash('Added to Playlst!', category='success')
        return redirect(url_for('auth.tvshows'))

    return render_template('favorites.html', user=current_user, favorites=favorites)


@auth.route('/delete_favorite', methods=['POST'])
@login_required
def delete_favorite():
    try:
        title = request.form['title']
        image = request.form['image']
        user_id = request.form['current_user']
        print(title, image, user_id)
        favorite = Favorite.query.filter_by(title=title, image=image, user_id=current_user.id).filter(
            func.lower(Favorite.title) == func.lower(title), func.lower(Favorite.image) == func.lower(image)).first()
        if favorite:
            db.session.delete(favorite)
            db.session.commit()
            flash("Title has been removed", category='success')
        else:
            flash("Title not found", category='error')
    except Exception as e:
        flash("Error while deleting favorite", category='error')
    return redirect(url_for('auth.favorites'))


@auth.route('/favorites', methods=['GET', 'POST'])
@login_required
def favorites():
    user = current_user
    return render_template('favorites.html', user=current_user.id, favorites=current_user.favorites)


@auth.route('/group_code', methods=['GET', 'POST'])
@login_required
def group_code():
    user = current_user
    code = current_user.code
    return render_template('group_code.html', user=current_user, code=code)


@auth.route('/group_hub', methods=['GET', 'POST'])
@login_required
def group_hub():
    family = Family.query.filter_by().first()
    return render_template('group_hub.html', user=current_user, family=family)


@auth.route('/generate_code', methods=['POST', 'GET'])
@login_required
def generate_code():
    user = current_user
    family = user.family

    # Check if user has a family
    if not family:
        code = ''.join(random.choices(
            string.ascii_uppercase + string.digits, k=6))
        # name = request.form['group_name']
        family = Family(code=code)
        family.members.append(user)
        db.session.add(family)
        db.session.commit()
        flash("Code generated successfully", category='success')

    # Update family name if request contains a new name
    elif request.method == 'POST' and 'group_name' in request.form:
        family.name = request.form['group_name']
        db.session.commit()
        flash("Group name updated!", category='success')

    return render_template('group_hub.html', user=current_user, family=family)


@auth.route('/add_member', methods=['GET', 'POST'])
@login_required
def add_member():
    user = current_user
    # if request.method == 'POST':
    code = request.form['code']
    family = Family.query.filter_by(code=code).first()
    if family:
        family.members.append(user)
        db.session.commit()
        flash('You have joined the group!', category='success')
        return redirect(url_for('auth.group_hub'))
    else:
        flash('Invalid code. Please try again.', category='error')
        return render_template('group_hub.html', user=current_user)


@auth.route('/join_group', methods=['POST', 'GET'])
@login_required
def join_group():
    return render_template('join_group.html', user=current_user)


@auth.route('/shared_favorites')
@login_required
def shared_favorites():
    current_user
    family = Family.query.filter(Family.members.contains(current_user)).first()
    if not family:
        flash("You are not a member of a family yet!", category='error')
        return redirect(url_for('auth.join_family'))

# Get shared favorites for each member
    shared_favorites = []
    for member in family.members:
        if member.id != current_user.id:
            member_favorites = set([fav.title for fav in member.favorites])
            shared_favorites.append(member_favorites)

    # Find the intersection of shared favorites
    if shared_favorites:
        shared_favorites = set.intersection(*shared_favorites)
    else:
        shared_favorites = set()

    # Filter favorites to only include shared favorites
    favorites = current_user.favorites.filter(
        Favorite.title.in_(shared_favorites)).all()

    # Convert InstrumentedList objects to regular lists before calling intersection
    favorites_titles = list(set([f.title for f in favorites]))
    favorites_images = list(set([f.image for f in favorites]))

    shared_favorites = Favorite.query.join(User).join(Family).filter(
        Family.code == current_user.family.code,
        Favorite.user_id != current_user.id,
        Favorite.title.in_(favorites_titles),
        Favorite.image.in_(favorites_images)
    ).all()

    return render_template('shared_favorites.html', user=current_user, favorites=shared_favorites)


@auth.route('/leave_group', methods=['POST', 'GET'])
@login_required
def leave_group():
    user = current_user
    family = user.family

    if not family:
        flash('You are not currently a member of any group', 'warning')
        return redirect(url_for('auth.group_hub'))

    family.members.remove(user)
    user.family = None
    db.session.commit()

    flash(f"You have left the group {family.name}.", 'success')
    return redirect(url_for('auth.group_hub'))


@auth.route('/user_profile', methods=['POST', 'GET'])
@login_required
def user_profile():
    profile_photo = None
    if current_user.photo:
        profile_photo = current_user.photo.filepath
    return render_template('user_profile.html', user=current_user, profile_photo=profile_photo)


@auth.route('/edit_user_profile', methods=['POST', 'GET'])
@login_required
def edit_user_profile():
    user = User.query.get(current_user.id)
    user.email = request.form['email']
    user.first_name = request.form['first_name']
    user.last_name = request.form['last_name']
    if request.method == 'POST':
        if 'profile_picture' in request.files:
            profile_picture = request.files['profile_picture']
            if profile_picture:
                filename = secure_filename(profile_picture.filename)
                filepath = os.path.join(
                    current_app.config['UPLOAD_FOLDER'], filename)
                profile_picture.save(filepath)
                if user.photo:
                    user.photo.filename = filename
                    user.photo.filepath = filepath
                else:
                    photo = Photo(filename=filename, filepath=filepath,
                                  user_id=current_user.id)
                    db.session.add(photo)
                    user.photo = photo
        db.session.commit()
        flash("Profile saved!", category='success')
        return redirect(url_for('auth.user_profile'))
    return render_template("user_profile.html", user=current_user)


@auth.route('/random_titles', methods=['POST', 'GET'])
@login_required
def random_titles():

    def random_title_gen():
        global random_title
        title_num_generation = random.randint(1000000, 7221897)
        tt = "tt"
        random_title = tt + str(title_num_generation)
        return random_title

    def get_data():
        url = "https://online-movie-database.p.rapidapi.com/title/get-details"
        querystring = {"tconst": random_title_gen(), "primaryCountry": "US"}
        headers = {
            "X-RapidAPI-Key": "ed1e6a5735mshdcb3f871a40c3abp18177ajsn0bb3cfaa8b87",
            "X-RapidAPI-Host": "online-movie-database.p.rapidapi.com"
        }
        response = requests.request(
            "GET", url, headers=headers, params=querystring)

        try:
            data = json.loads(response.text)
            if data is None:
                raise ValueError("Invalid JSON data")
            return data
        except ValueError:
            return None

    while True:
        data = get_data()
        if data is not None and 'parentTitle' in data and 'title' in data['parentTitle'] and 'image' in data['parentTitle']:
            title_poster = data['parentTitle']['image']['url']
            title = data['parentTitle']['title']
            break
    return render_template("random_titles.html", user=current_user, title_poster=title_poster, title=title)
