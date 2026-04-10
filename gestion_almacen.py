import json
from collections import deque

#Estructra de datos de la estanteria

class NodoProducto:
    def __init__(self, nombre, cantidad, precio):
        self.nombre = nombre
        self.cantidad = cantidad
        self.precio = precio
        self.siguiente = None 

# Lista enlazada que gestiona los productos de una estanteria concreta
class EstanteriaEnlazada:
    def __init__(self, nombre_estanteria):
        self.nombre = nombre_estanteria
        self.cabeza = None

    # 1. Funcion para ingresar un producto a la estanteria
    # Complejidad: O(P) en el peor caso, Omega(1) en el mejor
    def ingresar_producto(self, nombre, cantidad, precio):
        nodo_actual = self.cabeza
        
        while nodo_actual is not None:
            if nodo_actual.nombre == nombre:
                nodo_actual.cantidad += cantidad
                return
            nodo_actual = nodo_actual.siguiente

        nuevo_nodo = NodoProducto(nombre, cantidad, precio)
        nuevo_nodo.siguiente = self.cabeza
        self.cabeza = nuevo_nodo

    # 2. Funcion para retirar un producto de la estanteria
    # Complejidad: O(P) en el peor caso
    def retirar_producto(self, nombre, cantidad):
        nodo_actual = self.cabeza
        nodo_anterior = None

        while nodo_actual is not None:
            if nodo_actual.nombre == nombre:
                if nodo_actual.cantidad >= cantidad:
                    nodo_actual.cantidad -= cantidad
                    
                    # Desenlazar el nodo si la cantidad llega a 0
                    if nodo_actual.cantidad == 0:
                        if nodo_anterior is None:
                            self.cabeza = nodo_actual.siguiente
                        else:
                            nodo_anterior.siguiente = nodo_actual.siguiente
                    return True
                else:
                    print(f"ERROR: Stock insuficiente. Solo hay {nodo_actual.cantidad} unidades de '{nombre}'.")
                    return False
            
            nodo_anterior = nodo_actual
            nodo_actual = nodo_actual.siguiente
            
        print(f"ERROR: El producto '{nombre}' no se encuentra en {self.nombre}.")
        return False


#Segunda seccion: Estructura del almacen
# Vertice del grafo que contiene la estanteria y sus aristas (vecinos)
class NodoGrafo:
    def __init__(self, estanteria):
        self.estanteria = estanteria
        self.vecinos = [] 

# Grafo implementado como Lista de Adyacencia
class AlmacenGrafoPuro:
    def __init__(self):
        self.nodos_grafo = []

    def _buscar_nodo_por_nombre(self, nombre):
        for nodo in self.nodos_grafo:
            if nodo.estanteria.nombre == nombre:
                return nodo
        return None

    def agregar_estanteria(self, nombre):
        if self._buscar_nodo_por_nombre(nombre) is None:
            nueva_estanteria = EstanteriaEnlazada(nombre)
            nuevo_nodo = NodoGrafo(nueva_estanteria)
            self.nodos_grafo.append(nuevo_nodo)

    def conectar_pasillo(self, nombre_origen, nombre_destino):
        nodo_a = self._buscar_nodo_por_nombre(nombre_origen)
        nodo_b = self._buscar_nodo_por_nombre(nombre_destino)
        
        if nodo_a is not None and nodo_b is not None:
            nodo_a.vecinos.append(nodo_b)
            nodo_b.vecinos.append(nodo_a)

    # 3. Funcion para verificar la disponibilidad de un producto
    # Complejidad: O(V + E + N_total). Se usa BFS con Cola.
    def verificar_disponibilidad(self, nombre_producto):
        if len(self.nodos_grafo) == 0:
            print("INFO: El almacen esta vacio.")
            return

        print(f"\nBusqueda BFS: {nombre_producto}")
        
        nodo_inicial = self.nodos_grafo[0]
        cola_busqueda = deque([nodo_inicial])
        estanterias_visitadas = {nodo_inicial.estanteria.nombre}
        encontrado = False

        while len(cola_busqueda) > 0:
            nodo_actual = cola_busqueda.popleft() 
            
            producto_actual = nodo_actual.estanteria.cabeza
            while producto_actual is not None:
                if producto_actual.nombre == nombre_producto:
                    print(f"[ENCONTRADO] En {nodo_actual.estanteria.nombre}: {producto_actual.cantidad} unidades disponibles.")
                    encontrado = True
                producto_actual = producto_actual.siguiente

            # Encolar nodos vecinos no visitados
            for vecino in nodo_actual.vecinos:
                if vecino.estanteria.nombre not in estanterias_visitadas:
                    estanterias_visitadas.add(vecino.estanteria.nombre)
                    cola_busqueda.append(vecino)

        if not encontrado:
            print(f"NO DISPONIBLE: El producto '{nombre_producto}' no existe en la red del almacen.")

    # 4. Funcion para verificar el estado del almacen
    # Complejidad: Theta(V + N_total)
    def estado_del_almacen(self):
        print("\nEstado general del almacen")
        for nodo in self.nodos_grafo:
            total_productos = 0
            valor_total = 0.0
            
            producto_actual = nodo.estanteria.cabeza
            while producto_actual is not None:
                total_productos += producto_actual.cantidad
                valor_total += (producto_actual.cantidad * producto_actual.precio)
                producto_actual = producto_actual.siguiente
                
            print(f"ESTANTERIA: {nodo.estanteria.nombre}: {total_productos} unidades | Valor: {valor_total:.2f} EUR")

    # 5. Funcion para transferir productos entre estanterias
    # Complejidad: O(V + P_origen + P_destino)
    def transferir_productos(self, nombre_producto, cantidad, origen, destino):
        nodo_origen = self._buscar_nodo_por_nombre(origen)
        nodo_destino = self._buscar_nodo_por_nombre(destino)

        if nodo_origen is None or nodo_destino is None:
            print("ERROR TRANSFERENCIA: Una de las estanterias no existe.")
            return

        # Verificacion de arista en el grafo
        if nodo_destino not in nodo_origen.vecinos:
            print(f"ERROR TRANSFERENCIA: No hay conexion directa entre {origen} y {destino}.")
            return

        precio_mantenido = 0.0
        producto_actual = nodo_origen.estanteria.cabeza
        while producto_actual is not None:
            if producto_actual.nombre == nombre_producto:
                precio_mantenido = producto_actual.precio
                break
            producto_actual = producto_actual.siguiente

        # Realizar la transferencia
        if nodo_origen.estanteria.retirar_producto(nombre_producto, cantidad):
            nodo_destino.estanteria.ingresar_producto(nombre_producto, cantidad, precio_mantenido)
            print(f"TRANSFERENCIA EXITOSA: Movidas {cantidad} uds de '{nombre_producto}' de {origen} a {destino}.")

    # 6. Funcion para optimizar el inventario. BONUS
    # Complejidad: Theta(V + N_total)
    def optimizacion_inventario(self):
        max_valor = -1
        estanteria_max_valor = ""
        min_productos = float('inf')
        estanteria_min_productos = ""

        for nodo in self.nodos_grafo:
            total_productos = 0
            valor_total = 0.0
            
            producto_actual = nodo.estanteria.cabeza
            while producto_actual is not None:
                total_productos += producto_actual.cantidad
                valor_total += (producto_actual.cantidad * producto_actual.precio)
                producto_actual = producto_actual.siguiente
                
            if valor_total > max_valor:
                max_valor = valor_total
                estanteria_max_valor = nodo.estanteria.nombre
                
            if total_productos < min_productos:
                min_productos = total_productos
                estanteria_min_productos = nodo.estanteria.nombre
                
        print("\nRESULTADOS OPTIMIZACION BONUS")
        print(f"MAYOR VALOR: Estanteria: {estanteria_max_valor} (Acumulado: {max_valor:.2f} EUR)")
        print(f"MENOR CARGA: Estanteria: {estanteria_min_productos} (Stock total: {min_productos} unidades)")

#Seccion 3: Carga de datos y simulacion

def ejecutar_simulacion():
    almacen = AlmacenGrafoPuro()
    
    # Cargar los datos del archivo JSON que contiene los productos y sus datos
    try:
        with open('productos_almacen_volumen.json', 'r', encoding='utf-8') as archivo:
            datos_json = json.load(archivo)
    except FileNotFoundError:
        print("ERROR: El archivo 'productos_almacen_volumen.json' no se encuentra en la carpeta.")
        return

    for nombre_est, productos in datos_json.items():
        almacen.agregar_estanteria(nombre_est)
        nodo_est = almacen._buscar_nodo_por_nombre(nombre_est)
        
        for prod in productos:
            nodo_est.estanteria.ingresar_producto(prod["nombre"], prod["cantidad"], prod["precio"])

    almacen.conectar_pasillo("Estantería A", "Estantería B")
    almacen.conectar_pasillo("Estantería B", "Estantería C")
    almacen.conectar_pasillo("Estantería C", "Estantería D")
    almacen.verificar_disponibilidad("Chocolate Amargo Clásico")
    almacen.estado_del_almacen()
    almacen.transferir_productos("Chocolate Amargo Clásico", 10, "Estantería A", "Estantería B")
    almacen.estado_del_almacen()
    almacen.optimizacion_inventario()

if __name__ == "__main__":
    ejecutar_simulacion()
