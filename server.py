import functools
import json
from datetime import datetime
from pathlib import Path

from flask import (
    Flask,
    flash,
    redirect,
    render_template,
    request,
    session,
    url_for,
)

BASE_DIR = Path(__file__).resolve().parent
CLUBS_FILE = BASE_DIR / 'clubs.json'
COMPETITIONS_FILE = BASE_DIR / 'competitions.json'


def loadClubs():
    with open(CLUBS_FILE, encoding='utf-8') as c:
        listOfClubs = json.load(c)['clubs']
        return listOfClubs


def loadCompetitions():
    with open(COMPETITIONS_FILE, encoding='utf-8') as comps:
        listOfCompetitions = json.load(comps)['competitions']
        return listOfCompetitions


def saveClubs():
    with open(CLUBS_FILE, 'w', encoding='utf-8') as c:
        json.dump({'clubs': clubs}, c, indent=4, ensure_ascii=False)


def saveCompetitions():
    with open(COMPETITIONS_FILE, 'w', encoding='utf-8') as comps:
        json.dump(
            {'competitions': competitions}, comps, indent=4, ensure_ascii=False
        )


app = Flask(__name__)
app.secret_key = 'something_special'

competitions = loadCompetitions()
clubs = loadClubs()


def currentClub():
    clubName = session.get('club')
    if clubName is None:
        return None
    return next((c for c in clubs if c['name'] == clubName), None)


def competitionIsPast(competition):
    try:
        date = datetime.strptime(competition['date'], '%Y-%m-%d %H:%M:%S')
    except ValueError:
        return False
    return date < datetime.now()


def loginRequired(view):
    @functools.wraps(view)
    def wrapped(*args, **kwargs):
        if currentClub() is None:
            flash("Please log in to access this page.")
            return redirect(url_for('index'))
        return view(*args, **kwargs)
    return wrapped


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/showSummary', methods=['GET', 'POST'])
def showSummary():
    if request.method == 'POST':
        email = request.form.get('email', '')
        club = next((c for c in clubs if c['email'] == email), None)
        if club is None:
            flash("Sorry, we couldn't find an account for that email address.")
            return redirect(url_for('index'))
        session.clear()
        session['club'] = club['name']
        return redirect(url_for('showSummary'))
    club = currentClub()
    if club is None:
        flash("Please log in to access this page.")
        return redirect(url_for('index'))
    pastCompetitions = [
        c['name'] for c in competitions if competitionIsPast(c)
    ]
    return render_template(
        'welcome.html',
        club=club,
        competitions=competitions,
        pastCompetitions=pastCompetitions,
    )


@app.route('/book/<competition>/<club>')
@loginRequired
def book(competition, club):
    foundClub = next((c for c in clubs if c['name'] == club), None)
    foundCompetition = next(
        (c for c in competitions if c['name'] == competition), None
    )
    if foundClub is None:
        flash("This club could not be found-please log in again.")
        return redirect(url_for('index'))
    if foundClub['name'] != session.get('club'):
        flash("Sorry, you can only book places for your own club.")
        return redirect(url_for('index'))
    if foundCompetition is None:
        flash("This competition could not be found-please try again.")
        return redirect(url_for('index'))
    if competitionIsPast(foundCompetition):
        flash("Sorry, this competition is already over.")
        return redirect(url_for('showSummary'))
    return render_template(
        'booking.html', club=foundClub, competition=foundCompetition
    )


@app.route('/purchasePlaces', methods=['POST'])
@loginRequired
def purchasePlaces():
    competitionName = request.form.get('competition', '')
    clubName = request.form.get('club', '')
    competition = next(
        (c for c in competitions if c['name'] == competitionName), None
    )
    club = next((c for c in clubs if c['name'] == clubName), None)
    if competition is None or club is None:
        flash("Sorry, this booking request is not valid-please start again.")
        return redirect(url_for('index'))
    if club['name'] != session.get('club'):
        flash("Sorry, you can only book places for your own club.")
        return redirect(url_for('index'))
    if competitionIsPast(competition):
        flash("Sorry, this competition is already over.")
        return redirect(url_for('showSummary'))

    bookingPage = url_for(
        'book', competition=competitionName, club=clubName
    )
    try:
        placesRequired = int(request.form.get('places', ''))
    except ValueError:
        flash("Please enter a valid number of places.")
        return redirect(bookingPage)

    availablePlaces = int(competition['numberOfPlaces'])
    if placesRequired < 1:
        flash("You must book at least one place.")
        return redirect(bookingPage)
    if placesRequired > 12:
        flash("You cannot book more than 12 places per competition.")
        return redirect(bookingPage)
    if placesRequired > availablePlaces:
        if availablePlaces <= 0:
            flash("Sorry, this competition is full.")
        else:
            flash(
                "Sorry, only %d places are left in this competition."
                % availablePlaces
            )
        return redirect(bookingPage)

    availablePoints = int(club['points'])
    if placesRequired > availablePoints:
        flash(
            "Sorry, you only have %d points and cannot book %d places."
            % (availablePoints, placesRequired)
        )
        return redirect(bookingPage)

    competition['numberOfPlaces'] = availablePlaces-placesRequired
    club['points'] = availablePoints-placesRequired
    saveClubs()
    saveCompetitions()
    flash('Great-booking complete!')
    return redirect(url_for('showSummary'))


@app.route('/points')
def points():
    return render_template('points.html', clubs=clubs)


@app.route('/logout')
def logout():
    session.clear()
    flash("You have been logged out.")
    return redirect(url_for('index'))


if __name__ == "__main__":
    app.run(debug=True)
