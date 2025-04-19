# Ce fichier permet d'importer facilement les pages de l'application
from pages.dashboard import show as dashboard_show
from pages.indicateurs import show as indicateurs_show
from pages.associes import show as associes_show
from pages.repartition import show as repartition_show
from pages.charges import show as charges_show
from pages.parametres import show as parametres_show

# Alias pour faciliter l'importation
dashboard = type('Dashboard', (), {'show': dashboard_show})()
indicateurs = type('Indicateurs', (), {'show': indicateurs_show})()
associes = type('Associes', (), {'show': associes_show})()
repartition = type('Repartition', (), {'show': repartition_show})()
charges = type('Charges', (), {'show': charges_show})()
parametres = type('Parametres', (), {'show': parametres_show})()
