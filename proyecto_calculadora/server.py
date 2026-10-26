"""Backend sencillo para la calculadora de construcción.

Este archivo usa Flask y archivos JSON. Está escrito con fines educativos.
"""

from flask import Flask, jsonify, request, session, send_from_directory
from functools import wraps
from pathlib import Path
from datetime import datetime
import hashlib
import json
import math
import uuid



CARPETA_PROYECTO = Path(__file__).parent
CARPETA_DATOS = CARPETA_PROYECTO / "data"
ARCHIVO_USUARIOS = CARPETA_DATOS / "usuarios.json"
ARCHIVO_CALCULOS = CARPETA_DATOS / "calculos.json"

CARPETA_DATOS.mkdir(exist_ok=True)

app = Flask(__name__, static_folder=None)
app.secret_key = "clave-local-para-el-proyecto"




def leer_json(archivo, valor_inicial):
    """Lee una lista desde un archivo JSON."""
    if not archivo.exists():
        guardar_json(archivo, valor_inicial)
        return valor_inicial

    try:
        with open(archivo, "r", encoding="utf-8") as file:
            return json.load(file)
    except json.JSONDecodeError:
        return valor_inicial


def guardar_json(archivo, datos):
    """Guarda datos en un archivo JSON."""
    with open(archivo, "w", encoding="utf-8") as file:
        json.dump(datos, file, indent=2, ensure_ascii=False)


def fecha_actual():
    return datetime.now().isoformat(timespec="seconds")


def crear_id():
    return str(uuid.uuid4())


def usuario_publico(usuario):
    """Devuelve el usuario sin mostrar su contraseña."""
    return {
        "id": usuario["id"],
        "nombre": usuario["nombre"],
        "usuario": usuario["usuario"]
    }


def usuario_actual():
    """Busca el usuario que inició sesión."""
    id_usuario = session.get("usuario_id")
    usuarios = leer_json(ARCHIVO_USUARIOS, [])
    return next((u for u in usuarios if u["id"] == id_usuario), None)


def necesita_sesion(funcion):
    """Evita usar los cálculos sin iniciar sesión."""
    @wraps(funcion)
    def revisar_sesion(*args, **kwargs):
        if usuario_actual() is None:
            return jsonify({"error": "Debes iniciar sesión primero."}), 401
        return funcion(*args, **kwargs)
    return revisar_sesion




def numero(datos, nombre):
    """Convierte un dato en número y revisa que sea positivo."""
    try:
        valor = float(datos[nombre])
    except (KeyError, TypeError, ValueError):
        raise ValueError(f"El campo {nombre} debe ser un número.")

    if valor <= 0:
        raise ValueError(f"El campo {nombre} debe ser mayor que cero.")
    return valor


def material(nombre, valor, unidad, decimales=2):
    return {
        "nombre": nombre,
        "valor": round(valor, decimales),
        "unidad": unidad
    }


def calcular(tipo, datos):
    """Realiza un cálculo según el tipo elegido en el frontend."""

    if tipo == "muro":
        espesor = numero(datos, "espesor")
        largo = numero(datos, "largo")
        alto = numero(datos, "alto")

        if round(espesor, 2) == 0.30:
            cemento_por_metro = 15.2
            arena_por_metro = 0.115
            ladrillos_por_metro = 120
        elif round(espesor, 2) == 0.20:
            cemento_por_metro = 12.8
            arena_por_metro = 0.095
            ladrillos_por_metro = 100
        else:
            raise ValueError("El espesor debe ser 0.20 o 0.30 metros.")

        superficie = largo * alto
        materiales = [
            material("Superficie", superficie, "m²"),
            material("Cemento", superficie * cemento_por_metro, "kg"),
            material("Arena", superficie * arena_por_metro, "m³", 3),
            material("Ladrillos", math.ceil(superficie * ladrillos_por_metro), "unidades", 0)
        ]
        formula = "Superficie = largo × alto."

    elif tipo == "viga":
        largo = numero(datos, "largo")
        materiales = [
            material("Cemento", largo * 4.2, "kg"),
            material("Arena", largo * 0.009333, "m³", 3),
            material("Piedra", largo * 0.009333, "m³", 3),
            material("Hierro del 8", largo * 1.8667, "m"),
            material("Hierro del 4", largo * 1.4, "m")
        ]
        formula = "Cada material se calcula con un coeficiente por metro de viga."

    elif tipo == "columna":
        largo = numero(datos, "largo")
        materiales = [
            material("Cemento", largo * 7.5, "kg"),
            material("Arena", largo * 0.016, "m³", 3),
            material("Piedra", largo * 0.016, "m³", 3),
            material("Hierro del 10", largo * 6, "m"),
            material("Hierro del 4", largo * 3, "m")
        ]
        formula = "Cada material se calcula con un coeficiente por metro de columna."

    elif tipo == "contrapiso":
        espesor = numero(datos, "espesor")
        ancho = numero(datos, "ancho")
        largo = numero(datos, "largo")
        volumen = espesor * ancho * largo
        materiales = [
            material("Volumen", volumen, "m³"),
            material("Cemento", volumen * 105, "kg"),
            material("Arena", volumen * 0.45, "m³"),
            material("Piedra", volumen * 0.90, "m³")
        ]
        formula = "Volumen = espesor × ancho × largo."

    elif tipo == "techo":
        espesor = numero(datos, "espesor")
        ancho = numero(datos, "ancho")
        largo = numero(datos, "largo")
        superficie = ancho * largo
        materiales = [
            material("Superficie", superficie, "m²"),
            material("Volumen", superficie * espesor, "m³"),
            material("Cemento", superficie * 33, "kg"),
            material("Arena", superficie * 0.072, "m³", 3),
            material("Piedra", superficie * 0.072, "m³", 3),
            material("Hierro del 8", superficie * 7, "m"),
            material("Hierro del 6", superficie * 4, "m")
        ]
        formula = "Superficie = ancho × largo."

    elif tipo == "pisos":
        ancho = numero(datos, "ancho")
        largo = numero(datos, "largo")
        superficie = ancho * largo
        materiales = [
            material("Superficie base", superficie, "m²"),
            material("Superficie con 10% extra", superficie * 1.10, "m²")
        ]
        formula = "Superficie final = ancho × largo × 1.10."

    elif tipo == "pintura":
        superficie = numero(datos, "superficie")
        litros = math.ceil(superficie / 6)
        materiales = [
            material("Superficie", superficie, "m²"),
            material("Rendimiento", 6, "m² / litro"),
            material("Pintura necesaria", litros, "litros", 0)
        ]
        formula = "Litros = techo(superficie ÷ 6)."

    else:
        raise ValueError("El tipo de cálculo no existe.")

    nombres = {
        "muro": "Muro de ladrillo",
        "viga": "Viga de hormigón",
        "columna": "Columna de hormigón",
        "contrapiso": "Contrapiso",
        "techo": "Techo",
        "pisos": "Pisos",
        "pintura": "Pintura"
    }

    return {
        "titulo": nombres[tipo],
        "formula": formula,
        "items": materiales
    }



@app.post("/api/auth/register")
def registrar():
    datos = request.get_json() or {}
    nombre = datos.get("nombre", "").strip()
    usuario = datos.get("usuario", "").strip().lower()
    password = datos.get("password", "")

    if len(nombre) < 2 or len(usuario) < 3 or len(password) < 6:
        return jsonify({"error": "Revisa los datos. La contraseña debe tener mínimo 6 caracteres."}), 400

    usuarios = leer_json(ARCHIVO_USUARIOS, [])
    if any(u["usuario"] == usuario for u in usuarios):
        return jsonify({"error": "Ese usuario ya existe."}), 400

    nuevo_usuario = {
        "id": crear_id(),
        "nombre": nombre,
        "usuario": usuario,
        "password": hashlib.sha256(password.encode()).hexdigest()
    }
    usuarios.append(nuevo_usuario)
    guardar_json(ARCHIVO_USUARIOS, usuarios)
    session["usuario_id"] = nuevo_usuario["id"]

    return jsonify({"usuario": usuario_publico(nuevo_usuario)}), 201


@app.post("/api/auth/login")
def iniciar_sesion():
    datos = request.get_json() or {}
    usuario = datos.get("usuario", "").strip().lower()
    password = datos.get("password", "")
    clave = hashlib.sha256(password.encode()).hexdigest()

    usuarios = leer_json(ARCHIVO_USUARIOS, [])
    encontrado = next((u for u in usuarios if u["usuario"] == usuario and u["password"] == clave), None)

    if encontrado is None:
        return jsonify({"error": "Usuario o contraseña incorrectos."}), 401

    session["usuario_id"] = encontrado["id"]
    return jsonify({"usuario": usuario_publico(encontrado)})


@app.post("/api/auth/logout")
def cerrar_sesion():
    session.clear()
    return jsonify({"mensaje": "Sesión cerrada."})


@app.get("/api/auth/me")
def ver_usuario():
    usuario = usuario_actual()
    if usuario is None:
        return jsonify({"error": "No hay una sesión activa."}), 401
    return jsonify({"usuario": usuario_publico(usuario)})



@app.post("/api/calculations")
@necesita_sesion
def crear_calculo():
    datos = request.get_json() or {}
    tipo = datos.get("tipo", "")
    entradas = datos.get("entradas", {})

    try:
        resultado = calcular(tipo, entradas)
    except ValueError as error:
        return jsonify({"error": str(error)}), 400

    calculo = {
        "id": crear_id(),
        "user_id": session["usuario_id"],
        "tipo": tipo,
        "entradas": entradas,
        "resultado": resultado,
        "created_at": fecha_actual(),
        "updated_at": fecha_actual()
    }

    calculos = leer_json(ARCHIVO_CALCULOS, [])
    calculos.append(calculo)
    guardar_json(ARCHIVO_CALCULOS, calculos)
    return jsonify({"calculo": calculo}), 201


@app.get("/api/calculations")
@necesita_sesion
def listar_calculos():
    calculos = leer_json(ARCHIVO_CALCULOS, [])
    propios = [c for c in calculos if c["user_id"] == session["usuario_id"]]
    propios.sort(key=lambda c: c["created_at"], reverse=True)
    return jsonify({"calculos": propios})


def buscar_calculo(id_calculo):
    calculos = leer_json(ARCHIVO_CALCULOS, [])
    return next((c for c in calculos
                 if c["id"] == id_calculo and c["user_id"] == session["usuario_id"]), None)


@app.get("/api/calculations/<id_calculo>")
@necesita_sesion
def ver_calculo(id_calculo):
    calculo = buscar_calculo(id_calculo)
    if calculo is None:
        return jsonify({"error": "Cálculo no encontrado."}), 404
    return jsonify({"calculo": calculo})


@app.put("/api/calculations/<id_calculo>")
@necesita_sesion
def editar_calculo(id_calculo):
    datos = request.get_json() or {}
    tipo = datos.get("tipo", "")
    entradas = datos.get("entradas", {})

    try:
        resultado = calcular(tipo, entradas)
    except ValueError as error:
        return jsonify({"error": str(error)}), 400

    calculos = leer_json(ARCHIVO_CALCULOS, [])
    calculo = next((c for c in calculos
                    if c["id"] == id_calculo and c["user_id"] == session["usuario_id"]), None)
    if calculo is None:
        return jsonify({"error": "Cálculo no encontrado."}), 404

    calculo["tipo"] = tipo
    calculo["entradas"] = entradas
    calculo["resultado"] = resultado
    calculo["updated_at"] = fecha_actual()
    guardar_json(ARCHIVO_CALCULOS, calculos)
    return jsonify({"calculo": calculo})


@app.delete("/api/calculations/<id_calculo>")
@necesita_sesion
def eliminar_calculo(id_calculo):
    calculos = leer_json(ARCHIVO_CALCULOS, [])
    cantidad_anterior = len(calculos)
    calculos = [c for c in calculos if not (
        c["id"] == id_calculo and c["user_id"] == session["usuario_id"]
    )]

    if len(calculos) == cantidad_anterior:
        return jsonify({"error": "Cálculo no encontrado."}), 404

    guardar_json(ARCHIVO_CALCULOS, calculos)
    return jsonify({"mensaje": "Cálculo eliminado correctamente."})




@app.get("/")
def inicio():
    return send_from_directory(CARPETA_PROYECTO, "index.html")


@app.get("/<path:nombre_archivo>")
def archivo_frontend(nombre_archivo):
    
    if nombre_archivo.startswith("data/") or ".." in nombre_archivo:
        return jsonify({"error": "Archivo no permitido."}), 403
    return send_from_directory(CARPETA_PROYECTO, nombre_archivo)


if __name__ == "__main__":
    print("Servidor iniciado en http://127.0.0.1:8000")
    app.run(host="127.0.0.1", port=8000, debug=True)
