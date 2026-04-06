"""
Script de build simplifié pour l'application desktop ENASTIC
"""

import PyInstaller.__main__
import sys
import os

print("=" * 70)
print("BUILD SIMPLIFIÉ - APPLICATION DESKTOP ENASTIC")
print("=" * 70)
print()

# Options PyInstaller simplifiées
pyinstaller_args = [
    'desktop_app/main.py',
    '--name=ENASTIC_Inscriptions',
    '--onedir',  # Dossier au lieu d'un seul fichier (plus fiable sur macOS)
    '--clean',
    '--noconfirm',

    # Inclure le logo et les assets
    '--add-data=desktop_app/assets:desktop_app/assets',
    '--icon=desktop_app/assets/logo.ico',

    # Modules cachés
    '--hidden-import=PyQt6',
    '--hidden-import=PyQt6.QtCore',
    '--hidden-import=PyQt6.QtWidgets',
    '--hidden-import=PyQt6.QtGui',
    '--hidden-import=bcrypt',
    '--hidden-import=sqlite3',
]

print("🔨 Démarrage du build...")
print()

try:
    PyInstaller.__main__.run(pyinstaller_args)
    print()
    print("=" * 70)
    print("✅ BUILD TERMINÉ AVEC SUCCÈS!")
    print("=" * 70)
    print()
    print("📦 L'application se trouve dans: dist/ENASTIC_Inscriptions/")
    print()
    print("Pour lancer:")
    print("  ./dist/ENASTIC_Inscriptions/ENASTIC_Inscriptions")
    print()
except Exception as e:
    print()
    print("=" * 70)
    print("❌ ERREUR LORS DU BUILD")
    print("=" * 70)
    print(f"Erreur: {e}")
    print()
    sys.exit(1)
