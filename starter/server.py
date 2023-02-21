"""Server for movie ratings app."""
from flask import (Flask, render_template, request, flash, session,
                    redirect)
from model import connect_to_db, db
import crud

from jinja2 import StrictUndefined

app = Flask(__name__)
app.secret_key = "dev"
app.jinja_env.undefined = StrictUndefined


@app.route("/")
def homepage():
    """View homepage."""

    return render_template('home.html')

@app.route("/movies")
def all_movies():
    """View all movies."""

    movies = crud.get_movies()

    return render_template("all_movies.html", movies=movies)

@app.route("/movies/<movie_id>")
def show_movie(movie_id):
    """Show details on a particular movie."""

    movie = crud.get_movie_by_id(movie_id)

    return render_template("movie_details.html", movie=movie)

@app.route("/users")
def all_users():
    """view all users"""

    users = crud.get_users()

    return render_template("all_users.html", users=users)

@app.route("/users/<user_id>")
def user_profile(user_id):
    """Show user profile given id"""

    user = crud.get_user_by_id(user_id)

    return render_template("user_profile.html", user=user)

@app.route("/users", methods=["POST"])
def register_user():
    """Create a new user."""

    email = request.form.get("email")
    password = request.form.get("password")

    user = crud.get_user_by_email(email)
    if user:
        flash("Account with that email already exists")
    else:
        user = crud.create_user(email, password)
        db.session.add(user)
        db.session.commit()
        flash("Account created successfully")

    return redirect("/")

@app.route("/login", methods=["POST"])
def process_login():
    """Process user login."""

    email = request.form.get("email")
    password = request.form.get("password")

    user = crud.get_user_by_email(email)
    if not user or user.password != password:
        flash("Incorrect email or password. Please try again.")
    else:
        # Log in user by storing the user's email in session
        session["user_email"] = user.email
        flash(f"Welcome back, {user.email}!")

    return redirect("/")

@app.route("/movies/<movie_id>/ratings", methods=["POST"])
def create_rating(movie_id):
    """Give a movie its first rating"""

    logged_in_email = session.get("user_email")
    rating_score = request.form.get("rating")

    if logged_in_email is None:
        flash("Please log in to rate a movie.")
    elif not rating_score:
        flash("Error: no rating selected")
    else:
        user = crud.get_user_by_email(logged_in_email)
        movie = crud.get_movie_by_id(movie_id)

        rating = crud.create_rating(user, movie, int(rating_score))
        db.session.add(rating)
        db.session.commit()

        flash(f" Movie rated {rating_score}/5.")
        
    return redirect(f"/movies/{movie_id}")
    

@app.route("/update_rating", methods=["POST"])
def update_rating():
    rating_id = request.json["rating_id"]
    updated_score = request.json["updated_score"]
    crud.update_rating(rating_id, updated_score)
    db.session.commit()

    return "Rating updated!"

if __name__ == "__main__":
    connect_to_db(app)
    app.run(host="0.0.0.0", debug=True)
