"""
Gestionnaire de base de données SQLite pour l'application desktop
"""

import sqlite3
import os
import bcrypt
from datetime import datetime
from typing import List, Dict, Optional, Tuple


class DatabaseManager:
    """Gère toutes les opérations de base de données"""

    def __init__(self, db_path: str = "enastic_inscriptions.db"):
        """
        Initialise le gestionnaire de base de données

        Args:
            db_path: Chemin vers le fichier de base de données
        """
        self.db_path = db_path
        self.init_database()

    def get_connection(self):
        """Crée et retourne une connexion à la base de données"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Pour accéder aux colonnes par nom
        return conn

    def init_database(self):
        """Initialise les tables de la base de données"""
        conn = self.get_connection()
        cursor = conn.cursor()

        # Table des utilisateurs (chefs de service)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                nom_complet TEXT NOT NULL,
                role TEXT DEFAULT 'chef_service',
                site TEXT NOT NULL,
                email TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_login TIMESTAMP
            )
        ''')

        # Table des étudiants
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS etudiants (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                matricule TEXT UNIQUE NOT NULL,
                nom TEXT NOT NULL,
                prenoms TEXT NOT NULL,
                genre TEXT NOT NULL,
                date_naissance TEXT NOT NULL,
                lieu_naissance TEXT NOT NULL,
                classe TEXT NOT NULL,
                filiere TEXT NOT NULL,
                option TEXT,
                niveau TEXT,
                regime TEXT DEFAULT 'Normal',
                site_formation TEXT NOT NULL,
                annee_academique TEXT NOT NULL,
                statut TEXT DEFAULT 'En attente',
                numero_bordereau TEXT,
                email TEXT,
                telephone TEXT,
                adresse TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                created_by INTEGER,
                FOREIGN KEY (created_by) REFERENCES users(id)
            )
        ''')

        # Table des paiements
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS paiements (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                etudiant_id INTEGER NOT NULL,
                montant REAL NOT NULL,
                type_paiement TEXT NOT NULL,
                date_paiement TEXT NOT NULL,
                numero_recu TEXT,
                observations TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (etudiant_id) REFERENCES etudiants(id)
            )
        ''')

        # Table des certificats générés
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS certificats (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                etudiant_id INTEGER NOT NULL,
                type_certificat TEXT NOT NULL,
                fichier_path TEXT NOT NULL,
                annee_academique TEXT NOT NULL,
                date_generation TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                genere_par INTEGER,
                FOREIGN KEY (etudiant_id) REFERENCES etudiants(id),
                FOREIGN KEY (genere_par) REFERENCES users(id)
            )
        ''')

        # Table de configuration
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS configuration (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Table d'historique des modifications
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS historique (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                action TEXT NOT NULL,
                table_name TEXT NOT NULL,
                record_id INTEGER,
                details TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        ''')

        # Index pour améliorer les performances
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_etudiants_matricule
            ON etudiants(matricule)
        ''')

        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_etudiants_site
            ON etudiants(site_formation)
        ''')

        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_etudiants_annee
            ON etudiants(annee_academique)
        ''')

        # Initialiser les configurations par défaut
        self._init_default_config(cursor)

        # Créer un utilisateur admin par défaut s'il n'existe pas
        self._create_default_admin(cursor)

        conn.commit()
        conn.close()

    def _init_default_config(self, cursor):
        """Initialise les configurations par défaut"""
        default_configs = {
            'annee_academique_actuelle': '2025-2026',
            'app_version': '1.0.0',
            'delai_prevalidation': '7',
            'sites': 'Ndjamena,Sarh,Amdjarass'
        }

        for key, value in default_configs.items():
            cursor.execute('''
                INSERT OR IGNORE INTO configuration (key, value)
                VALUES (?, ?)
            ''', (key, value))

    def _create_default_admin(self, cursor):
        """Crée un utilisateur administrateur par défaut"""
        cursor.execute('SELECT id FROM users WHERE username = ?', ('admin',))
        if not cursor.fetchone():
            password_hash = bcrypt.hashpw('admin123'.encode('utf-8'), bcrypt.gensalt())
            cursor.execute('''
                INSERT INTO users (username, password_hash, nom_complet, role, site)
                VALUES (?, ?, ?, ?, ?)
            ''', ('admin', password_hash.decode('utf-8'), 'Administrateur', 'admin', 'Tous'))

    # ==================== GESTION DES UTILISATEURS ====================

    def create_user(self, username: str, password: str, nom_complet: str,
                   site: str, role: str = 'chef_service', email: str = None) -> int:
        """
        Crée un nouvel utilisateur

        Returns:
            ID du nouvel utilisateur
        """
        password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO users (username, password_hash, nom_complet, role, site, email)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (username, password_hash.decode('utf-8'), nom_complet, role, site, email))

        user_id = cursor.lastrowid
        conn.commit()
        conn.close()

        return user_id

    def authenticate_user(self, username: str, password: str) -> Optional[Dict]:
        """
        Authentifie un utilisateur

        Returns:
            Dictionnaire avec les infos de l'utilisateur si succès, None sinon
        """
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT id, username, password_hash, nom_complet, role, site, email
            FROM users WHERE username = ?
        ''', (username,))

        user = cursor.fetchone()

        if user and bcrypt.checkpw(password.encode('utf-8'),
                                   user['password_hash'].encode('utf-8')):
            # Mettre à jour la date de dernière connexion
            cursor.execute('''
                UPDATE users SET last_login = ? WHERE id = ?
            ''', (datetime.now().isoformat(), user['id']))
            conn.commit()

            user_dict = dict(user)
            del user_dict['password_hash']  # Ne pas retourner le hash
            conn.close()
            return user_dict

        conn.close()
        return None

    # ==================== GESTION DES ÉTUDIANTS ====================

    def generer_matricule(self, site: str, classe: str, annee_academique: str) -> str:
        """
        Génère automatiquement un matricule unique pour un étudiant

        Format: [CODE_SITE]-[ANNEE]-[CLASSE]-[NUMERO]
        Exemple: ND-2025-MTIC1-001

        Args:
            site: Site de formation (Ndjamena, Sarh, Amdjarass)
            classe: Code de la classe (ex: MTIC1, TELECOMS2)
            annee_academique: Année académique (ex: 2025-2026)

        Returns:
            Matricule unique généré
        """
        # Code du site
        codes_sites = {
            'Ndjamena': 'ND',
            'Sarh': 'SR',
            'Amdjarass': 'AM'
        }
        code_site = codes_sites.get(site, 'XX')

        # Année (prendre la première année)
        annee = annee_academique.split('-')[0]

        # Trouver le prochain numéro disponible pour ce site/classe/année
        conn = self.get_connection()
        cursor = conn.cursor()

        # Chercher le dernier matricule pour cette combinaison
        pattern = f"{code_site}-{annee}-{classe}-%"
        cursor.execute('''
            SELECT matricule FROM etudiants
            WHERE matricule LIKE ?
            ORDER BY matricule DESC
            LIMIT 1
        ''', (pattern,))

        dernier = cursor.fetchone()

        if dernier:
            # Extraire le numéro et incrémenter
            try:
                dernier_num = int(dernier['matricule'].split('-')[-1])
                nouveau_num = dernier_num + 1
            except:
                nouveau_num = 1
        else:
            nouveau_num = 1

        conn.close()

        # Formater le matricule
        matricule = f"{code_site}-{annee}-{classe}-{nouveau_num:03d}"

        return matricule

    def create_etudiant(self, etudiant_data: Dict, user_id: int) -> int:
        """
        Crée un nouvel étudiant avec attribution automatique du matricule si non fourni

        Returns:
            ID du nouvel étudiant
        """
        # Générer automatiquement le matricule si non fourni
        matricule = etudiant_data.get('matricule')
        if not matricule or matricule.strip() == '':
            # Attribution automatique
            matricule = self.generer_matricule(
                etudiant_data.get('site_formation'),
                etudiant_data.get('classe'),
                etudiant_data.get('annee_academique', self.get_config('annee_academique_actuelle') or '2025-2026')
            )
            etudiant_data['matricule'] = matricule

        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO etudiants (
                matricule, nom, prenoms, genre, date_naissance, lieu_naissance,
                classe, filiere, option, niveau, regime, site_formation,
                annee_academique, statut, numero_bordereau, email, telephone,
                adresse, created_by
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            matricule,
            etudiant_data.get('nom'),
            etudiant_data.get('prenoms'),
            etudiant_data.get('genre'),
            etudiant_data.get('date_naissance'),
            etudiant_data.get('lieu_naissance'),
            etudiant_data.get('classe'),
            etudiant_data.get('filiere'),
            etudiant_data.get('option'),
            etudiant_data.get('niveau'),
            etudiant_data.get('regime', 'Normal'),
            etudiant_data.get('site_formation'),
            etudiant_data.get('annee_academique'),
            etudiant_data.get('statut', 'En attente'),
            etudiant_data.get('numero_bordereau'),
            etudiant_data.get('email'),
            etudiant_data.get('telephone'),
            etudiant_data.get('adresse'),
            user_id
        ))

        etudiant_id = cursor.lastrowid

        # Enregistrer dans l'historique
        self._log_action(cursor, user_id, 'CREATE', 'etudiants', etudiant_id,
                        f"Création étudiant {etudiant_data.get('nom')} {etudiant_data.get('prenoms')}")

        conn.commit()
        conn.close()

        return etudiant_id

    def get_etudiants(self, filters: Dict = None, limit: int = None) -> List[Dict]:
        """
        Récupère la liste des étudiants avec filtres optionnels

        Args:
            filters: Dictionnaire de filtres (site, classe, annee, statut, etc.)
            limit: Nombre maximum de résultats

        Returns:
            Liste de dictionnaires représentant les étudiants
        """
        conn = self.get_connection()
        cursor = conn.cursor()

        query = 'SELECT * FROM etudiants WHERE 1=1'
        params = []

        if filters:
            if 'site_formation' in filters:
                query += ' AND site_formation = ?'
                params.append(filters['site_formation'])

            if 'classe' in filters:
                query += ' AND classe = ?'
                params.append(filters['classe'])

            if 'annee_academique' in filters:
                query += ' AND annee_academique = ?'
                params.append(filters['annee_academique'])

            if 'statut' in filters:
                query += ' AND statut = ?'
                params.append(filters['statut'])

            if 'search' in filters:
                query += ' AND (nom LIKE ? OR prenoms LIKE ? OR matricule LIKE ?)'
                search_term = f"%{filters['search']}%"
                params.extend([search_term, search_term, search_term])

        query += ' ORDER BY created_at DESC'

        if limit:
            query += f' LIMIT {limit}'

        cursor.execute(query, params)
        etudiants = [dict(row) for row in cursor.fetchall()]

        conn.close()
        return etudiants

    def get_etudiant_by_id(self, etudiant_id: int) -> Optional[Dict]:
        """Récupère un étudiant par son ID"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute('SELECT * FROM etudiants WHERE id = ?', (etudiant_id,))
        etudiant = cursor.fetchone()

        conn.close()
        return dict(etudiant) if etudiant else None

    def get_etudiant_by_matricule(self, matricule: str) -> Optional[Dict]:
        """Récupère un étudiant par son matricule"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute('SELECT * FROM etudiants WHERE matricule = ?', (matricule,))
        etudiant = cursor.fetchone()

        conn.close()
        return dict(etudiant) if etudiant else None

    def update_etudiant(self, etudiant_id: int, etudiant_data: Dict, user_id: int) -> bool:
        """Met à jour un étudiant"""
        conn = self.get_connection()
        cursor = conn.cursor()

        # Construire la requête UPDATE dynamiquement
        fields = []
        values = []

        for key, value in etudiant_data.items():
            if key != 'id':
                fields.append(f"{key} = ?")
                values.append(value)

        if not fields:
            conn.close()
            return False

        fields.append("updated_at = ?")
        values.append(datetime.now().isoformat())
        values.append(etudiant_id)

        query = f"UPDATE etudiants SET {', '.join(fields)} WHERE id = ?"
        cursor.execute(query, values)

        # Enregistrer dans l'historique
        self._log_action(cursor, user_id, 'UPDATE', 'etudiants', etudiant_id,
                        f"Modification étudiant ID {etudiant_id}")

        conn.commit()
        success = cursor.rowcount > 0
        conn.close()

        return success

    def delete_etudiant(self, etudiant_id: int, user_id: int) -> bool:
        """Supprime un étudiant"""
        conn = self.get_connection()
        cursor = conn.cursor()

        # Récupérer les infos avant suppression
        cursor.execute('SELECT nom, prenoms FROM etudiants WHERE id = ?', (etudiant_id,))
        etudiant = cursor.fetchone()

        if not etudiant:
            conn.close()
            return False

        cursor.execute('DELETE FROM etudiants WHERE id = ?', (etudiant_id,))

        # Enregistrer dans l'historique
        self._log_action(cursor, user_id, 'DELETE', 'etudiants', etudiant_id,
                        f"Suppression étudiant {etudiant['nom']} {etudiant['prenoms']}")

        conn.commit()
        success = cursor.rowcount > 0
        conn.close()

        return success

    # ==================== STATISTIQUES ====================

    def get_statistics(self, site: str = None, annee: str = None) -> Dict:
        """Récupère les statistiques globales"""
        conn = self.get_connection()
        cursor = conn.cursor()

        filters = []
        params = []

        if site:
            filters.append('site_formation = ?')
            params.append(site)

        if annee:
            filters.append('annee_academique = ?')
            params.append(annee)

        where_clause = ' AND '.join(filters) if filters else '1=1'

        # Total étudiants
        cursor.execute(f'SELECT COUNT(*) as total FROM etudiants WHERE {where_clause}', params)
        total = cursor.fetchone()['total']

        # Par statut
        cursor.execute(f'''
            SELECT statut, COUNT(*) as count
            FROM etudiants
            WHERE {where_clause}
            GROUP BY statut
        ''', params)
        par_statut = {row['statut']: row['count'] for row in cursor.fetchall()}

        # Par genre
        cursor.execute(f'''
            SELECT genre, COUNT(*) as count
            FROM etudiants
            WHERE {where_clause}
            GROUP BY genre
        ''', params)
        par_genre = {row['genre']: row['count'] for row in cursor.fetchall()}

        # Par niveau
        cursor.execute(f'''
            SELECT niveau, COUNT(*) as count
            FROM etudiants
            WHERE {where_clause}
            GROUP BY niveau
        ''', params)
        par_niveau = {row['niveau']: row['count'] for row in cursor.fetchall()}

        conn.close()

        return {
            'total': total,
            'par_statut': par_statut,
            'par_genre': par_genre,
            'par_niveau': par_niveau
        }

    # ==================== UTILITAIRES ====================

    def _log_action(self, cursor, user_id: int, action: str, table_name: str,
                   record_id: int, details: str):
        """Enregistre une action dans l'historique"""
        cursor.execute('''
            INSERT INTO historique (user_id, action, table_name, record_id, details)
            VALUES (?, ?, ?, ?, ?)
        ''', (user_id, action, table_name, record_id, details))

    def get_config(self, key: str) -> Optional[str]:
        """Récupère une valeur de configuration"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute('SELECT value FROM configuration WHERE key = ?', (key,))
        result = cursor.fetchone()

        conn.close()
        return result['value'] if result else None

    def set_config(self, key: str, value: str):
        """Définit une valeur de configuration"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            INSERT OR REPLACE INTO configuration (key, value, updated_at)
            VALUES (?, ?, ?)
        ''', (key, value, datetime.now().isoformat()))

        conn.commit()
        conn.close()

    def backup_database(self, backup_path: str) -> bool:
        """Crée une sauvegarde de la base de données"""
        try:
            import shutil
            shutil.copy2(self.db_path, backup_path)
            return True
        except Exception as e:
            print(f"Erreur lors de la sauvegarde: {e}")
            return False
