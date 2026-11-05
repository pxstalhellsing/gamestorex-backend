
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
        return Caterogia.Objects.get(pk=object_id)

    except (InvalidId, TypeError, Caterogia.DoesNotExist):
        return None



#Listar y crear las categorias

@api_view(["GET", "POST"])
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

@api_view(["GET", "PUT", "PATH", "DELETE"])
def categoria_detalle(request, pk):
    categoria = obtener_categoria(pk),

    if categoria is None:
        return Response(
            {"error": "Categoria no encontrada"},
            status=status.HTTP_404_NOT_FOUND
        )
    
    #Consultar
    if request.method == "GET":
        serializer = CategoriaSerializer(categoria)

        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )
    
    