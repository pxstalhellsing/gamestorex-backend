from django.db import models

class Categoria(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    descripcion = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.nombre


class Videojuego(models.Model):
    titulo = models.CharField(max_length=150)
    descripcion = models.TextField()
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.IntegerField(default=0)
    plataforma = models.CharField(max_length=50, default="PC")
    categoria = models.ForeignKey(
        Categoria,
        on_delete=models.CASCADE,
        related_name='videojuegos'
    )

    def __str__(self):
        return f"{self.titulo} ({self.plataforma})"


class Pedido(models.Model):
    ESTADOS = [
        ('PENDIENTE', 'Pendiente'),
        ('PAGADO', 'Pagado'),
        ('CANCELADO', 'Cancelado'),
    ]
    cliente_nombre = models.CharField(max_length=120)
    cliente_correo = models.EmailField()
    fecha_pedido = models.DateTimeField(auto_now_add=True)
    estado = models.CharField(max_length=20, choices=ESTADOS, default='PENDIENTE')
    total = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)

    def __str__(self):
        return f"Pedido de {self.cliente_nombre} - ${self.total}"


class DetallePedido(models.Model):
    pedido = models.ForeignKey(
        Pedido,
        on_delete=models.CASCADE,
        related_name='detalles'
    )
    videojuego = models.ForeignKey(
        Videojuego,
        on_delete=models.PROTECT,
        related_name='ventas'
    )
    cantidad = models.IntegerField()
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    subtotal = models.DecimalField(max_digits=12, decimal_places=2)