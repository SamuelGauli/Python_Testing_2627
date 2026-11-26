"""Tests de performance Locust pour GUDLFT.

Budgets imposes par les specifications (phase 2) :
  - liste des competitions : moins de 5 secondes
  - mise a jour du total de points : moins de 2 secondes
Nombre d'utilisateurs specifie : 6.

Lancement (serveur deja demarre sur le port 5000) :
  locust -f locustfile.py --headless -u 6 -t 30s
"""
from locust import HttpUser, between, task

BUDGET_COMPETITIONS = 5.0
BUDGET_POINTS = 2.0


class Secretary(HttpUser):
    """Un secretaire de club qui consulte et navigue (lecture seule)."""

    host = 'http://127.0.0.1:5000'
    wait_time = between(1, 2)

    def on_start(self):
        """Chaque simulateur se connecte comme un vrai secretaire."""
        self.client.post('/showSummary',
                         data={'email': 'john@simplylift.co'})

    @task(3)
    def home(self):
        self.client.get('/')

    @task(5)
    def competitions(self):
        """Liste des competitions : budget de 5 secondes."""
        with self.client.get('/showSummary', catch_response=True) as resp:
            elapsed = resp.elapsed.total_seconds()
            if elapsed > BUDGET_COMPETITIONS:
                resp.failure('liste competitions %.2fs > 5s' % elapsed)

    @task(2)
    def standings(self):
        """Total des points : budget de 2 secondes."""
        with self.client.get('/points', catch_response=True) as resp:
            elapsed = resp.elapsed.total_seconds()
            if elapsed > BUDGET_POINTS:
                resp.failure('classement %.2fs > 2s' % elapsed)

    @task(1)
    def booking_page(self):
        self.client.get('/book/Spring%20Festival/Simply%20Lift')
