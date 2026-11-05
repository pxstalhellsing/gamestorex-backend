
from bson import ObjectId
from bson.errors import InvalidId

from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import Categoria, Videojuego
from .serializers import CategoriaSerializer



# Buscar una categoria por su ObjectId

def obtener_categoria(pk):

    try:
        object_id = ObjectId(pk)

    except (InvalidId, TypeError):
        return None

    try:
        return Categoria.objects.get(pk=object_id)

    except Categoria.DoesNotExist:
        return None

