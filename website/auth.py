from flask import Blueprint, render_template, request, flash, redirect, url_for
from .models import User
from werkzeug.security import generate_password_hash, check_password_hash
from . import db
from flask_login import login_user, login_required, logout_user, current_user
import requests
import random
import json
from .models import Favorite
from . import db
# from movie_show_generator import movie_show_generator


auth = Blueprint('auth', __name__)


@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()
        if user:
            if check_password_hash(user.password, password):
                flash('Logged in successfully!', category='success')
                login_user(user, remember=True)
                return redirect(url_for('views.home'))
            else:
                flash('Incorrect password, try again.', category='error')
        else:
            flash('Email does not exist. Please sign up to continue',
                  category='error')

    return render_template("login.html", user=current_user)


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))


@auth.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        email = request.form.get('email')
        first_name = request.form.get('first_name')
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
            new_user = User(email=email, first_name=first_name,
                            password=generate_password_hash(password1, method='sha256'))
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user, remember=True)
            flash('Account created!', category='success')
            return redirect(url_for('views.home'))

    return render_template("signup.html", user=current_user)


@auth.route('/movies', methods=['GET', 'POST'])
def movies():
    global movie_image_url
    global Movie_Title_Name
    global id
    global choice
    email = request.form.get('email')
    user = User.query.filter_by(email=email).first()

    # gets the genre from user and selects a random movie from that genre to display
    # 500/month hard stop requests
    users_input = request.form.get("next")
    url1 = "https://online-movie-database.p.rapidapi.com/title/v2/get-popular-movies-by-genre"
    querystring1 = {"genre": users_input, "limit": "100"}
    headers = {
        "X-RapidAPI-Key": "4aa56d7288msh5be0286e95c8c10p160380jsnfce8a0c61ccd",
        "X-RapidAPI-Host": "online-movie-database.p.rapidapi.com"
    }
    response1 = requests.request(
        "GET", url1, headers=headers, params=querystring1)
    ids = []
    data1 = json.loads(response1.text)

    for id in data1:
        ids.append(id.split("/")[2])
        # res = [sub[2:] for sub in ids]
    choice = random.choice(ids)

    # uses the choice which is an IMDB titleid to asign run through this API to determine the title name, 1000 daily limit
    url2 = "http://www.omdbapi.com/?apikey=b2e0b78b&"
    querystring2 = {"i": choice}
    response2 = requests.request("GET", url2, params=querystring2)
    data2 = json.loads(response2.text)
    Movie_Title_Name = data2['Title']
    print(Movie_Title_Name)

    # gets the image for the title ID from the url2 API only 500 requests/month
    url3 = "https://online-movie-database.p.rapidapi.com/title/get-images"
    querystring3 = {"tconst": choice, "limit": "1"}
    headers = {
        "X-RapidAPI-Key": "4aa56d7288msh5be0286e95c8c10p160380jsnfce8a0c61ccd",
        "X-RapidAPI-Host": "online-movie-database.p.rapidapi.com"
    }
    response3 = requests.request(
        "GET", url3, headers=headers, params=querystring3)
    data3 = json.loads(response3.text)
    movie_image_url = data3["images"][0]["relatedTitles"][0]["image"]["url"]
    print(movie_image_url)

    # if request.method == "POST":
    #     if "favorites" in request.form:
    #         title = request.form['title']
    #         image = request.form['movie_image']
    #         new_favorite = Favorite(title=title, image=image)
    #         print(new_favorite)
    #         # todo add the image url variable picture to the database model - figure out flask's method to storing photos
    #     db.session.add(new_favorite)
    #     db.session.commit()
    #     flash('Added to Watchlist!', category='success')

    return render_template("movies.html", user=current_user, movie_image_url=movie_image_url, Movie_Title_Name=Movie_Title_Name)


@auth.route('/favorites', methods=['GET', 'POST'])
def add_favorite_movie():
    if request.method == 'POST':
        title = request.form['movie_title']
        image = request.form['movie_image_url']
        user_id = request.form['current_user']
        new_favorite = Favorite(title=title, image=image,
                                user_id=current_user.id)
        db.session.add(new_favorite)
        db.session.commit()
        flash('Added to Watchlist!', category='success')
        return redirect(url_for('auth.movies'))
    else:
        favorites = current_user.favorites
    return render_template('favorites.html', user=current_user, favorites=favorites)


@auth.route('/tvshows', methods=['GET', 'POST'])
def tvshows():
    url1 = "https://online-movie-database.p.rapidapi.com/title/get-most-popular-tv-shows"
    querystring1 = {"currentCountry": "US",
                    "purchaseCountry": "US", "homeCountry": "US"}
    headers = {
        "X-RapidAPI-Key": "20719788e5msh46d7f8c7ed9abd9p1d8da2jsnb3f8e9ee7b85",
        "X-RapidAPI-Host": "online-movie-database.p.rapidapi.com"
    }
    response1 = requests.request(
        "GET", url1, headers=headers, params=querystring1)
    tv_show_ids = []
    data1 = json.loads(response1.text)
    for id in data1:
        tv_show_ids.append(id.split("/")[2])
    choice = random.choice(tv_show_ids)

    url2 = "http://www.omdbapi.com/?apikey=b2e0b78b&"
    querystring2 = {"i": choice}
    response2 = requests.request("GET", url2, params=querystring2)
    data2 = json.loads(response2.text)
    Tv_Show_Title_Name = data2['Title']
    print(Tv_Show_Title_Name)

    url3 = "https://online-movie-database.p.rapidapi.com/title/get-images"
    querystring3 = {"tconst": choice, "limit": "1"}
    headers = {
        "X-RapidAPI-Key": "20719788e5msh46d7f8c7ed9abd9p1d8da2jsnb3f8e9ee7b85",
        "X-RapidAPI-Host": "online-movie-database.p.rapidapi.com"
    }
    response3 = requests.request(
        "GET", url3, headers=headers, params=querystring3)
    data3 = json.loads(response3.text)
    tv_show_image_url = data3["images"][0]["relatedTitles"][0]["image"]["url"]

    return render_template("tvshows.html", user=current_user, tv_show_image_url=tv_show_image_url, Tv_Show_Title_Name=Tv_Show_Title_Name)


@auth.route('/add_favorite_tv_show', methods=['GET', 'POST'])
def add_favorite_tv_show():
    global favorites
    if request.method == "POST":
        title = request.form['tv_show_title']
        image = request.form['tv_show_image_url']
        user_id = request.form['current_user']
        new_favorite = Favorite(title=title, image=image, user_id=current_user.id)
        db.session.add(new_favorite)
        db.session.commit()
        flash('Added to Watchlist!', category='success')
        return redirect(url_for('auth.tvshows'))
    else:
        favorites = current_user.favorites
    return render_template('favorites.html', user=current_user, favorites=favorites)

@auth.route('/delete_favorite', methods=['POST'])
def delete_favorite():
    # if favorites.user_id == current_user.id:
    # favorite = Favorite.query.filter_by(title=title, user_id=current_user.id)
    # if favorite:
    title = request.form['title']
    image = request.form['image']
    deletion = title + image 
    db.session.delete(deletion)
    db.session.commit()
    flash("Favorite has been removed", category='success')
    return redirect(url_for('auth.favorites'))
    
