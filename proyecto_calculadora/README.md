# Master en Construcción — Calculadora de materiales

Proyecto práctico con **frontend HTML/CSS/JavaScript** y **backend en Python**, sin base de datos SQL. La aplicación permite registrarse, iniciar sesión, calcular materiales y administrar un historial de cálculos.

> Importante: los coeficientes son estimaciones del ejercicio académico. No reemplazan el cálculo de un profesional de ingeniería o arquitectura.

## 1. Tecnologías utilizadas

- HTML5 para las pantallas.
- CSS3 para conservar el diseño original azul, amarillo y de construcción.
- JavaScript para enviar formularios sin recargar la página y consumir la API.
- Python 3 con Flask, una herramienta sencilla para crear rutas web.
- Archivos JSON para guardar usuarios y cálculos. No se utiliza MySQL, PostgreSQL ni SQLite.

## 2. Cómo ejecutar el proyecto

1. Instala Python 3.10 o una versión superior.
2. Abre una terminal dentro de esta carpeta.
3. Instala Flask una sola vez:

```bash
pip install -r requirements.txt
```

4. Ejecuta:

```bash
python server.py
```

5. Abre en el navegador:

```text
http://127.0.0.1:8000
```

Para detener el servidor presiona `Ctrl + C` en la terminal.

También puedes hacer doble clic en `iniciar.bat` si usas Windows, o ejecutar `bash iniciar.sh` en Linux/macOS. **No abras `index.html` directamente con doble clic**, porque en ese caso el navegador no encuentra la API de Python y el registro mostrará un error de conexión.

El archivo `server.py` es intencionalmente sencillo: las rutas están separadas por secciones y cada operación del CRUD tiene una función propia.

### Solución al mensaje “No se pudo conectar con el servidor Python”

Ese mensaje significa que el frontend está abierto, pero `server.py` no está ejecutándose. Cierra la pestaña, abre una terminal en la carpeta del proyecto, ejecuta `python server.py` y entra nuevamente por `http://127.0.0.1:8000`.

## 3. Cómo usarlo

1. Selecciona **Crear cuenta nueva**.
2. Registra nombre, usuario y una contraseña de mínimo seis caracteres.
3. Inicia sesión.
4. Escoge un tipo de cálculo del menú.
5. Escribe las medidas y presiona **Calcular y guardar**.
6. Consulta el resultado.
7. Regresa al menú para ver el historial y usar **Ver**, **Editar** o **Eliminar**.

## 4. Estructura de carpetas

```text
server.py                 Servidor Flask y API REST
index.html                Inicio de sesión
registro.html             Registro de usuario
menu.html                 Menú e historial CRUD
muro.html ... pintura.html Formularios de cálculo
resultado.html            Resultado dinámico
css/estilos.css           Diseño visual
js/app.js                 Conexión del frontend con la API
data/usuarios.json        Usuarios persistidos (se crea/actualiza localmente)
data/calculos.json        Historial persistido (se crea/actualiza localmente)
```

## 5. API y CRUD

Todas las rutas `/api` son atendidas por `server.py`:

| Método | Ruta | Función |
|---|---|---|
| `POST` | `/api/auth/register` | Crear usuario |
| `POST` | `/api/auth/login` | Iniciar sesión |
| `POST` | `/api/auth/logout` | Cerrar sesión |
| `GET` | `/api/auth/me` | Consultar usuario conectado |
| `POST` | `/api/calculations` | Crear y guardar cálculo |
| `GET` | `/api/calculations` | Listar historial del usuario |
| `GET` | `/api/calculations/{id}` | Consultar un cálculo |
| `PUT` | `/api/calculations/{id}` | Editar y recalcular |
| `DELETE` | `/api/calculations/{id}` | Eliminar cálculo |

El CRUD principal se aplica al historial de cálculos:

- **Create / Crear:** el formulario envía un `POST`.
- **Read / Leer:** el resultado y el historial usan `GET`.
- **Update / Actualizar:** el botón **Editar** carga los datos y usa `PUT`.
- **Delete / Eliminar:** el botón **Eliminar** usa `DELETE`.

Las contraseñas no se almacenan en texto plano: para este ejercicio se guardan como un hash SHA-256. La sesión se conserva mientras el servidor Python está encendido.

## 6. Archivos JSON

No borres manualmente `data/usuarios.json` ni `data/calculos.json` mientras estés usando la aplicación. Si quieres comenzar una demostración desde cero, detén el servidor y reemplaza el contenido de ambos archivos por:

```json
[]
```

## 7. Publicar en GitHub

Después de crear un repositorio público vacío en GitHub, desde esta carpeta ejecuta:

```bash
git init
git add .
git commit -m "Backend Python y CRUD de calculadora"
git branch -M main
git remote add origin https://github.com/TU_USUARIO/NOMBRE_DEL_REPOSITORIO.git
git push -u origin main
```

Cambia `TU_USUARIO` y `NOMBRE_DEL_REPOSITORIO` por tus datos reales. No publiques contraseñas, tokens ni información personal.

## 8. Qué explicar en la sustentación

- `server.py` sirve las páginas y recibe solicitudes HTTP.
- `app.js` captura los formularios y usa `fetch()` para comunicarse con Python.
- Las rutas REST separan autenticación y cálculos.
- `calculos.json` reemplaza una tabla SQL para este proyecto académico.
- El usuario solo consulta sus propios cálculos porque cada registro guarda `user_id`.
- Los resultados se calculan en Python y regresan en formato JSON.
- El diseño original se conservó y se mejoró con mensajes de validación, estado de carga, historial responsive y botones de editar/eliminar.
