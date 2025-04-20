# Ce fichier permet d'importer facilement les pages de l'application
from pages.dashboard import show as dashboard_show
from pages.indicateurs import show as indicateurs_show
from pages.associes import show as associes_show
from pages.repartition import show as repartition_show
from pages.charges import show as charges_show
from pages.parametres import show as parametres_show

# Créer des classes simples pour chaque page
class Dashboard:
    @staticmethod
    def show(*args, **kwargs):
        dashboard_show()

class Indicateurs:
    @staticmethod
    def show(*args, **kwargs):
        indicateurs_show()

class Associes:
    @staticmethod
    def show(*args, **kwargs):
        associes_show()

class Repartition:
    @staticmethod
    def show(*args, **kwargs):
        repartition_show()

class Charges:
    @staticmethod
    def show(*args, **kwargs):
        charges_show()

class Parametres:
    @staticmethod
    def show(*args, **kwargs):
        parametres_show()

# Créer des instances de chaque classe
dashboard = Dashboard()
indicateurs = Indicateurs()
associes = Associes()
repartition = Repartition()
charges = Charges()
parametres = Parametres()
