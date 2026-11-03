from django.urls import path
from . import views

urlpatterns = [
    path('categorias/', views.categoria_list_create, name='categorias-list'),
    path('videojuegos/', views.videojuego_list_create, name='videojuegos-list'),
    path('videojuegos/<str:pk>/', views.videojuego_detail, name='videojuegos-detail'),
    path('pedidos/', views.pedido_list_create, name='pedidos-list'),
    path('pedidos/agregar-item/', views.agregar_detalle_pedido, name='pedidos-agregar-item'),
]