# Intro
```
Hey,

Je viens de recevoir le rapport de QA pour la phase 1 du projet. Il y a plusieurs bogues, dont un qui fait planter l'application ! 
Malheureusement, je ne suis pas au bureau pour les prochains jours (un de mes enfants est tombé malade ce week-end). 
Je ne sais pas encore quand je pourrai être là dans la semaine. Pourriez-vous prendre en charge la mise en œuvre du projet ? 
Vous devrez régler les bogues de la phase 1 et mettre en œuvre les éléments de la phase 2 (j'ai ajouté le travail de la phase 2 et les bogues de la section “issues” du repo). 

Vous devrez cloner et forker le repo et le mettre en place sur votre machine locale (tout ce dont vous avez besoin se trouve dans le fichier README). 
Ensuite, passez en revue les bogues dans la section des problèmes, puis essayez de reproduire les problèmes sur votre machine locale pour résoudre les bogues et ajouter la gestion des erreurs. 
Pour gagner du temps de configuration, nous utilisons Flask et JSON pour éviter d'utiliser une base de données. 
La plupart des outils dont vous aurez besoin se trouvent dans le fichier requirements.txt dans le repo, 
mais vous devrez installer Flask et notre framework de test préféré, pytest, ainsi que notre outil de test de performance, Locust. 

Vous devrez également préparer un rapport de test et un rapport de performances, 
conformément au guide de développement à la fin des spécifications fonctionnelles ci-jointes. 
Veillez à suivre toutes les directives, car le QA nous reproche de ne pas respecter les normes. 
Vous devez tester de manière approfondie les résultats requis (à la fois les happy paths et les sad paths) pour toutes les fonctionnalités de l'application.  
Je vous encourage également à adopter une approche de TDD, car cela vous aidera à rationaliser votre travail. 

Une fois que vous aurez terminé, nous ferons un examen de ce que vous avez dans la branche QA du code. 
Nous examinerons les rapports et la manière dont vous avez résolu les problèmes, 
nous examinerons votre code et nous testerons la couverture de la nouvelle fonctionnalité. 

Merci !

```
1. Why


    This is a proof of concept (POC) project to show a light-weight version of our competition booking platform. The aim is the keep things as light as possible, and use feedback from the users to iterate.

2. Getting Started

    This project uses the following technologies:

    * Python v3.x+ (developed and tested on Python 3.13)

    * [Flask](https://flask.palletsprojects.com/)

        Whereas Django does a lot of things for us out of the box, Flask allows us to add only what we need.
     

    * [venv](https://docs.python.org/3/library/venv.html) (Python virtual environment)

        This ensures you'll be able to install the correct packages without interfering with Python on your machine.
        `venv` ships with Python, so there is nothing extra to install globally.


3. Installation

    - After cloning, change into the directory.

    - Create the virtual environment:

      ```
      python -m venv venv
      ```

    - Activate it:

      * Windows (PowerShell):

        ```
        venv\Scripts\activate
        ```

      * Linux / macOS:

        ```
        source venv/bin/activate
        ```

      You should see that your command prompt has changed to the name of the folder.
      This means that you can install packages in here without affecting files outside.
      To deactivate, type `deactivate`.

    - Install the dependencies in one step:

      ```
      pip install -r requirements.txt
      ```

      This installs Flask **and** the testing/quality tools required by the
      specifications: `pytest`, `pytest-cov`, `coverage`, `flake8` and `locust`.
      If you install a package, make sure others know by updating the
      requirements.txt file. An easy way to do this is `pip freeze > requirements.txt`.

    - Run the application (the entry point is `server.py`):

      ```
      python server.py
      ```

      The app answers on [http://127.0.0.1:5000](http://127.0.0.1:5000).

    - Alternative: run it with the Flask CLI. The file is called `server.py`,
      so Flask cannot guess it by itself (`flask run` fails with
      *Could not locate a Flask application*): you **must** point Flask at it.

      * Windows (PowerShell):

        ```
        $env:FLASK_APP="server.py"
        flask run
        ```

      * Linux / macOS:

        ```
        export FLASK_APP=server.py
        flask run
        ```

      See the [Flask quickstart](https://flask.palletsprojects.com/en/stable/quickstart/#a-minimal-application)
      for more details.

4. Current Setup

    The app is powered by [JSON files](https://www.tutorialspoint.com/json/json_quick_guide.htm). This is to get around having a DB until we actually need one. The main ones are:
     
    * competitions.json - list of competitions (name, date, number of places)
    * clubs.json - list of clubs with relevant information. You can look here to see what email addresses the app will accept for login.

    Every successful reservation is written back to both files, so the data
    survives a restart of the server.

    Demo accounts (secretary email addresses):

    | Club | Email | Points |
    | --- | --- | --- |
    | Simply Lift | john@simplylift.co | 13 |
    | Iron Temple | admin@irontemple.com | 4 |
    | She Lifts | kate@shelifts.co.uk | 12 |

5. Testing

    You are free to use whatever testing framework you like - the main thing is that you can show what tests you are using.
    The tools used by this project are declared in `requirements.txt`.

    * Unit / integration tests: [pytest](https://docs.pytest.org/), tests go into
      the `tests/` folder (that folder is **not** ignored by git any more, it used
      to be and no test could ever be committed).

      ```
      pytest tests/
      ```

      Note: the `tests/` folder only contains a `.gitkeep` at the moment - every
      fix listed in the Git workflow below was verified by running the server
      (see *Manual checks*). `pytest tests/` therefore reports *no tests ran*
      (exit code 5) until automated tests are added there. The specifications
      require at least 60% of coverage before the QA branch is reviewed.

    * Coverage (specification target: at least 60% of the code covered):

      ```
      pytest --cov=server --cov-report=term-missing
      ```

      The [coverage](https://coverage.readthedocs.io/) module can also be used on
      its own: `coverage run -m pytest` then `coverage report -m`.

    * Manual checks: start the app with `python server.py` and exercise both the
      happy paths (valid email, valid booking) and the sad paths (unknown email,
      more than 12 places, competition full, not enough points, past competition).

    * Performance tests: [Locust](https://locust.io/) (6 users by default).
      Budgets from the specifications: a competition list must load in less than
      5 seconds and a points update in less than 2 seconds.

    Please group tests in separate folders (unit / integration / functional) and
    run them from the command line before merging into `main`.

6. Flake8 Report

    [flake8](https://flake8.pycqa.org/) is part of `requirements.txt`. Run it from
    the repository root:

    ```
    flake8 .
    ```

    The settings live in [`.flake8`](.flake8): 79 characters per line, and the
    virtual environment (`venv/`) is excluded so a local install never pollutes
    the report.

    Expected output: **no output at all** (0 errors, PEP 8 / 79 characters per line).
    To keep a text copy of the report for the QA branch:

    ```
    flake8 . > flake8-report.txt
    ```

7. Git workflow and naming conventions

    * `main` is the source of truth (finished code). Everyone should be able to
      clone `main` and run the project.

    * One bug or one feature per branch, named with the type of change
      (see the specifications, "Guide de développement"):

      ```
      bug/<short-description>
      feature/<short-description>
      improvement/<short-description>
      ```

    * Commit messages start with a prefix: `fix:`, `feat:`, `chore:`, `style:`.
      Several commits on one branch are fine when a change needs them.

    * Flow: branch -> reproduce the bug -> fix -> test it (server running) ->
      push the branch -> merge into `main` -> push `main`. Never merge a change
      whose tests are red.
