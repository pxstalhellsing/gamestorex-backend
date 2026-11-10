| `api/models.py` | 20% | Apoyo para definir relaciones `ForeignKey` entre `Categoria`, `Videojuego`, `Pedido` y `DetallePedido`. |
| `api/views.py` | 50% | Generación de endpoints CRUD con `@api_view`, manejo de `ObjectId` y lógica de descuento de stock. |
| `api/serializers.py` | 40% | Sugerencias de validación de precios/stock y serialización de `ObjectId` en relaciones. |
| `api/urls.py` | 10% | Consulta de sintaxis para el enrutamiento de los endpoints. |
| `config/settings.py` | 15% | Apoyo en la configuración de conexión a MongoDB. |
| `seed_data.py` | 50% | Script de apoyo para poblar la base de datos MongoDB con el catálogo inicial. |

---

## Preguntas Reflexivas

### 1. ¿En qué aspectos del proyecto utilizaron inteligencia artificial?
Utilizamos inteligencia artificial como asistente de consulta para adaptar el manejo de identificadores `ObjectId` de MongoDB dentro de Django REST Framework (`ObjectIdRelatedField` y funciones de búsqueda en `views.py`) y para crear los serializadores.

### 2. ¿Qué partes del código fueron desarrolladas principalmente por ustedes?
Diseñamos los 4 modelos de datos (`Categoria`, `Videojuego`, `Pedido`, `DetallePedido`) y sus atributos en `api/models.py`, definimos las reglas de validación de precios positivos y control de stock en `api/serializers.py`, configuramos la base de datos local y realizamos las pruebas de funcionamiento de cada endpoint.

### 3. ¿Qué errores o problemas encontraron en las respuestas generadas por IA?
En un inicio encontramos problemas al serializar llaves foráneas en MongoDB porque Django REST Framework intentaba convertir objetos `ObjectId` directamente a JSON arrojando `TypeError: Object of type ObjectId is not JSON serializable`. Lo solucionamos creando una clase personalizada `ObjectIdRelatedField` en `serializers.py` y validando los IDs con `bson.ObjectId` en `views.py`.

### 4. ¿Cómo verificaron que el código sugerido funcionaba correctamente?
Ejecutando las migraciones hacia MongoDB, poblando la base de datos y probando manualmente todas las rutas HTTP en Postman, verificando tanto los casos exitosos (descuento de stock y suma del total del pedido) como los casos de error (`400 Bad Request` al ingresar precios negativos o superar el stock disponible).

### 5. ¿Qué conocimientos adquirieron durante el desarrollo?
Comprendimos cómo conectar Django con una base de datos NoSQL como MongoDB utilizando `ObjectId`, el funcionamiento de los `Serializers` para validar datos antes de guardarlos, la diferencia práctica entre los métodos HTTP en una API REST y cómo implementar reglas de negocio reales en el servidor.