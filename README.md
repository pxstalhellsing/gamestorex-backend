# GameStoreX Back-End — API REST con Django y MongoDB

## 1. Descripción

En la primera etapa del proyecto (`gamestorex`), la tienda de videojuegos funcionaba en React consumiendo datos estáticos simulados. Este Back-End reemplaza los datos simulados por persistencia real en **MongoDB** utilizando **Django** y **Django REST Framework (DRF)**.

El sistema permite:
- Realizar operaciones **CRUD completas** sobre Categorías, Videojuegos, Pedidos y Detalles de Pedido.
- Importar videojuegos reales directamente desde la enciclopedia **IGDB (Internet Game Database)** hacia MongoDB, asignándoles stock y precios automáticamente y exponiéndolos en formato JSON.
- Filtrar videojuegos por plataforma, búsqueda de texto y disponibilidad de stock.
- Ejecutar **reglas de negocio reales**: validación de existencias, descuento automático de stock al comprar, cálculo automático de subtotales/totales y restitución de stock en caso de cancelación o eliminación de un pedido.

---

## 2. Tecnologías Utilizadas

- **Python 3.12+** — Lenguaje principal de desarrollo.
- **Django 5.2** — Framework web Back-End y ORM.
- **Django MongoDB Backend (`django-mongodb-backend`)** — Conector oficial de MongoDB para Django con soporte nativo de `ObjectId`.
- **Django REST Framework (DRF)** — Construcción de endpoints REST, serialización JSON y validaciones.
- **MongoDB** — Base de datos NoSQL orientada a documentos.
- **IGDB API v4 & Requests** — Integración con el servicio externo de Twitch/IGDB para poblar el catálogo de videojuegos.
- **Postman / Insomnia** — Herramientas utilizadas para probar y documentar los endpoints HTTP.

---

## 3. Estructura del Proyecto

```text
gamestorex-backend/
├── api/                        # Aplicación principal de la tienda
│   ├── migrations/             # Migraciones de los modelos de la aplicación
│   ├── admin.py                # Registro de modelos en el panel de administración
│   ├── apps.py                 # Configuración de la app
│   ├── models.py               # Modelos: Categoria, Videojuego, Pedido, DetallePedido
│   ├── serializers.py          # Serializers, validaciones y manejo de ObjectId
│   ├── tests.py                # Pruebas unitarias de la API
│   ├── urls.py                 # Definición de rutas de la API (/api/...)
│   └── views.py                # Vistas basadas en @api_view, lógica de negocio e IGDB
├── config/                     # Configuración global del proyecto Django
│   ├── settings.py             # Configuración de base de datos MongoDB, apps y middlewares
│   ├── urls.py                 # Enrutador raíz del proyecto
│   ├── asgi.py
│   └── wsgi.py
├── mongo_migrations/           # Migraciones adaptadas para el motor MongoDB
├── .gitignore
├── manage.py
├── requirements.txt            # Lista de dependencias del proyecto
├── README.md                   # Documentación del proyecto y de la API
└── USO_IA.md                   # Declaración de uso de Inteligencia Artificial
```

---

## 4. Modelos de Datos y Relaciones (`api/models.py`)

El sistema implementa **4 modelos relacionados** mediante claves foráneas (`ForeignKey`), utilizando `ObjectId` como identificador primario en MongoDB:

### 4.1. `Categoria`
Representa el género o clasificación de los videojuegos.
- `id` (`ObjectId`, automático)
- `nombre` (`CharField`, máx. 100 caracteres, único)
- `descripcion` (`TextField`, opcional)

### 4.2. `Videojuego`
Representa cada producto disponible en el catálogo de GameStoreX.
- `id` (`ObjectId`, automático)
- `titulo` (`CharField`, máx. 150 caracteres)
- `descripcion` (`TextField`)
- `precio` (`DecimalField`, máx. 10 dígitos, 2 decimales)
- `stock` (`IntegerField`, por defecto `0`)
- `plataforma` (`CharField`, máx. 50 caracteres, por defecto `"PC"`)
- `categoria` (**`ForeignKey`** hacia `Categoria`, `on_delete=models.CASCADE`, `related_name='videojuegos'`)

### 4.3. `Pedido`
Representa la cabecera de una orden de compra realizada por un cliente.
- `id` (`ObjectId`, automático)
- `cliente_nombre` (`CharField`, máx. 120 caracteres)
- `cliente_correo` (`EmailField`)
- `fecha_pedido` (`DateTimeField`, `auto_now_add=True`)
- `estado` (`CharField`, opciones: `PENDIENTE`, `PAGADO`, `CANCELADO`, por defecto `PENDIENTE`)
- `total` (`DecimalField`, calculado automáticamente a partir de los detalles)

### 4.4. `DetallePedido`
Representa cada línea de producto dentro de un pedido.
- `id` (`ObjectId`, automático)
- `pedido` (**`ForeignKey`** hacia `Pedido`, `on_delete=models.CASCADE`, `related_name='detalles'`)
- `videojuego` (**`ForeignKey`** hacia `Videojuego`, `on_delete=models.PROTECT`, `related_name='ventas'`)
- `cantidad` (`IntegerField`)
- `precio_unitario` (`DecimalField`, capturado automáticamente desde `videojuego.precio`)
- `subtotal` (`DecimalField`, calculado automáticamente como `precio_unitario * cantidad`)

---

## 5. Validaciones y Lógica de Negocio Implementadas

1. **Validaciones de Integridad (`api/serializers.py`):**
   - `validate_precio`: Impide crear o actualizar videojuegos con precio menor o igual a `0.00`.
   - `validate_stock`: Impide registrar un stock negativo (`< 0`).
   - `validate` en `DetallePedidoSerializer`: Verifica que la `cantidad` sea mayor a `0` y comprueba en tiempo real que el `stock` disponible del videojuego sea suficiente para cubrir la cantidad solicitada.
   - `ObjectIdRelatedField`: Valida que los IDs enviados en llaves foráneas correspondan a un `ObjectId` válido de MongoDB y que el documento exista en la base de datos.

2. **Reglas de Negocio (`api/views.py`):**
   - **Descuento automático de Stock y Cálculo de Totales:** Al registrar un `DetallePedido` (`POST /api/detalles-pedido/`), el sistema obtiene el precio actual del videojuego desde la base de datos, calcula el `subtotal`, resta la cantidad comprada del `stock` del videojuego y suma el `subtotal` al `total` del `Pedido`.
   - **Restitución de Stock por Cancelación o Eliminación:** Si un pedido cambia su estado a `CANCELADO` (`PATCH /api/pedidos/<id>/`) o si se elimina un detalle/pedido (`DELETE`), el sistema devuelve automáticamente las unidades al `stock` original de cada videojuego involucrado.
   - **Protección de Categorías:** No se permite eliminar una categoría que tenga videojuegos asociados.

---

## 6. Instrucciones de Instalación, Migraciones y Ejecución

### Prerrequisitos
- Tener instalado **Python 3.12+** y **MongoDB** ejecutándose localmente (por defecto en `mongodb://localhost:27017/`).

### Paso a paso

1. **Clonar el repositorio:**
   ```bash
   git clone https://github.com/pxstalhellsing/gamestorex-backend.git
   cd gamestorex-backend
   ```

2. **Crear y activar un entorno virtual:**
   ```bash
   python -m venv venv
   # En Windows:
   venv\Scripts\activate
   # En Linux / macOS:
   source venv/bin/activate
   ```

3. **Instalar las dependencias:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Crear y aplicar las migraciones en MongoDB:**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

5. **Iniciar el servidor de desarrollo:**
   ```bash
   python manage.py runserver
   ```
   La API estará disponible en: `http://127.0.0.1:8000/api/`

---

## 7. Documentación de Endpoints de la API

### 7.1. Categorías (`/api/categorias/`)

| Método HTTP | Ruta | Descripción | Códigos de Estado |
| :--- | :--- | :--- | :--- |
| `GET` | `/api/categorias/` | Lista todas las categorías registradas. | `200 OK` |
| `POST` | `/api/categorias/` | Crea una nueva categoría. | `201 Created`, `400 Bad Request` |
| `GET` | `/api/categorias/<id>/` | Obtiene una categoría por su `ObjectId`. | `200 OK`, `404 Not Found` |
| `PUT` / `PATCH` | `/api/categorias/<id>/` | Actualiza una categoría existente. | `200 OK`, `400 Bad Request`, `404 Not Found` |
| `DELETE` | `/api/categorias/<id>/` | Elimina una categoría (si no tiene juegos asociados). | `204 No Content`, `400 Bad Request`, `404 Not Found` |

**Ejemplo de Solicitud (`POST /api/categorias/`):**
```json
{
  "nombre": "RPG",
  "descripcion": "Videojuegos de rol y aventura de mundo abierto"
}
```

**Ejemplo de Respuesta (`201 Created`):**
```json
{
  "id": "67291f8a4c9d1e2b3a4f5678",
  "nombre": "RPG",
  "descripcion": "Videojuegos de rol y aventura de mundo abierto"
}
```

---

### 7.2. Videojuegos (`/api/videojuegos/`)

| Método HTTP | Ruta | Descripción | Códigos de Estado |
| :--- | :--- | :--- | :--- |
| `GET` | `/api/videojuegos/` | Lista todos los videojuegos del catálogo. | `200 OK` |
| `GET` | `/api/videojuegos/?plataforma=PS5&search=elden&disponibles=true` | Filtra videojuegos por plataforma, texto en el título o stock disponible (`> 0`). | `200 OK` |
| `POST` | `/api/videojuegos/` | Crea un nuevo videojuego validando precio y stock. | `201 Created`, `400 Bad Request` |
| `POST` | `/api/videojuegos/importar-igdb/` | Importa videojuegos desde la API de **IGDB** a MongoDB y los retorna en JSON. | `201 Created`, `400 Bad Request`, `502 Bad Gateway` |
| `GET` | `/api/videojuegos/<id>/` | Obtiene el detalle de un videojuego por su `ObjectId`. | `200 OK`, `404 Not Found` |
| `PUT` / `PATCH` | `/api/videojuegos/<id>/` | Actualiza los datos o el stock de un videojuego. | `200 OK`, `400 Bad Request`, `404 Not Found` |
| `DELETE` | `/api/videojuegos/<id>/` | Elimina un videojuego del catálogo. | `204 No Content`, `404 Not Found` |

**Ejemplo de Solicitud (`POST /api/videojuegos/`):**
```json
{
  "titulo": "Elden Ring",
  "descripcion": "Un vasto mundo lleno de misterio creado por FromSoftware.",
  "precio": "49990.00",
  "stock": 10,
  "plataforma": "PS5",
  "categoria": "67291f8a4c9d1e2b3a4f5678"
}
```

**Ejemplo de Respuesta (`201 Created`):**
```json
{
  "id": "672920154c9d1e2b3a4f5679",
  "titulo": "Elden Ring",
  "descripcion": "Un vasto mundo lleno de misterio creado por FromSoftware.",
  "precio": "49990.00",
  "stock": 10,
  "plataforma": "PS5",
  "categoria": "67291f8a4c9d1e2b3a4f5678",
  "categoria_nombre": "RPG"
}
```

**Ejemplo de Importación desde IGDB (`POST /api/videojuegos/importar-igdb/`):**
```json
{
  "buscar": "Resident Evil",
  "limite": 5
}
```

---

### 7.3. Pedidos (`/api/pedidos/`)

| Método HTTP | Ruta | Descripción | Códigos de Estado |
| :--- | :--- | :--- | :--- |
| `GET` | `/api/pedidos/` | Lista todos los pedidos incluyendo el arreglo de sus `detalles`. | `200 OK` |
| `POST` | `/api/pedidos/` | Crea un nuevo pedido (inicia con `total` en `0.00`). | `201 Created`, `400 Bad Request` |
| `GET` | `/api/pedidos/<id>/` | Obtiene un pedido específico con sus ítems y total actualizado. | `200 OK`, `404 Not Found` |
| `PUT` / `PATCH` | `/api/pedidos/<id>/` | Actualiza datos o estado del pedido (pasar a `CANCELADO` restituye el stock). | `200 OK`, `400 Bad Request`, `404 Not Found` |
| `DELETE` | `/api/pedidos/<id>/` | Elimina un pedido y restituye el stock de sus productos. | `204 No Content`, `404 Not Found` |

**Ejemplo de Solicitud (`POST /api/pedidos/`):**
```json
{
  "cliente_nombre": "Javier Vergara",
  "cliente_correo": "javier.vergara@autonoma.cl",
  "estado": "PENDIENTE"
}
```

**Ejemplo de Respuesta (`201 Created`):**
```json
{
  "id": "672921004c9d1e2b3a4f5680",
  "cliente_nombre": "Javier Vergara",
  "cliente_correo": "javier.vergara@autonoma.cl",
  "fecha_pedido": "2026-11-05T12:30:00Z",
  "estado": "PENDIENTE",
  "total": "0.00",
  "detalles": []
}
```

---

### 7.4. Detalles de Pedido (`/api/detalles-pedido/`)

| Método HTTP | Ruta | Descripción | Códigos de Estado |
| :--- | :--- | :--- | :--- |
| `GET` | `/api/detalles-pedido/` | Lista todos los detalles de pedidos registrados. | `200 OK` |
| `POST` | `/api/detalles-pedido/` | Agrega un videojuego a un pedido, valida y descuenta stock, y actualiza el `total` del pedido. | `201 Created`, `400 Bad Request` |
| `GET` | `/api/detalles-pedido/<id>/` | Obtiene el detalle de una línea de pedido específica. | `200 OK`, `404 Not Found` |
| `DELETE` | `/api/detalles-pedido/<id>/` | Elimina el ítem del pedido, devuelve el stock al videojuego y descuenta el subtotal del pedido. | `204 No Content`, `404 Not Found` |

**Ejemplo de Solicitud (`POST /api/detalles-pedido/`):**
```json
{
  "pedido": "672921004c9d1e2b3a4f5680",
  "videojuego": "672920154c9d1e2b3a4f5679",
  "cantidad": 2
}
```

**Ejemplo de Respuesta (`201 Created`):**
```json
{
  "id": "672921554c9d1e2b3a4f5681",
  "pedido": "672921004c9d1e2b3a4f5680",
  "videojuego": "672920154c9d1e2b3a4f5679",
  "videojuego_titulo": "Elden Ring",
  "cantidad": 2,
  "precio_unitario": "49990.00",
  "subtotal": "99980.00"
}
```
*(Al realizar esta operación, el stock de "Elden Ring" disminuye automáticamente de `10` a `8`, y el campo `total` del pedido `672921004c9d1e2b3a4f5680` se actualiza a `"99980.00"`).*

---

## 8. Declaración de Uso de IA

La declaración detallada sobre el uso de herramientas de Inteligencia Artificial en cada archivo del proyecto y las respuestas a las preguntas reflexivas se encuentran en el archivo [USO_IA.md](./USO_IA.md).

---

## 9. Autores

- **Pía Fuentes**
- **Javier Vergara**
- **Asignatura:** Desarrollo de Aplicaciones Web — Universidad Autónoma de Chile.
