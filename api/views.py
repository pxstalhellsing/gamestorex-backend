from decimal import Decimal
from bson import ObjectId
from bson.errors import InvalidId
from django_mongodb_backend import transaction

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

# PEDIDOS

@api_view(["GET", "POST"])
def pedido_lista(request):

    if request.method == "GET":

        pedidos = Pedido.objects.all().order_by(
            "-fecha_pedido"
        )

        serializer = PedidoSerializer(
            pedidos,
            many=True
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )

    serializer = PedidoCreateSerializer(
        data=request.data
    )

    if serializer.is_valid():

        pedido = serializer.save()

        return Response(
            PedidoSerializer(pedido).data,
            status=status.HTTP_201_CREATED
        )

    return Response(
        serializer.errors,
        status=status.HTTP_400_BAD_REQUEST
    )

    @api_view(["GET", "PATCH", "DELETE"])
def pedido_detalle(request, pk):

    pedido = obtener_objeto(Pedido, pk)

    if pedido is None:

        return Response(
            {"error": "Pedido no encontrado."},
            status=status.HTTP_404_NOT_FOUND
        )

    if request.method == "GET":

        serializer = PedidoSerializer(pedido)

        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )

    if request.method == "PATCH":

        serializer = PedidoActualizarSerializer(
            data=request.data,
            partial=True
        )

        if not serializer.is_valid():

            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )

        datos = serializer.validated_data

        nuevo_estado = datos.get(
            "estado",
            pedido.estado
        )

        if pedido.estado == "CANCELADO" and nuevo_estado != "CANCELADO":

            return Response(
                {
                    "error": (
                        "Un pedido cancelado no puede "
                        "volver a activarse."
                    )
                },
                status=status.HTTP_409_CONFLICT
            )

        if nuevo_estado == "PAGADO" and pedido.estado != "PENDIENTE":

            return Response(
                {
                    "error": (
                        "Solo se pueden pagar pedidos pendientes."
                    )
                },
                status=status.HTTP_409_CONFLICT
            )

        if (
            pedido.estado != "PENDIENTE"
            and (
                "cliente_nombre" in datos
                or "cliente_correo" in datos
            )
        ):

            return Response(
                {
                    "error": (
                        "Los datos del cliente solo se pueden "
                        "modificar en pedidos pendientes."
                    )
                },
                status=status.HTTP_409_CONFLICT
            )

        with transaction.atomic():

            if (
                nuevo_estado == "CANCELADO"
                and pedido.estado != "CANCELADO"
            ):

                reponer_stock(pedido)

            pedido.cliente_nombre = datos.get(
                "cliente_nombre",
                pedido.cliente_nombre
            )

            pedido.cliente_correo = datos.get(
                "cliente_correo",
                pedido.cliente_correo
            )

            pedido.estado = nuevo_estado

            pedido.save()

        return Response(
            PedidoSerializer(pedido).data,
            status=status.HTTP_200_OK
        )

    if request.method == "DELETE":

        with transaction.atomic():

            # Si el pedido no estaba cancelado,
            # devolver los videojuegos al inventario.

            if pedido.estado != "CANCELADO":

                reponer_stock(pedido)

            pedido.delete()

        return Response(
            status=status.HTTP_204_NO_CONTENT
        )

#Detalles de Pedido

 @api_view(["GET", "POST"])
def detalle_pedido_lista(request):

    if request.method == "GET":

        detalles = DetallePedido.objects.all()

        pedido_id = request.query_params.get("pedido")

        if pedido_id:

            try:
                pedido_object_id = ObjectId(pedido_id)

            except (InvalidId, TypeError, ValueError):

                return Response(
                    {"error": "El ID del pedido no es válido."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            detalles = detalles.filter(
                pedido_id=pedido_object_id
            )

        serializer = DetallePedidoSerializer(
            detalles,
            many=True
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )

    serializer = DetallePedidoCreateSerializer(
        data=request.data
    )

    if not serializer.is_valid():

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

    pedido = serializer.validated_data["pedido"]

    videojuego = serializer.validated_data["videojuego"]

    cantidad = serializer.validated_data["cantidad"]

    if pedido.estado != "PENDIENTE":

        return Response(
            {
                "error": (
                    "Solo puedes modificar pedidos pendientes."
                )
            },
            status=status.HTTP_409_CONFLICT
        )

    with transaction.atomic():

        videojuego = Videojuego.objects.get(
            pk=videojuego.pk
        )

        if videojuego.stock < cantidad:

            return Response(
                {
                    "error": (
                        f"Stock insuficiente. "
                        f"Disponible: {videojuego.stock}."
                    )
                },
                status=status.HTTP_409_CONFLICT
            )

        precio = Decimal(str(videojuego.precio))

        subtotal = calcular_subtotal(
            precio,
            cantidad
        )

        videojuego.stock -= cantidad

        videojuego.save(
            update_fields=["stock"]
        )

        detalle = DetallePedido.objects.create(
            pedido=pedido,
            videojuego=videojuego,
            cantidad=cantidad,
            precio_unitario=precio,
            subtotal=subtotal
        )

        recalcular_total(pedido)

    return Response(
        DetallePedidoSerializer(detalle).data,
        status=status.HTTP_201_CREATED
    )

@api_view(["GET", "PUT", "PATCH", "DELETE"])
def detalle_pedido_item(request, pk):

    detalle = obtener_objeto(DetallePedido, pk)

    if detalle is None:

        return Response(
            {"error": "Detalle de pedido no encontrado."},
            status=status.HTTP_404_NOT_FOUND
        )

    pedido = detalle.pedido

    if request.method == "GET":

        serializer = DetallePedidoSerializer(detalle)

        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )

    if request.method in ["PUT", "PATCH"]:

        if pedido.estado != "PENDIENTE":

            return Response(
                {
                    "error": (
                        "No puedes modificar detalles "
                        "de un pedido que no está pendiente."
                    )
                },
                status=status.HTTP_409_CONFLICT
            )

        serializer = DetallePedidoActualizarSerializer(
            data=request.data,
            partial=(request.method == "PATCH"
                     )
        )

        if not serializer.is_valid():

            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )

        nueva_cantidad = serializer.validated_data.get(
            "cantidad",
            detalle.cantidad
        )

        with transaction.atomic():

            videojuego = Videojuego.objects.get(
                pk=detalle.videojuego_id
            )

            diferencia = nueva_cantidad - detalle.cantidad

            # Si se solicitan más unidades,
            # comprobar y descontar el stock adicional.

            if diferencia > 0:

                if videojuego.stock < diferencia:

                    return Response(
                        {
                            "error": (
                                f"Stock insuficiente. "
                                f"Disponible: {videojuego.stock}."
                            )
                        },
                        status=status.HTTP_409_CONFLICT
                    )

                videojuego.stock -= diferencia

            # Si se solicitan menos unidades,
            # devolver la diferencia al inventario.

            elif diferencia < 0:

                videojuego.stock += abs(diferencia)

            videojuego.save(
                update_fields=["stock"]
            )

            detalle.cantidad = nueva_cantidad

            detalle.subtotal = calcular_subtotal(
                detalle.precio_unitario,
                nueva_cantidad
            )

            detalle.save(
                update_fields=["cantidad", "subtotal"]
            )

            recalcular_total(pedido)

        return Response(
            DetallePedidoSerializer(detalle).data,
            status=status.HTTP_200_OK
        )

    if request.method == "DELETE":

        if pedido.estado != "PENDIENTE":

            return Response(
                {
                    "error": (
                        "No puedes eliminar detalles "
                        "de un pedido que no está pendiente."
                    )
                },
                status=status.HTTP_409_CONFLICT
            )

        with transaction.atomic():

            videojuego = Videojuego.objects.get(
                pk=detalle.videojuego_id
            )

            videojuego.stock += detalle.cantidad

            videojuego.save(
                update_fields=["stock"]
            )

            detalle.delete()

            recalcular_total(pedido)

        return Response(
            status=status.HTTP_204_NO_CONTENT
        )