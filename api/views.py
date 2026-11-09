from decimal import Decimal
from bson import ObjectId
from bson.errors import InvalidId

from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import (
    Categoria,
    Videojuego,
    Pedido,
    DetallePedido
)
from .serializers import (
    CategoriaSerializer,
    VideojuegoSerializer,
    PedidoSerializer,
    DetallePedidoSerializer
)



# Funciones auxilares

def obtener_objeto(modelo, pk):
   

    try:
        object_id = ObjectId(str(pk))
    except (InvalidId, TypeError, ValueError):
        return None

    try:
        return modelo.objects.get(pk=object_id)
    except modelo.DoesNotExist:
        return None


def calcular_subtotal(precio, cantidad):
    return (precio * cantidad).quantize(
        Decimal("0.01")
    )


def recalcular_total(pedido):

    total = Decimal("0.00")

    for detalle in pedido.detalles.all():
        total += detalle.subtotal

    pedido.total = total
    pedido.save(update_fields=["total"])



#Categorias

@api_view(["GET", "POST"])
def categoria_lista(request):

    if request.method == "GET":

        categorias = Categoria.objects.all()

        serializer = CategoriaSerializer(
            categorias,
            many=True
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )

    serializer = CategoriaSerializer(data=request.data)

    if serializer.is_valid():
        categoria = serializer.save()

        return Response(
            CategoriaSerializer(categoria).data,
            status=status.HTTP_201_CREATED
        )

    return Response(
        serializer.errors,
        status=status.HTTP_400_BAD_REQUEST
    )

@api_view(["GET", "PUT", "PATCH", "DELETE"])
def categoria_detalle(request, pk):

    categoria = obtener_objeto(Categoria, pk)

    if categoria is None:
        return Response(
            {"error": "Categoría no encontrada."},
            status=status.HTTP_404_NOT_FOUND
        )

    if request.method == "GET":

        serializer = CategoriaSerializer(categoria)

        return Response(serializer.data)

    if request.method in ["PUT", "PATCH"]:

        serializer = CategoriaSerializer(
            categoria,
            data=request.data,
            partial=(request.method == "PATCH")
        )

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

    if request.method == "DELETE":

        if categoria.videojuegos.exists():
            return Response(
                {
                    "error": (
                        "No puedes eliminar una categoría "
                        "que contiene videojuegos."
                    )
                },
                status=status.HTTP_409_CONFLICT
            )

        categoria.delete()

        return Response(
            {"mensaje": "Categoría eliminada correctamente."},
            status=status.HTTP_200_OK
        )

#Videojuegos

@api_view(["GET", "POST"])
def videojuego_lista(request):

    if request.method == "GET":

        videojuegos = Videojuego.objects.all()

        serializer = VideojuegoSerializer(
            videojuegos,
            many=True
        )

        return Response(serializer.data)

    serializer = VideojuegoSerializer(data=request.data)

    if serializer.is_valid():

        videojuego = serializer.save()

        return Response(
            VideojuegoSerializer(videojuego).data,
            status=status.HTTP_201_CREATED
        )

    return Response(
        serializer.errors,
        status=status.HTTP_400_BAD_REQUEST
    )


@api_view(["GET", "PUT", "PATCH", "DELETE"])
def videojuego_detalle(request, pk):

    videojuego = obtener_objeto(Videojuego, pk)

    if videojuego is None:
        return Response(
            {"error": "Videojuego no encontrado."},
            status=status.HTTP_404_NOT_FOUND
        )

    if request.method == "GET":

        serializer = VideojuegoSerializer(videojuego)

        return Response(serializer.data)

    if request.method in ["PUT", "PATCH"]:

        serializer = VideojuegoSerializer(
            videojuego,
            data=request.data,
            partial=(request.method == "PATCH")
        )

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

    if request.method == "DELETE":

        if videojuego.ventas.exists():
            return Response(
                {
                    "error": (
                        "No puedes eliminar un videojuego "
                        "que tiene ventas registradas."
                    )
                },
                status=status.HTTP_409_CONFLICT
            )

        videojuego.delete()

        return Response(
            {"mensaje": "Videojuego eliminado correctamente."},
            status=status.HTTP_200_OK
        )

