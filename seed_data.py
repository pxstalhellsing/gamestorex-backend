import json
import os
from decimal import Decimal
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from api.models import Categoria, Videojuego

def cargar_datos():
    ruta_json = os.path.join(os.path.dirname(__file__), 'games.json')

    # Si copiaste el games.json de tu proyecto React antiguo, lo importa automáticamente
    if os.path.exists(ruta_json):
        with open(ruta_json, 'r', encoding='utf-8') as f:
            juegos_react = json.load(f)

        for item in juegos_react:
            nombre_cat = item.get('genre', 'General').strip()
            categoria_obj, _ = Categoria.objects.get_or_create(
                nombre=nombre_cat,
                defaults={'descripcion': f'Videojuegos del género {nombre_cat}'}
            )
            Videojuego.objects.update_or_create(
                titulo=item.get('title'),
                defaults={
                    'descripcion': item.get('description', 'Sin descripción'),
                    'precio': Decimal(str(item.get('price', 10000))),
                    'stock': int(item.get('stock', 5)),
                    'plataforma': item.get('platform', 'PC'),
                    'categoria': categoria_obj
                }
            )
        print(f"✅ Se importaron {Videojuego.objects.count()} videojuegos desde games.json a MongoDB.")
        return

    # Si no está games.json, carga este catálogo base de GameStoreX
    cat_rpg, _ = Categoria.objects.get_or_create(nombre="RPG", defaults={"descripcion": "Juegos de rol y fantasía"})
    cat_accion, _ = Categoria.objects.get_or_create(nombre="Acción", defaults={"descripcion": "Combate y aventura dinámica"})
    cat_aventura, _ = Categoria.objects.get_or_create(nombre="Aventura", defaults={"descripcion": "Exploración e historia"})

    juegos_base = [
        {
            "titulo": "Elden Ring",
            "descripcion": "Un vasto mundo lleno de misterio creado por FromSoftware.",
            "precio": Decimal("49990.00"),
            "stock": 8,
            "plataforma": "PS5",
            "categoria": cat_rpg
        },
        {
            "titulo": "God of War Ragnarök",
            "descripcion": "Kratos y Atreus viajan por los nueve reinos nórdicos.",
            "precio": Decimal("54990.00"),
            "stock": 5,
            "plataforma": "PS5",
            "categoria": cat_accion
        },
        {
            "titulo": "The Legend of Zelda: Tears of the Kingdom",
            "descripcion": "Una aventura épica a través de la tierra y los cielos de Hyrule.",
            "precio": Decimal("59990.00"),
            "stock": 10,
            "plataforma": "Nintendo Switch",
            "categoria": cat_aventura
        }
    ]

    for j in juegos_base:
        Videojuego.objects.update_or_create(titulo=j["titulo"], defaults=j)

    print(f"✅ Catálogo base cargado en MongoDB ({Videojuego.objects.count()} videojuegos).")

if __name__ == '__main__':
    cargar_datos()