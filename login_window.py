"""
Fenêtre de connexion pour l'application desktop
"""

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                              QLineEdit, QPushButton, QMessageBox, QFrame)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QIcon, QPixmap
import os


class LoginWindow(QWidget):
    """Fenêtre de connexion"""

    # Signal émis lors de la connexion réussie
    login_successful = pyqtSignal(dict)

    def __init__(self, db_manager):
        super().__init__()
        self.db_manager = db_manager
        self.init_ui()

    def init_ui(self):
        """Initialise l'interface utilisateur"""
        self.setWindowTitle("ENASTIC - Connexion")
        self.setFixedSize(500, 450)

        # Définir l'icône de la fenêtre
        icon_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'assets', 'logo.png')
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        self.setStyleSheet("""
            QWidget {
                background-color: #f0f7ff;
            }
            QLabel#title {
                color: #4A90E2;
                font-size: 28px;
                font-weight: bold;
            }
            QLabel#subtitle {
                color: #6B7280;
                font-size: 14px;
            }
            QLineEdit {
                padding: 12px;
                border: 2px solid #E0E0E0;
                border-radius: 8px;
                font-size: 14px;
                background: white;
            }
            QLineEdit:focus {
                border: 2px solid #4A90E2;
            }
            QPushButton#loginBtn {
                background-color: #4A90E2;
                color: white;
                padding: 12px;
                border: none;
                border-radius: 8px;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton#loginBtn:hover {
                background-color: #3B82F6;
            }
            QPushButton#loginBtn:pressed {
                background-color: #2563EB;
            }
            QFrame#loginFrame {
                background: white;
                border-radius: 12px;
                border: 2px solid #E5F0FF;
            }
        """)

        # Layout principal
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(40, 40, 40, 40)
        main_layout.setSpacing(20)

        # En-tête avec logo
        header = QVBoxLayout()
        header.setSpacing(10)

        # Logo ENASTIC
        logo_label = QLabel()
        logo_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'assets', 'logo.png')
        if os.path.exists(logo_path):
            pixmap = QPixmap(logo_path)
            scaled_pixmap = pixmap.scaled(100, 100, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            logo_label.setPixmap(scaled_pixmap)
            logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            header.addWidget(logo_label)

        title = QLabel("ENASTIC")
        title.setObjectName("title")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        subtitle = QLabel("Gestion des Inscriptions")
        subtitle.setObjectName("subtitle")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)

        header.addWidget(title)
        header.addWidget(subtitle)

        # Frame de connexion
        login_frame = QFrame()
        login_frame.setObjectName("loginFrame")

        form_layout = QVBoxLayout()
        form_layout.setContentsMargins(30, 30, 30, 30)
        form_layout.setSpacing(15)

        # Nom d'utilisateur
        username_label = QLabel("Nom d'utilisateur")
        username_label.setStyleSheet("color: #374151; font-weight: 500;")

        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Entrez votre nom d'utilisateur")
        self.username_input.returnPressed.connect(self.handle_login)

        # Mot de passe
        password_label = QLabel("Mot de passe")
        password_label.setStyleSheet("color: #374151; font-weight: 500;")

        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setPlaceholderText("Entrez votre mot de passe")
        self.password_input.returnPressed.connect(self.handle_login)

        # Bouton de connexion
        self.login_btn = QPushButton("Se connecter")
        self.login_btn.setObjectName("loginBtn")
        self.login_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.login_btn.clicked.connect(self.handle_login)

        # Message d'erreur
        self.error_label = QLabel("")
        self.error_label.setStyleSheet("color: #DC2626; font-size: 12px;")
        self.error_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.error_label.setWordWrap(True)
        self.error_label.hide()

        # Ajouter au formulaire
        form_layout.addWidget(username_label)
        form_layout.addWidget(self.username_input)
        form_layout.addWidget(password_label)
        form_layout.addWidget(self.password_input)
        form_layout.addWidget(self.login_btn)
        form_layout.addWidget(self.error_label)

        login_frame.setLayout(form_layout)

        # Info par défaut
        info_label = QLabel("Utilisateur par défaut: admin / admin123")
        info_label.setStyleSheet("color: #9CA3AF; font-size: 11px;")
        info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Assembler le layout principal
        main_layout.addLayout(header)
        main_layout.addWidget(login_frame)
        main_layout.addWidget(info_label)
        main_layout.addStretch()

        self.setLayout(main_layout)

        # Focus sur le champ username
        self.username_input.setFocus()

    def handle_login(self):
        """Gère la tentative de connexion"""
        username = self.username_input.text().strip()
        password = self.password_input.text()

        # Validation
        if not username or not password:
            self.show_error("Veuillez remplir tous les champs")
            return

        # Désactiver le bouton pendant la vérification
        self.login_btn.setEnabled(False)
        self.login_btn.setText("Vérification...")
        self.error_label.hide()

        # Authentification
        user = self.db_manager.authenticate_user(username, password)

        if user:
            # Connexion réussie
            self.login_successful.emit(user)
            self.close()
        else:
            # Échec de la connexion
            self.show_error("Nom d'utilisateur ou mot de passe incorrect")
            self.password_input.clear()
            self.password_input.setFocus()

        # Réactiver le bouton
        self.login_btn.setEnabled(True)
        self.login_btn.setText("Se connecter")

    def show_error(self, message: str):
        """Affiche un message d'erreur"""
        self.error_label.setText(message)
        self.error_label.show()

    def keyPressEvent(self, event):
        """Gère les événements clavier"""
        if event.key() == Qt.Key.Key_Escape:
            self.close()
        super().keyPressEvent(event)
