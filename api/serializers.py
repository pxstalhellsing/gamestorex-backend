from rest_framework import serializers
from decimal import Decimal
from .models import Categoria, Videojuego, Pedido, DetallePedido
from bson import ObjectId
from bson.errors import InvalidId


# CAMPO PERSONALIZADO PARA REFERENCIAS OBJECTID


class ObjectIdRelatedField(serializers.RelatedField):

    def to_internal_value(self, data):

        try:
            object_id = ObjectId(str(data))
        except (InvalidId, TypeError, ValueError):
            raise serializers.ValidationError(
                "El identificador proporcionado no es válido."
            )

        try:
            return self.get_queryset().get(pk=object_id)

        except self.get_queryset().model.DoesNotExist:
            raise serializers.ValidationError(
                "No se encontró el registro solicitado."
            )

    def to_representation(self, value):
        return str(value.pk)

# SERIALIZER DE CATEGORÍAS

class CategoriaSerializer(serializers.ModelSerializer):
    id = serializers.CharField(read_only=True)

    class Meta:
        model = Categoria
        fields = ['id', 'nombre', 'descripcion']

# SERIALIZER DE CATEGORÍAS

class VideojuegoSerializer(serializers.ModelSerializer):
    id = serializers.CharField(read_only=True)
    categoria = ObjectIdRelatedField(queryset=Categoria.objects.all())
    categoria_nombre = serializers.ReadOnlyField(source='categoria.nombre')

    class Meta:
        model = Videojuego
        fields = ['id', 'titulo', 'descripcion', 'precio', 'stock', 'plataforma', 'categoria', 'categoria_nombre']

    def validate_precio(self, value):
        if value <= Decimal('0.00'):
            raise serializers.ValidationError("El precio debe ser mayor que cero.")
        return value

    def validate_stock(self, value):
        if value < 0:
            raise serializers.ValidationError("El stock no puede ser negativo.")
        return value

# SERIALIZER DE DETALLES DE PEDIDO 

class DetallePedidoSerializer(serializers.ModelSerializer):
    id = serializers.CharField(read_only=True)
    videojuego_titulo = serializers.ReadOnlyField(source='videojuego.titulo')

    class Meta:
        model = DetallePedido
        fields = ['id', 'pedido', 'videojuego', 'videojuego_titulo', 'cantidad', 'precio_unitario', 'subtotal']
        read_only_fields = ['precio_unitario', 'subtotal']

    def validate(self, data):
        videojuego = data['videojuego']
        cantidad = data['cantidad']
        if cantidad <= 0:
            raise serializers.ValidationError({"cantidad": "La cantidad debe ser mayor a 0."})
        if videojuego.stock < cantidad:
            raise serializers.ValidationError({"stock": f"Stock insuficiente. Disponible: {videojuego.stock}."})
        return data


# SERIALIZER PARA AGREGAR VIDEOJUEGOS A UN PEDIDO

class DetallePedidoEntradaSerializer(serializers.Serializer):

    videojuego = ObjectIdRelatedField(
        queryset=Videojuego.objects.all()
    )

    cantidad = serializers.IntegerField(min_value=1)

# SERIALIZER PARA CONSULTAR PEDIDOS

class PedidoSerializer(serializers.ModelSerializer):
    id = serializers.CharField(read_only=True)
    detalles = DetallePedidoSerializer(many=True, read_only=True)

    class Meta:
        model = Pedido
        fields = ['id', 'cliente_nombre', 'cliente_correo', 'fecha_pedido', 'estado', 'total', 'detalles']
        read_only_fields = ['total', 'fecha_pedido']

# SERIALIZER PARA CREAR PEDIDOS

class PedidoCreateSerializer(serializers.Serializer):

    cliente_nombre = serializers.CharField(max_length=120)

    cliente_correo = serializers.EmailField()

    detalles = DetallePedidoEntradaSerializer(
        many=True
    )

    def validate_cliente_nombre(self, value):

        nombre = value.strip()

        if not nombre:
            raise serializers.ValidationError(
                "El nombre del cliente es obligatorio."
            )

        return nombre

    def validate_detalles(self, value):

        if not value:
            raise serializers.ValidationError(
                "El pedido debe contener al menos un videojuego."
            )

        # Agrupar cantidades cuando un videojuego aparece
        # más de una vez en el mismo pedido.

        cantidades = {}

        videojuegos = {}

        for item in value:

            videojuego = item['videojuego']

            cantidad = item['cantidad']

            identificador = str(videojuego.pk)

            cantidades[identificador] = (
                cantidades.get(identificador, 0) + cantidad
            )

            videojuegos[identificador] = videojuego

        # Comprobar el stock total necesario.

        for identificador, cantidad_total in cantidades.items():

            videojuego = videojuegos[identificador]

            if videojuego.stock < cantidad_total:

                raise serializers.ValidationError(
                    f"Stock insuficiente para {videojuego.titulo}. "
                    f"Disponible: {videojuego.stock}. "
                    f"Solicitado: {cantidad_total}."
                )

        return value

    def create(self, validated_data):

        from django_mongodb_backend import transaction

        detalles_recibidos = validated_data.pop('detalles')

        with transaction.atomic():

            pedido = Pedido.objects.create(
                cliente_nombre=validated_data['cliente_nombre'],
                cliente_correo=validated_data['cliente_correo'],
                total=Decimal('0.00')
            )

            total_pedido = Decimal('0.00')

            for item in detalles_recibidos:

                videojuego = Videojuego.objects.get(
                    pk=item['videojuego'].pk
                )

                cantidad = item['cantidad']

                # Segunda comprobación del stock,
                # utilizando la información más reciente.

                if videojuego.stock < cantidad:

                    raise serializers.ValidationError(
                        f"Stock insuficiente para {videojuego.titulo}."
                    )

                precio = Decimal(str(videojuego.precio))

                subtotal = (
                    precio * cantidad
                ).quantize(Decimal('0.01'))

                # Descontar stock.

                videojuego.stock -= cantidad

                videojuego.save(
                    update_fields=['stock']
                )

                # Registrar el detalle del pedido.

                DetallePedido.objects.create(
                    pedido=pedido,
                    videojuego=videojuego,
                    cantidad=cantidad,
                    precio_unitario=precio,
                    subtotal=subtotal
                )

                total_pedido += subtotal

            # Actualizar total del pedido.

            pedido.total = total_pedido

            pedido.save(
                update_fields=['total']
            )

        return pedido

# SERIALIZER PARA ACTUALIZAR PEDIDOS


class PedidoActualizarSerializer(serializers.Serializer):

    cliente_nombre = serializers.CharField(
        max_length=120,
        required=False
    )

    cliente_correo = serializers.EmailField(
        required=False
    )

    estado = serializers.ChoiceField(
        choices=Pedido.ESTADOS,
        required=False
    )

    def validate_cliente_nombre(self, value):

        nombre = value.strip()

        if not nombre:
            raise serializers.ValidationError(
                "El nombre no puede estar vacío."
            )

        return nombre

    def validate(self, data):

        if not data:
            raise serializers.ValidationError(
                "Debes enviar al menos un dato para actualizar."
            )

        return data

# SERIALIZER PARA MODIFICAR CANTIDADES DE DETALLES

class DetallePedidoActualizarSerializer(serializers.Serializer):

    cantidad = serializers.IntegerField(min_value=1)

# SERIALIZER PARA CREAR DETALLES DE PEDIDO

class DetallePedidoCreateSerializer(serializers.Serializer):

    pedido = ObjectIdRelatedField(
        queryset=Pedido.objects.all()
    )

    videojuego = ObjectIdRelatedField(
        queryset=Videojuego.objects.all()
    )

    cantidad = serializers.IntegerField(min_value=1)
