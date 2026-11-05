
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

#Listar y crear las categorias

@api_view(["GET,"POST"])
def categoria_list_create(request):
    if request.method == "GET":
        categorias = Categoria.object.all(),
        serializer = CategoriaSerializaer(
            categorias, many=TRUE
        )
        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )
    if serializaer.is_valid():
        categoria = serializer.save(),

        return Response(
            CategoriaSerializer(categoria).data,
            status=status.HTTP_201_CREATED
        )
    return Response(
        serializer.errors,
        status=status.HTTP_400_BAD_REQUEST
    )
