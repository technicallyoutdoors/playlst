from flask import Blueprint, render_template, request, flash, redirect, url_for, current_app, session, jsonify
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
from .email_utils import generate_reset_token, verify_reset_token, send_email


auth = Blueprint('auth', __name__)


@auth.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        user = User.query.filter_by(email=email).first()
        if user:
            token = generate_reset_token(user.email)
            reset_url = url_for('auth.reset_password', token=token, _external=True)
            text = (
                f"Hi {user.first_name},\n\n"
                f"We received a request to reset your Playlst password. "
                f"Click the link below to choose a new one (it expires in 1 hour):\n\n"
                f"{reset_url}\n\n"
                f"If you didn't request this, you can safely ignore this email."
            )
            html = (
                f"<p>Hi {user.first_name},</p>"
                f"<p>We received a request to reset your Playlst password. "
                f"Click the button below to choose a new one (expires in 1 hour):</p>"
                f"<p><a href=\"{reset_url}\" style=\"background:#66aa33;color:#fff;"
                f"padding:10px 24px;border-radius:999px;text-decoration:none;"
                f"font-weight:bold;display:inline-block\">Reset Password</a></p>"
                f"<p>Or paste this link into your browser:<br>{reset_url}</p>"
                f"<p>If you didn't request this, you can safely ignore this email.</p>"
            )
            send_email(user.email, "Reset your Playlst password", text, html)
        # Always show the same message — don't reveal whether the email exists
        flash("If an account exists for that email, we've sent a reset link.",
              category='success')
        return redirect(url_for('auth.login'))

    return render_template('forgot_password.html', user=current_user)


@auth.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    email = verify_reset_token(token)
    if not email:
        flash("That reset link is invalid or has expired. Please request a new one.",
              category='error')
        return redirect(url_for('auth.forgot_password'))

    user = User.query.filter_by(email=email).first()
    if not user:
        flash("Account not found.", category='error')
        return redirect(url_for('auth.forgot_password'))

    if request.method == 'POST':
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')
        if not password1 or password1 != password2:
            flash("Passwords do not match.", category='error')
        elif len(password1) < 7:
            flash("Password must be more than 7 characters.", category='error')
        else:
            user.password = generate_password_hash(password1, method='pbkdf2:sha256')
            db.session.commit()
            flash("Your password has been updated. Please log in.", category='success')
            return redirect(url_for('auth.login'))

    return render_template('reset_password.html', user=current_user, token=token)


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


TMDB_API_KEY = "28dd9fa4c4a210cd3dc589981c8fb66a"

# TMDB genre id -> name (movie and TV use different id sets)
MOVIE_GENRES = {
    28: 'Action', 12: 'Adventure', 16: 'Animation', 35: 'Comedy', 80: 'Crime',
    99: 'Documentary', 18: 'Drama', 10751: 'Family', 14: 'Fantasy', 36: 'History',
    27: 'Horror', 10402: 'Music', 9648: 'Mystery', 10749: 'Romance',
    878: 'Sci-Fi', 10770: 'TV Movie', 53: 'Thriller', 10752: 'War', 37: 'Western',
}
TV_GENRES = {
    10759: 'Action & Adventure', 16: 'Animation', 35: 'Comedy', 80: 'Crime',
    99: 'Documentary', 18: 'Drama', 10751: 'Family', 10762: 'Kids', 9648: 'Mystery',
    10763: 'News', 10764: 'Reality', 10765: 'Sci-Fi & Fantasy', 10766: 'Soap',
    10767: 'Talk', 10768: 'War & Politics', 37: 'Western',
}


@auth.route('/api/random_pick')
@login_required
def api_random_pick():
    """Return a random movie OR TV show (any genre) as JSON for the swipe deck."""
    media = random.choice(['movie', 'tv'])
    # sort by vote_count.desc + page 1-100 keeps us within the ~2000 most-rated
    # (i.e. famous) titles, so obscure stuff doesn't show up
    page = random.randint(1, 100)
    if media == 'movie':
        url = ("https://api.themoviedb.org/3/discover/movie"
               f"?api_key={TMDB_API_KEY}&language=en-US&sort_by=vote_count.desc"
               f"&include_adult=false&vote_count.gte=300&page={page}")
    else:
        url = ("https://api.themoviedb.org/3/discover/tv"
               f"?api_key={TMDB_API_KEY}&language=en-US&sort_by=vote_count.desc"
               f"&vote_count.gte=100&page={page}")
    try:
        data = requests.get(url, timeout=10).json()
    except Exception:
        return jsonify({'ok': False, 'error': 'tmdb unavailable'}), 502

    results = [t for t in data.get('results', []) if t.get('poster_path')]
    if not results:
        return jsonify({'ok': False, 'error': 'no results'}), 404
    # don't show titles already in the user's Playlst
    owned = set(f.title for f in current_user.favorites)
    fresh = [t for t in results if (t.get('title') or t.get('name', '')) not in owned]
    pick = random.choice(fresh or results)
    gmap = MOVIE_GENRES if media == 'movie' else TV_GENRES
    genres = [gmap[g] for g in pick.get('genre_ids', []) if g in gmap][:2]
    return jsonify({
        'ok': True,
        'title': pick.get('title') or pick.get('name', ''),
        'image': 'https://image.tmdb.org/t/p/w500' + pick['poster_path'],
        'overview': pick.get('overview', ''),
        'media_type': media,
        'genre': ', '.join(genres),
        'year': (pick.get('release_date') or pick.get('first_air_date') or '')[:4],
        'rating': round(pick.get('vote_average') or 0, 1),
    })


@auth.route('/api/save_favorite', methods=['POST'])
@login_required
def api_save_favorite():
    """Add a title to the current user's Playlst (used by swipe-right). JSON."""
    data = request.get_json(silent=True) or {}
    title = (data.get('title') or '').strip()
    image = (data.get('image') or '').strip()
    if not title or not image:
        return jsonify({'ok': False, 'error': 'missing title/image'}), 400
    exists = Favorite.query.filter_by(user_id=current_user.id, title=title).first()
    if exists:
        return jsonify({'ok': True, 'duplicate': True})
    db.session.add(Favorite(title=title, image=image, user_id=current_user.id))
    db.session.commit()
    return jsonify({'ok': True})


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
                            password=generate_password_hash(password1, method='pbkdf2:sha256'))
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
    full_overview = over_view[:20000]
    short_over_view = over_view[:135]

    title = random_title.get('title')

    print(title)

    print(over_view)

    return render_template("movies.html", user=current_user, full_path_random_title_image=full_path_random_title_image, title=title, over_view=over_view, full_overview=full_overview, short_over_view=short_over_view)


@auth.route('/add_favorite_movie', methods=['GET', 'POST'])
@login_required
def add_favorite_movie():
    title = request.form['movie_title']
    image = request.form['movie_image_url']
    user_id = request.form['current_user']
    favorite_exists = Favorite.query.filter_by(
        user_id=current_user.id, title=title).first()
    if favorite_exists:
        flash('title as already been added to your Playlst', category='error')
        return redirect(url_for('auth.movies'))
    global favorites
    new_favorite = Favorite(title=title,
                            user_id=current_user.id, image=image)
    if new_favorite:
        db.session.add(new_favorite)
        db.session.commit()
        flash('Added to PLaylst!', category='success')
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
    # .all() materializes the dynamic relationship to a list so the template's
    # {% if favorites %} empty-state check works (a query object is always truthy)
    return render_template('favorites.html', user=current_user.id, favorites=current_user.favorites.all())


@auth.route('/group_code', methods=['GET', 'POST'])
@login_required
def group_code():
    user = current_user
    code = current_user.code
    return render_template('group_code.html', user=current_user, code=code)


@auth.route('/group_hub', methods=['GET', 'POST'])
@login_required
def group_hub():
    member_photo = current_user.photo
    family = Family.query.filter_by().first()
    return render_template('group_hub.html', user=current_user, family=family, member_photo=member_photo)


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
        flash('You have joined the group! Now start making your PLAYLST',
              category='success')
        return redirect(url_for('auth.group_hub'))
    else:
        flash('Invalid code. Please try again.', category='error')
        return render_template('group_hub.html', user=current_user)


@auth.route('/join_group', methods=['POST', 'GET'])
@login_required
def join_group():
    return render_template('join_group.html', user=current_user)


@auth.route('/search', methods=['GET', 'POST'])
@login_required
def search_title():
    query = request.form.get('query', '').strip()
    results = []

    if query:
        url = "https://api.themoviedb.org/3/search/multi"
        params = {
            "api_key": "28dd9fa4c4a210cd3dc589981c8fb66a",
            "query": query,
            "language": "en-US",
            "page": 1,
            "include_adult": "false"
        }
        response = requests.get(url, params=params)
        data = response.json()
        image_base = "https://image.tmdb.org/t/p/w500"
        owned = set(f.title for f in current_user.favorites)
        for item in data.get('results', []):
            media_type = item.get('media_type')
            if media_type not in ('movie', 'tv'):
                continue
            poster = item.get('poster_path')
            if not poster:
                continue
            title = item.get('title') or item.get('name', '')
            results.append({
                'title': title,
                'image': image_base + poster,
                'overview': item.get('overview', ''),
                'media_type': media_type,
                'already': title in owned,
            })

    return render_template('search.html', user=current_user, results=results, query=query)


@auth.route('/shared_favorites')
@login_required
def shared_favorites():
    family = current_user.family
    if not family:
        flash("You are not a member of a group yet!", category='error')
        return redirect(url_for('auth.join_group'))

    other_members = [m for m in family.members if m.id != current_user.id]
    if not other_members:
        flash("Your group only has one member so far — invite someone to see matches!", category='error')
        return redirect(url_for('auth.group_hub'))

    my_titles = set(fav.title for fav in current_user.favorites)
    shared_titles = my_titles
    for member in other_members:
        shared_titles = shared_titles & set(fav.title for fav in member.favorites)

    favorites = [fav for fav in current_user.favorites if fav.title in shared_titles]

    return render_template('shared_favorites.html', user=current_user, favorites=favorites)


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


@auth.route('/watch')
@login_required
def watch():
    return render_template('watch.html', user=current_user)


TMDB_GENRES = {
    'Action': 28,
    'Comedy': 35,
    'Drama': 18,
    'Horror': 27,
    'Romance': 10749,
    'Sci-Fi': 878,
    'Thriller': 53,
    'Animation': 16,
    'Documentary': 99,
    'Fantasy': 14,
}

@auth.route('/genre', methods=['GET', 'POST'])
@login_required
def genre():
    selected_genre = request.form.get('genre') or request.args.get('genre')
    result = None

    if selected_genre and selected_genre in TMDB_GENRES:
        genre_id = TMDB_GENRES[selected_genre]
        random_page = random.randint(1, 10)
        url = (
            "https://api.themoviedb.org/3/discover/movie"
            f"?api_key=28dd9fa4c4a210cd3dc589981c8fb66a"
            f"&with_genres={genre_id}&language=en-US&sort_by=popularity.desc"
            f"&include_adult=false&page={random_page}&with_watch_monetization_types=flatrate"
        )
        data = requests.get(url).json()
        titles = [t for t in data.get('results', []) if t.get('poster_path')]
        if titles:
            pick = random.choice(titles)
            result = {
                'title': pick.get('title', ''),
                'image': "https://image.tmdb.org/t/p/original" + pick['poster_path'],
                'overview': pick.get('overview', ''),
            }

    return render_template('genre.html', user=current_user, genres=list(TMDB_GENRES.keys()),
                           selected_genre=selected_genre, result=result)


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
