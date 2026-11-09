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
    PedidoCreateSerializer,
    PedidoActualizarSerializer,
    DetallePedidoSerializer,
    DetallePedidoCreateSerializer,
    DetallePedidoActualizarSerializer
)


# Funciones auxilares

def obtener_objeto(modelo, pk):
    """
    Busca un documento utilizando su ObjectId.
    Si el identificador no existe o es inválido,
    devuelve None.
    """

    try:
        object_id = ObjectId(str(pk))

        return modelo.objects.get(pk=object_id)

    except (InvalidId, TypeError, ValueError):
        return None

    except modelo.DoesNotExist:
        return None


def calcular_subtotal(precio, cantidad):
    """
    Calcula el subtotal de un videojuego
    dentro de un pedido.
    """

    return (precio * cantidad).quantize(
        Decimal("0.01")
    )


def recalcular_total(pedido):
    """
    Recorre los detalles de un pedido
    y vuelve a calcular su total.
    """

    total = Decimal("0.00")

    for detalle in pedido.detalles.all():
        total += detalle.subtotal

    pedido.total = total

    pedido.save(
        update_fields=["total"]
    )


def reponer_stock(pedido):
    """
    Devuelve al inventario los videojuegos
    que pertenecen a un pedido.
    """

    for detalle in pedido.detalles.all():

        videojuego = Videojuego.objects.get(
            pk=detalle.videojuego_id
        )

        videojuego.stock += detalle.cantidad

        videojuego.save(
            update_fields=["stock"]
        )


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

        # Buscar por título.

        buscar = request.query_params.get("buscar")

        if buscar:
            videojuegos = videojuegos.filter(
                titulo__icontains=buscar
            )

        # Filtrar por plataforma.

        plataforma = request.query_params.get("plataforma")

        if plataforma:
            videojuegos = videojuegos.filter(
                plataforma__iexact=plataforma
            )

        # Filtrar por categoría mediante ObjectId.

        categoria_id = request.query_params.get("categoria")

        if categoria_id:

            try:
                categoria_object_id = ObjectId(categoria_id)

            except (InvalidId, TypeError, ValueError):

                return Response(
                    {"error": "El ID de categoría no es válido."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            videojuegos = videojuegos.filter(
                categoria_id=categoria_object_id
            )

        serializer = VideojuegoSerializer(
            videojuegos,
            many=True
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )

    serializer = VideojuegoSerializer(
        data=request.data
    )

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

        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )

    if request.method in ["PUT", "PATCH"]:

        serializer = VideojuegoSerializer(
            videojuego,
            data=request.data,
            partial=(request.method == "PATCH")
        )

        if serializer.is_valid():

            serializer.save()

            return Response(
                serializer.data,
                status=status.HTTP_200_OK
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

    if request.method == "DELETE":

        # No eliminar videojuegos que tienen ventas registradas.

        if videojuego.ventas.exists():

            return Response(
                {
                    "error": (
                        "No puedes eliminar este videojuego "
                        "porque está registrado en pedidos."
                    )
                },
                status=status.HTTP_409_CONFLICT
            )

        videojuego.delete()

        return Response(
            status=status.HTTP_204_NO_CONTENT
        )