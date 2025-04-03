# ast_nodes.py

from typing import List, Dict, Any, Optional, Tuple


class Nodo:
    pass

class Programa(Nodo):
    def __init__(self, cuerpo: List[Nodo]):
        self.cuerpo = cuerpo

class Mostrar(Nodo):
    def __init__(self, expresion):
        self.expresion = expresion  # Almacenas la expresión que debe ser mostrada

    def ejecutar(self, entorno):
        # Aquí implementas lo que se debe hacer con la expresión
        # Por ejemplo, imprimir el resultado
        print(self.expresion.ejecutar(entorno))  # Asumiendo que la expresión tiene un método ejecutar


class DeclaracionVariable(Nodo):
    def __init__(self, nombre: str, tipo: Optional[str], valor: Nodo):
        self.nombre = nombre
        self.tipo = tipo
        self.valor = valor

class AsignacionVariable(Nodo):
    def __init__(self, nombre: str, valor: Nodo):
        self.nombre = nombre
        self.valor = valor

class ValorLiteral(Nodo):
    def __init__(self, valor: Any, tipo: str):
        self.valor = valor
        self.tipo = tipo

class Identificador(Nodo):
    def __init__(self, nombre: str):
        self.nombre = nombre

class OperacionBinaria(Nodo):
    def __init__(self, izquierda: Nodo, operador: str, derecha: Nodo):
        self.izquierda = izquierda
        self.operador = operador
        self.derecha = derecha

class OperacionUnaria(Nodo):
    def __init__(self, operador: str, operando: Nodo):
        self.operador = operador
        self.operando = operando

class Condicional(Nodo):
    def __init__(self, condicion: Nodo, cuerpo: List[Nodo], sino: Optional[List[Nodo]]):
        self.condicion = condicion
        self.cuerpo = cuerpo
        self.sino = sino

class BucleWhile(Nodo):
    def __init__(self, condicion: Nodo, cuerpo: List[Nodo]):
        self.condicion = condicion
        self.cuerpo = cuerpo

class BucleFor(Nodo):
    def __init__(self, inicializacion: Nodo, condicion: Nodo, incremento: Nodo, cuerpo: List[Nodo]):
        self.inicializacion = inicializacion
        self.condicion = condicion
        self.incremento = incremento
        self.cuerpo = cuerpo

class BucleForEach(Nodo):
    def __init__(self, variable: str, iterable: Nodo, cuerpo: List[Nodo]):
        self.variable = variable
        self.iterable = iterable
        self.cuerpo = cuerpo

class DeclaracionFuncion(Nodo):
    def __init__(self, nombre: str, parametros: List[Dict[str, str]], tipo_retorno: Optional[str], cuerpo: List[Nodo]):
        self.nombre = nombre
        self.parametros = parametros
        self.tipo_retorno = tipo_retorno
        self.cuerpo = cuerpo

class LlamadaFuncion(Nodo):
    def __init__(self, nombre: str, argumentos: List[Nodo]):
        self.nombre = nombre
        self.argumentos = argumentos

class RetornoFuncion(Nodo):
    def __init__(self, valor: Optional[Nodo] = None):
        self.valor = valor

class ListaValores(Nodo):
    def __init__(self, valores: List[Nodo]):
        self.valores = valores

class Diccionario(Nodo):
    def __init__(self, pares: List[Tuple[Nodo, Nodo]]):
        self.pares = pares

class ElementoHTML(Nodo):
    def __init__(self, tipo: str, atributos: Dict[str, Nodo], contenido: List[Nodo]):
        self.tipo = tipo
        self.atributos = atributos
        self.contenido = contenido

class EstiloCSS(Nodo):
    def __init__(self, selector: str, propiedades: Dict[str, str]):
        self.selector = selector
        self.propiedades = propiedades