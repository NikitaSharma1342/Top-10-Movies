from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
import requests

MOVIE_DB_URL = "https://api.themoviedb.org/3/search/movie"
API_KEY = "6a1ca2c93c6c2872ca80cb9cabb24a47"
MOVIE_DB_INFO_URL = "https://api.themoviedb.org/3/movie"
MOVIE_DB_IMAGE_URL = "https://image.tmdb.org/t/p/w500"

app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
Bootstrap(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///movies.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250), unique = True, nullable = False)
    year = db.Column(db.Integer, nullable = False)
    description = db.Column(db.String(500),unique = True)
    rating = db.Column(db.Float, nullable = True)
    ranking = db.Column(db.Integer, nullable = True)
    review = db.Column(db.String(500), nullable = True)
    img_url = db.Column(db.String(250), nullable = False)

db.create_all()

# new_movie = Movie(
#     title = "Photo Booth",
#     year = 2002,
#     description = "Publicist Shepeard Stuart finds himself in a phone booth, pinned down by an extortionist sniper riffle, Unable to leave or recieve outside help, Stuart's negotiation with caller leads to jaw-dropping climax.",
#     rating = 7.3,
#     ranking = 10,
#     review = "My favourite character was the caller.",
#     img_url="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTV3Yot_lqresrmET6RtvmgVsx6KFYjtHG-KA&usqp=CAU"
# )
#
# db.session.add(new_movie)
# db.session.commit()


@app.route("/")
def home():
    all_movies = Movie.query.all()
    for i in range(len(all_movies)):
        all_movies[i].ranking = len(all_movies) - i
    db.session.commit()
    return render_template("index.html", movies = all_movies)

class EditMovieForm(FlaskForm):
    rating = StringField("Your rating out of 10 e.g. 7.5")
    review = StringField("Your review")
    submit = SubmitField("Done")



@app.route("/edit", methods = ["GET", "POST"])
def edit():
    form = EditMovieForm()
    movie_id = request.args.get('id')
    movie = Movie.query.get(movie_id)
    if form.validate_on_submit():
        movie.rating = float(form.rating.data)
        movie.review = form.review.data
        db.session.commit()
        return redirect(url_for('home'))
    return render_template("edit.html", movie=movie, form=form)

@app.route("/delete")
def delete():
    movie_id  = request.args.get('id')
    movie_to_delete = Movie.query.get(movie_id)
    db.session.delete(movie_to_delete)
    db.session.commit()
    return redirect(url_for('home'))


class AddMovieForm(FlaskForm):
    title = StringField("Movie Title", validators=[DataRequired()])
    submit = SubmitField("Add Movie")



@app.route("/add", methods=["GET", "POST"])
def add():
    form = AddMovieForm()
    if form.validate_on_submit():
        movie_title = form.title.data
        response = requests.get(MOVIE_DB_URL, params={"api_key": API_KEY, "query": movie_title })
        data = response.json()["results"]
        return render_template("select.html", options = data)

    return render_template("add.html", form= form)

@app.route("/find")
def find():
    movie_api_id = request.args.get("id")
    if movie_api_id:
        movie_api_url = f"{MOVIE_DB_INFO_URL}/{movie_api_id}"
        response = requests.get(movie_api_url, params={"api_key": API_KEY, "language": "en-US"})
        data = response.json()
        new_movie = Movie(
            title=data["title"],
            year=data["release_date"].split("-")[0],
            img_url=f"{MOVIE_DB_IMAGE_URL}{data['poster_path']}",
            description=data["overview"]

        )
        db.session.add(new_movie)
        db.session.commit()
        return redirect(url_for("home"))


if __name__ == '__main__':
    app.run(debug=True)
