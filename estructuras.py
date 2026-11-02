# --- CLASE PRINCIPAL (POO) ---
class ObjetoPerdido:
    def __init__(self, codigo, nombre, categoria, fecha, hora, lugar, estado, registrado_por, contacto, imagen=None, observacion=""):
        self.codigo = codigo
        self.nombre = nombre
        self.categoria = categoria
        self.fecha = fecha
        self.hora = hora
        self.lugar = lugar
        self.estado = estado
        self.registrado_por = registrado_por
        self.contacto = contacto
        self.imagen = imagen
        self.observacion = observacion  # <-- Guardamos la descripción u observación
class Nodo:
    def __init__(self, objeto):
        self.objeto = objeto
        self.siguiente = None

# --- 1. LISTA ENLAZADA (Inventario general) ---
class ListaEnlazadaObjetos:
    def __init__(self):
        self.cabeza = None

    def agregar(self, objeto):
        nuevo_nodo = Nodo(objeto)
        if not self.cabeza:
            self.cabeza = nuevo_nodo
        else:
            actual = self.cabeza
            while actual.siguiente:
                actual = actual.siguiente
            actual.siguiente = nuevo_nodo

    def obtener_todos(self):
        elementos = []
        actual = self.cabeza
        while actual:
            elementos.append(actual.objeto)
            actual = actual.siguiente
        return elementos

# --- 2. TABLA HASH (Búsqueda rápida por código) ---
class TablaHashObjetos:
    def __init__(self, capacidad=50):
        self.capacidad = capacidad
        self.tabla = [[] for _ in range(capacidad)]

    def _funcion_hash(self, codigo):
        return sum(ord(c) for c in str(codigo)) % self.capacidad

    def insertar(self, objeto):
        indice = self._funcion_hash(objeto.codigo)
        for item in self.tabla[indice]:
            if item.codigo == objeto.codigo:
                item = objeto
                return
        self.tabla[indice].append(objeto)

    def buscar(self, codigo):
        indice = self._funcion_hash(codigo)
        for item in self.tabla[indice]:
            if item.codigo.lower() == str(codigo).lower():
                return item
        return None

# --- 3. PILA / LIFO (Historial de auditoría / Deshacer) ---
class PilaHistorial:
    def __init__(self):
        self.elementos = []

    def apilar(self, accion):
        self.elementos.append(accion)

    def desapilar(self):
        if self.elementos:
            return self.elementos.pop()
        return None

    def obtener_todos(self):
        return list(reversed(self.elementos))

# --- 4. COLA / FIFO (Fila de reclamos de objetos) ---
class ColaReclamos:
    def __init__(self):
        self.elementos = []

    def encolar(self, solicitud):
        self.elementos.append(solicitud)

    def desencolar(self):
        if self.elementos:
            return self.elementos.pop(0)
        return None

    def obtener_todos(self):
        return self.elementos