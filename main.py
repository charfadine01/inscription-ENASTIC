"""
Point d'entrée principal de l'application desktop ENASTIC
"""

import sys
import os
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import Qt

# Ajouter le répertoire parent au path pour les imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from desktop_app.database.db_manager import DatabaseManager
from desktop_app.ui.login_window import LoginWindow
from desktop_app.ui.main_window import MainWindow


class DesktopApp:
    """Application desktop principale"""

    def __init__(self):
        """Initialise l'application"""
        # Créer l'application Qt
        self.app = QApplication(sys.argv)
        self.app.setApplicationName("ENASTIC Inscriptions")
        self.app.setOrganizationName("ENASTIC")

        # Définir l'icône de l'application
        icon_path = os.path.join(os.path.dirname(__file__), 'assets', 'logo.png')
        if os.path.exists(icon_path):
            self.app.setWindowIcon(QIcon(icon_path))

        # Style global
        self.app.setStyle("Fusion")

        # Initialiser la base de données
        db_path = self.get_db_path()
        self.db_manager = DatabaseManager(db_path)

        # Variables
        self.login_window = None
        self.main_window = None
        self.current_user = None

    def get_db_path(self):
        """
        Retourne le chemin de la base de données

        Crée le dossier de données dans le répertoire utilisateur
        """
        # Dossier de données dans le home de l'utilisateur
        home_dir = os.path.expanduser("~")
        app_data_dir = os.path.join(home_dir, ".enastic_inscriptions")

        # Créer le dossier s'il n'existe pas
        os.makedirs(app_data_dir, exist_ok=True)

        return os.path.join(app_data_dir, "enastic_inscriptions.db")

    def show_login(self):
        """Affiche la fenêtre de connexion"""
        self.login_window = LoginWindow(self.db_manager)
        self.login_window.login_successful.connect(self.on_login_success)

        # Centrer la fenêtre
        screen = self.app.primaryScreen().geometry()
        x = (screen.width() - self.login_window.width()) // 2
        y = (screen.height() - self.login_window.height()) // 2
        self.login_window.move(x, y)

        self.login_window.show()

    def on_login_success(self, user_data):
        """
        Callback appelé lors d'une connexion réussie

        Args:
            user_data: Dictionnaire contenant les données de l'utilisateur
        """
        self.current_user = user_data

        # Fermer la fenêtre de connexion
        if self.login_window:
            self.login_window.close()

        # Afficher la fenêtre principale
        self.show_main_window()

    def show_main_window(self):
        """Affiche la fenêtre principale"""
        self.main_window = MainWindow(self.db_manager, self.current_user)

        # Maximiser la fenêtre
        self.main_window.showMaximized()

        # Quand la fenêtre principale se ferme, retourner à la connexion
        self.main_window.destroyed.connect(self.on_main_window_closed)

    def on_main_window_closed(self):
        """Callback appelé quand la fenêtre principale est fermée"""
        self.current_user = None
        self.main_window = None

        # Retourner à la fenêtre de connexion
        self.show_login()

    def run(self):
        """Lance l'application"""
        # Afficher la fenêtre de connexion
        self.show_login()

        # Démarrer la boucle événementielle
        return self.app.exec()


def main():
    """Fonction principale"""
    # Activer le support haute résolution
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )

    # Créer et lancer l'application
    app = DesktopApp()
    sys.exit(app.run())


if __name__ == "__main__":
    main()
