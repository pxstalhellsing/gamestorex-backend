from rest_framework import serializers
from decimal import Decimal
from .models import Categoria, Videojuego, Pedido, DetallePedido
from bson import ObjectId
from bson.errors import InvalidId

class CategoriaSerializer(serializers.ModelSerializer):
    id = serializers.CharField(read_only=True)

    class Meta:
        model = Categoria
        fields = ['id', 'nombre', 'descripcion']


class VideojuegoSerializer(serializers.ModelSerializer):
    id = serializers.CharField(read_only=True)
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


class PedidoSerializer(serializers.ModelSerializer):
    id = serializers.CharField(read_only=True)
    detalles = DetallePedidoSerializer(many=True, read_only=True)

    class Meta:
        model = Pedido
        fields = ['id', 'cliente_nombre', 'cliente_correo', 'fecha_pedido', 'estado', 'total', 'detalles']
        read_only_fields = ['total', 'fecha_pedido']