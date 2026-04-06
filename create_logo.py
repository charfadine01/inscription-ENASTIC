"""
Script pour créer le logo ENASTIC
"""

from PIL import Image, ImageDraw, ImageFont
import os

def create_enastic_logo():
    """Crée le logo ENASTIC"""

    # Taille du logo
    size = 256

    # Créer une image avec fond transparent
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Couleurs ENASTIC (bleu professionnel)
    blue_primary = (74, 144, 226)      # #4A90E2
    blue_dark = (37, 99, 235)          # #2563EB
    white = (255, 255, 255)

    # Dessiner un cercle bleu en fond
    circle_margin = 10
    draw.ellipse([circle_margin, circle_margin, size-circle_margin, size-circle_margin],
                 fill=blue_primary, outline=blue_dark, width=4)

    # Essayer d'utiliser une police système, sinon utiliser la police par défaut
    try:
        # Tenter différentes polices selon le système
        font_paths = [
            '/System/Library/Fonts/Helvetica.ttc',  # macOS
            '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',  # Linux
            'C:\\Windows\\Fonts\\Arial.ttf',  # Windows
        ]

        font_large = None
        font_small = None

        for font_path in font_paths:
            if os.path.exists(font_path):
                font_large = ImageFont.truetype(font_path, 70)
                font_small = ImageFont.truetype(font_path, 32)
                break

        if font_large is None:
            # Utiliser la police par défaut
            font_large = ImageFont.load_default()
            font_small = ImageFont.load_default()

    except Exception as e:
        print(f"Impossible de charger une police: {e}")
        font_large = ImageFont.load_default()
        font_small = ImageFont.load_default()

    # Texte "E" grand au centre
    text_e = "E"

    # Calculer la position pour centrer le "E"
    # On utilise textbbox pour obtenir les dimensions du texte
    bbox = draw.textbbox((0, 0), text_e, font=font_large)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]

    x = (size - text_width) // 2
    y = (size - text_height) // 2 - 20

    # Dessiner "E" en blanc
    draw.text((x, y), text_e, fill=white, font=font_large)

    # Texte "NASTIC" en plus petit en bas
    text_nastic = "NASTIC"
    bbox_small = draw.textbbox((0, 0), text_nastic, font=font_small)
    text_width_small = bbox_small[2] - bbox_small[0]

    x_small = (size - text_width_small) // 2
    y_small = size - 60

    draw.text((x_small, y_small), text_nastic, fill=white, font=font_small)

    # Sauvegarder le logo
    logo_dir = os.path.dirname(os.path.abspath(__file__))
    logo_path = os.path.join(logo_dir, 'assets', 'logo.png')

    # Créer le dossier assets s'il n'existe pas
    os.makedirs(os.path.dirname(logo_path), exist_ok=True)

    img.save(logo_path)
    print(f"✅ Logo créé: {logo_path}")

    # Créer aussi une icône .ico pour Windows
    icon_path = os.path.join(logo_dir, 'assets', 'logo.ico')
    img.save(icon_path, format='ICO', sizes=[(256, 256), (128, 128), (64, 64), (48, 48), (32, 32), (16, 16)])
    print(f"✅ Icône créée: {icon_path}")

    return logo_path, icon_path


if __name__ == '__main__':
    print("Création du logo ENASTIC...")
    print()
    logo_path, icon_path = create_enastic_logo()
    print()
    print(f"Logo PNG: {logo_path}")
    print(f"Icône ICO: {icon_path}")
    print()
    print("✅ Terminé!")
