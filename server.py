import json
import functools
from flask import Flask,render_template,request,redirect,flash,url_for,session


def loadClubs():
    with open('clubs.json') as c:
         listOfClubs = json.load(c)['clubs']
         return listOfClubs


def loadCompetitions():
    with open('competitions.json') as comps:
         listOfCompetitions = json.load(comps)['competitions']
         return listOfCompetitions


def saveClubs():
    with open('clubs.json', 'w', encoding='utf-8') as c:
        json.dump({'clubs': clubs}, c, indent=4, ensure_ascii=False)


def saveCompetitions():
    with open('competitions.json', 'w', encoding='utf-8') as comps:
        json.dump({'competitions': competitions}, comps, indent=4, ensure_ascii=False)


app = Flask(__name__)
app.secret_key = 'something_special'

competitions = loadCompetitions()
clubs = loadClubs()


def currentClub():
    clubName = session.get('club')
    if clubName is None:
        return None
    return next((c for c in clubs if c['name'] == clubName), None)


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

@app.route('/showSummary',methods=['POST'])
def showSummary():
    email = request.form.get('email', '')
    club = next((c for c in clubs if c['email'] == email), None)
    if club is None:
        flash("Sorry, we couldn't find an account for that email address.")
        return redirect(url_for('index'))
    session.clear()
    session['club'] = club['name']
    return render_template('welcome.html',club=club,competitions=competitions)


@app.route('/book/<competition>/<club>')
@loginRequired
def book(competition,club):
    foundClub = next((c for c in clubs if c['name'] == club), None)
    foundCompetition = next((c for c in competitions if c['name'] == competition), None)
    if foundClub is None:
        flash("This club could not be found-please log in again.")
        return redirect(url_for('index'))
    if foundClub['name'] != session.get('club'):
        flash("Sorry, you can only book places for your own club.")
        return redirect(url_for('index'))
    if foundCompetition is None:
        flash("This competition could not be found-please try again.")
        return redirect(url_for('index'))
    return render_template('booking.html',club=foundClub,competition=foundCompetition)


@app.route('/purchasePlaces',methods=['POST'])
@loginRequired
def purchasePlaces():
    competitionName = request.form.get('competition', '')
    clubName = request.form.get('club', '')
    competition = next((c for c in competitions if c['name'] == competitionName), None)
    club = next((c for c in clubs if c['name'] == clubName), None)
    if competition is None or club is None:
        flash("Sorry, this booking request is not valid-please start again.")
        return redirect(url_for('index'))
    if club['name'] != session.get('club'):
        flash("Sorry, you can only book places for your own club.")
        return redirect(url_for('index'))
    try:
        placesRequired = int(request.form.get('places', ''))
    except ValueError:
        flash("Please enter a valid number of places.")
        return redirect(url_for('book', competition=competitionName, club=clubName))

    availablePlaces = int(competition['numberOfPlaces'])
    if placesRequired < 1:
        flash("You must book at least one place.")
        return redirect(url_for('book', competition=competitionName, club=clubName))
    if placesRequired > 12:
        flash("You cannot book more than 12 places per competition.")
        return redirect(url_for('book', competition=competitionName, club=clubName))
    if placesRequired > availablePlaces:
        if availablePlaces <= 0:
            flash("Sorry, this competition is full.")
        else:
            flash("Sorry, only %d places are left in this competition." % availablePlaces)
        return redirect(url_for('book', competition=competitionName, club=clubName))

    availablePoints = int(club['points'])
    if placesRequired > availablePoints:
        flash("Sorry, you only have %d points and cannot book %d places."
              % (availablePoints, placesRequired))
        return redirect(url_for('book', competition=competitionName, club=clubName))

    competition['numberOfPlaces'] = availablePlaces-placesRequired
    club['points'] = availablePoints-placesRequired
    saveClubs()
    saveCompetitions()
    flash('Great-booking complete!')
    return render_template('welcome.html', club=club, competitions=competitions)


# TODO: Add route for points display


@app.route('/logout')
def logout():
    session.clear()
    flash("You have been logged out.")
    return redirect(url_for('index'))

if __name__ == "__main__":
    app.run(debug=True)