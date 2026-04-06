#!/usr/bin/env python3
"""
Script pour corriger l'environnement macOS et créer un .app
"""

import subprocess
import sys
import os
import shutil
from pathlib import Path

print("=" * 70)
print("CORRECTION ENVIRONNEMENT + BUILD .APP ENASTIC")
print("=" * 70)
print()

# Étape 1: Vérifier Python
print("1. Vérification de Python...")
print(f"   Python: {sys.version}")
print(f"   Exécutable: {sys.executable}")
print()

# Étape 2: Installer/Mettre à jour PyInstaller
print("2. Installation/Mise à jour de PyInstaller...")
try:
    subprocess.run([sys.executable, "-m", "pip", "install", "--upgrade", "pyinstaller"], check=True)
    print("   ✓ PyInstaller installé/mis à jour")
except Exception as e:
    print(f"   ✗ Erreur: {e}")
print()

# Étape 3: Nettoyer les anciens builds
print("3. Nettoyage des anciens builds...")
for path in ['build', 'dist', 'ENASTIC_Inscriptions.spec']:
    if os.path.exists(path):
        if os.path.isdir(path):
            shutil.rmtree(path)
            print(f"   ✓ Supprimé: {path}/")
        else:
            os.remove(path)
            print(f"   ✓ Supprimé: {path}")
print()

# Étape 4: Créer un fichier .spec personnalisé
print("4. Création du fichier .spec personnalisé...")

spec_content = """# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['desktop_app/main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('desktop_app/assets', 'desktop_app/assets'),
    ],
    hiddenimports=[
        'PyQt6.QtCore',
        'PyQt6.QtWidgets',
        'PyQt6.QtGui',
        'PyQt6.sip',
        'sqlite3',
        'bcrypt',
        'reportlab',
        'reportlab.pdfgen',
        'reportlab.lib',
        'qrcode',
        'PIL',
        'PIL.Image',
        'docx',
        'openpyxl',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='ENASTIC_Inscriptions',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='desktop_app/assets/logo.ico' if os.path.exists('desktop_app/assets/logo.ico') else None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='ENASTIC_Inscriptions',
)

# Pour macOS: créer un .app bundle
import sys
if sys.platform == 'darwin':
    app = BUNDLE(
        coll,
        name='ENASTIC_Inscriptions.app',
        icon='desktop_app/assets/logo.ico' if os.path.exists('desktop_app/assets/logo.ico') else None,
        bundle_identifier='td.enastic.inscriptions',
        info_plist={
            'NSPrincipalClass': 'NSApplication',
            'NSHighResolutionCapable': 'True',
            'CFBundleName': 'ENASTIC Inscriptions',
            'CFBundleDisplayName': 'ENASTIC Inscriptions',
            'CFBundleVersion': '1.0.0',
            'CFBundleShortVersionString': '1.0.0',
        },
    )
"""

with open('ENASTIC_Inscriptions.spec', 'w') as f:
    f.write(spec_content)

print("   ✓ Fichier .spec créé")
print()

# Étape 5: Lancer PyInstaller avec le .spec
print("5. Compilation avec PyInstaller...")
print("   (Cela peut prendre plusieurs minutes...)")
print()

try:
    # Utiliser directement subprocess pour éviter les problèmes
    result = subprocess.run(
        [sys.executable, "-m", "PyInstaller", "ENASTIC_Inscriptions.spec", "--noconfirm"],
        capture_output=True,
        text=True,
        timeout=600  # 10 minutes max
    )

    print("STDOUT:")
    print(result.stdout)
    print()
    print("STDERR:")
    print(result.stderr)
    print()

    if result.returncode == 0:
        print("=" * 70)
        print("✅ BUILD RÉUSSI!")
        print("=" * 70)
        print()

        # Vérifier ce qui a été créé
        if os.path.exists('dist'):
            print("📦 Fichiers créés dans dist/:")
            for item in os.listdir('dist'):
                path = os.path.join('dist', item)
                if os.path.isdir(path):
                    # Calculer la taille du dossier
                    total_size = 0
                    for dirpath, dirnames, filenames in os.walk(path):
                        for f in filenames:
                            fp = os.path.join(dirpath, f)
                            try:
                                total_size += os.path.getsize(fp)
                            except:
                                pass
                    print(f"   📁 {item}/ ({total_size / (1024*1024):.1f} MB)")
                else:
                    size = os.path.getsize(path)
                    print(f"   📄 {item} ({size / (1024*1024):.1f} MB)")
            print()

            # Instructions
            if sys.platform == 'darwin':
                if os.path.exists('dist/ENASTIC_Inscriptions.app'):
                    print("🎉 Application macOS créée!")
                    print()
                    print("Pour lancer:")
                    print("   open dist/ENASTIC_Inscriptions.app")
                    print()
                    print("Pour copier dans Applications:")
                    print("   cp -r dist/ENASTIC_Inscriptions.app /Applications/")
                    print()
                elif os.path.exists('dist/ENASTIC_Inscriptions'):
                    print("📦 Application créée (format dossier)")
                    print()
                    print("Pour lancer:")
                    print("   ./dist/ENASTIC_Inscriptions/ENASTIC_Inscriptions")
                    print()
    else:
        print("=" * 70)
        print("❌ BUILD ÉCHOUÉ")
        print("=" * 70)
        print(f"Code de sortie: {result.returncode}")
        print()

except subprocess.TimeoutExpired:
    print("❌ Timeout - Le build a pris trop de temps")
except Exception as e:
    print(f"❌ Erreur lors du build: {e}")
    import traceback
    traceback.print_exc()

print()
print("=" * 70)
print("FIN DU SCRIPT")
print("=" * 70)
