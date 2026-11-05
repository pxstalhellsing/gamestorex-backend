from django.urls import path
from . import views

urlpatterns = [
    # Categorías
    path('categorias/', views.categoria_lista, name='categoria-lista'),
    path('categorias/<str:pk>/', views.categoria_detalle, name='categoria-detalle'),

    # Videojuegos
    path('videojuegos/', views.videojuego_lista, name='videojuego-lista'),
    path('videojuegos/<str:pk>/', views.videojuego_detalle, name='videojuego-detalle'),

    # Pedidos
    path('pedidos/', views.pedido_lista, name='pedido-lista'),
    path('pedidos/<str:pk>/', views.pedido_detalle, name='pedido-detalle'),

    # Detalles de Pedido
    path('detalles-pedido/', views.detalle_pedido_lista, name='detalle-pedido-lista'),
    path('detalles-pedido/<str:pk>/', views.detalle_pedido_item, name='detalle-pedido-item'),
]