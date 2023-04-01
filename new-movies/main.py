from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
import requests

MOVIE_ENDPOINT = "https://api.themoviedb.org/3/search/movie"
MOVIE_API = "389554ab49f2971565d31e24ed5100dd"
MOVIE_DB_INFO_URL = "https://api.themoviedb.org/3/movie"
MOVIE_DB_IMAGE_URL = "https://image.tmdb.org/t/p/w500"

app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
Bootstrap(app)
app.app_context().push()
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///get-movies-collection.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(300), unique=True, nullable=False)
    year = db.Column(db.Integer, nullable=False)
    description = db.Column(db.String(300), nullable=True)
    rating = db.Column(db.Float, nullable=True)
    review = db.Column(db.String(300), nullable=True)
    ranking = db.Column(db.Integer, nullable=True)
    img_url = db.Column(db.String(300), nullable=True)

    def __repr__(self):
        return f'<Movie {self.title}'

db.create_all()

class FindMovie(FlaskForm):
    title= StringField("Enter a title", validators=[DataRequired()])
    submit = SubmitField("Find Movie")

class EditRating(FlaskForm):
    rating = StringField("Add a rating", validators=[DataRequired()])
    review = StringField("Add a review", validators=[DataRequired()])
    submit = SubmitField("Done")
@app.route("/")
def home():
    all_movies = Movie.query.all()
    return render_template("index.html", movies=all_movies)

@app.route('/find', methods=["GET", "POST"])
def find():
    form = FindMovie()
    if form.validate_on_submit():
        params = {
            "query": form.title.data,
            "api_key" : MOVIE_API

        }
        response = requests.get(MOVIE_ENDPOINT, params=params )
        movie_response = response.json()
        movie = movie_response["results"]


        return render_template('select.html', options=movie)
    return render_template("add.html", form=form)

@app.route("/add", methods=["GET", "POST"])
def add():
    movie_id = request.args.get("id")
    selected_movie = Movie.query.get(movie_id)
    if movie_id:
        params = {
            "api_key" : MOVIE_API,
            "language" : "en-US"
        }
        new_movie_endpoint = f"{MOVIE_DB_INFO_URL}/{movie_id}"
        response = requests.get(new_movie_endpoint, params=params)
        movie = response.json()
        title = movie["title"]
        description = movie["overview"]
        year = movie["release_date"]
        img_url = f"{MOVIE_DB_IMAGE_URL}/{movie['poster_path']}"

        add_movies = Movie(title=title,
                           year=year,
                           description=description,
                            img_url=img_url
                           )
        db.session.add(add_movies)
        db.session.commit()

        return redirect(url_for("edit", id=add_movies.id))

@app.route('/edit', methods=["GET","POST"])
def edit():
    form = EditRating()
    movie_id = request.args.get("id")
    movie_update = Movie.query.get(movie_id)
    if form.validate_on_submit():
        movie_update.rating = form.rating.data
        movie_update.review = form.review.data
        db.session.commit()

        return redirect(url_for("home"))
    return render_template('edit.html', form=form)


@app.route('/delete')
def delete():
    movie_id = request.args.get("id")
    movie_delete = Movie.query.get(movie_id)
    db.session.delete(movie_delete)
    db.session.commit()
    return redirect(url_for("home"))


if __name__ == '__main__':
    app.run(debug=True)
