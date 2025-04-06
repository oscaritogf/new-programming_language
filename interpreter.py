# interpreter.py
# Este archivo contiene la implementación del intérprete, que toma un árbol sintáctico abstracto (AST)
# generado por el analizador sintáctico (Parser) y lo ejecuta, evaluando las expresiones y declaraciones.

from typing import Dict, Any, List, Optional, Union  # Importaciones para anotaciones de tipos
import ast_nodes as ast  # Importar los nodos del árbol sintáctico desde ast_nodes
from parser import Parser  # Importar el analizador sintáctico

# Clase para representar un valor en el intérprete
class Valor:
    def __init__(self, tipo: str, valor: Any):
        self.tipo = tipo  # Tipo del valor (entero, decimal, cadena, etc.)
        self.valor = valor  # Valor en sí
    
    def __repr__(self):
        return f"Valor({self.tipo}, {self.valor})"  # Representación legible del valor

# Clase para manejar el entorno de ejecución (variables, funciones, etc.)
class Entorno:
    def __init__(self, padre=None):
        self.variables: Dict[str, Valor] = {}  # Diccionario de variables definidas en este entorno
        self.funciones: Dict[str, ast.DeclaracionFuncion] = {}  # Diccionario de funciones definidas
        self.padre = padre  # Referencia al entorno padre (para manejar entornos anidados)
    
    # Definir una nueva variable en el entorno
    def definir_variable(self, nombre: str, valor: Valor) -> None:
        self.variables[nombre] = valor  # Agregar la variable al diccionario
    
    # Asignar un valor a una variable existente
    def asignar_variable(self, nombre: str, valor: Valor) -> None:
        if nombre in self.variables:  # Si la variable está definida en este entorno
            self.variables[nombre] = valor
        elif self.padre:  # Si no está en este entorno, buscar en el entorno padre
            self.padre.asignar_variable(nombre, valor)
        else:  # Si no se encuentra, lanzar un error
            raise NameError(f"Variable '{nombre}' no definida")
    
    # Obtener el valor de una variable
    def obtener_variable(self, nombre: str) -> Valor:
        if nombre in self.variables:  # Si la variable está definida en este entorno
            return self.variables[nombre]
        elif self.padre:  # Si no está en este entorno, buscar en el entorno padre
            return self.padre.obtener_variable(nombre)
        else:  # Si no se encuentra, lanzar un error
            raise NameError(f"Variable '{nombre}' no definida")
    
    # Definir una nueva función en el entorno
    def definir_funcion(self, nombre: str, funcion: ast.DeclaracionFuncion) -> None:
        self.funciones[nombre] = funcion  # Agregar la función al diccionario
    
    # Obtener una función definida en el entorno
    def obtener_funcion(self, nombre: str) -> ast.DeclaracionFuncion:
        if nombre in self.funciones:  # Si la función está definida en este entorno
            return self.funciones[nombre]
        elif self.padre:  # Si no está en este entorno, buscar en el entorno padre
            return self.padre.obtener_funcion(nombre)
        else:  # Si no se encuentra, lanzar un error
            raise NameError(f"Función '{nombre}' no definida")

# Clase para manejar excepciones de retorno en funciones
class RetornoExcepcion(Exception):
    def __init__(self, valor: Optional[Valor] = None):
        self.valor = valor  # Valor retornado por la función
        super().__init__(self)

# Clase principal del intérprete
class Interprete:
    def __init__(self):
        self.entorno_global = Entorno()  # Crear el entorno global
        self.inicializar_entorno_global()  # Inicializar funciones nativas
    
    # Inicializar funciones nativas en el entorno global
    def inicializar_entorno_global(self) -> None:
        # Aquí se pueden definir funciones nativas como "mostrar", "alerta", etc.
        pass
    
    # Método para evaluar un nodo del AST
    def evaluar(self, nodo: ast.Nodo, entorno: Entorno) -> Valor:
        # Evaluar un programa completo
        if isinstance(nodo, ast.Programa):
            resultado = None
            for statement in nodo.cuerpo:  # Evaluar cada declaración en el cuerpo del programa
                resultado = self.evaluar(statement, entorno)
            return resultado or Valor('nulo', None)  # Retornar el último resultado o nulo
        
        # Evaluar una declaración de variable
        elif isinstance(nodo, ast.DeclaracionVariable):
            valor = self.evaluar(nodo.valor, entorno)  # Evaluar el valor asignado
            
            # Verificar el tipo si se especificó
            if nodo.tipo and nodo.tipo != valor.tipo:
                raise TypeError(f"Se esperaba tipo '{nodo.tipo}' pero se obtuvo '{valor.tipo}'")
            
            entorno.definir_variable(nodo.nombre, valor)  # Definir la variable en el entorno
            return valor
        
        # Evaluar una asignación de variable
        elif isinstance(nodo, ast.AsignacionVariable):
            valor = self.evaluar(nodo.valor, entorno)  # Evaluar el valor asignado
            entorno.asignar_variable(nodo.nombre, valor)  # Asignar el valor a la variable
            return valor
        
        # Evaluar un valor literal
        elif isinstance(nodo, ast.ValorLiteral):
            return Valor(nodo.tipo, nodo.valor)  # Retornar el valor literal
        
        # Evaluar un identificador (variable)
        elif isinstance(nodo, ast.Identificador):
            return entorno.obtener_variable(nodo.nombre)  # Obtener el valor de la variable
        
        # Evaluar una operación binaria
        elif isinstance(nodo, ast.OperacionBinaria):
            izquierda = self.evaluar(nodo.izquierda, entorno)  # Evaluar el operando izquierdo
            derecha = self.evaluar(nodo.derecha, entorno)  # Evaluar el operando derecho
            
            # Realizar la operación según el operador
            if nodo.operador == 'MAS':
                if izquierda.tipo in ['entero', 'decimal'] and derecha.tipo in ['entero', 'decimal']:
                    resultado = izquierda.valor + derecha.valor
                    tipo = 'decimal' if 'decimal' in [izquierda.tipo, derecha.tipo] else 'entero'
                    return Valor(tipo, resultado)
                elif izquierda.tipo == 'cadena' or derecha.tipo == 'cadena':
                    return Valor('cadena', str(izquierda.valor) + str(derecha.valor))  # Concatenación
                else:
                    raise TypeError(f"Operación no soportada entre '{izquierda.tipo}' y '{derecha.tipo}'")
            
            # Otros operadores (MENOS, MULTIPLICACION, DIVISION, etc.)
            elif nodo.operador == 'MENOS':
                if izquierda.tipo in ['entero', 'decimal'] and derecha.tipo in ['entero', 'decimal']:
                    resultado = izquierda.valor - derecha.valor
                    tipo = 'decimal' if 'decimal' in [izquierda.tipo, derecha.tipo] else 'entero'
                    return Valor(tipo, resultado)
                else:
                    raise TypeError(f"Operación no soportada entre '{izquierda.tipo}' y '{derecha.tipo}'")
            
            elif nodo.operador == 'MULTIPLICACION':
                if izquierda.tipo in ['entero', 'decimal'] and derecha.tipo in ['entero', 'decimal']:
                    resultado = izquierda.valor * derecha.valor
                    tipo = 'decimal' if 'decimal' in [izquierda.tipo, derecha.tipo] else 'entero'
                    return Valor(tipo, resultado)
                else:
                    raise TypeError(f"Operación no soportada entre '{izquierda.tipo}' y '{derecha.tipo}'")
            
            elif nodo.operador == 'DIVISION':
                if izquierda.tipo in ['entero', 'decimal'] and derecha.tipo in ['entero', 'decimal']:
                    if derecha.valor == 0:
                        raise ZeroDivisionError("División por cero")
                    resultado = izquierda.valor / derecha.valor
                    return Valor('decimal', resultado)
                else:
                    raise TypeError(f"Operación no soportada entre '{izquierda.tipo}' y '{derecha.tipo}'")
            
            else:
                raise NotImplementedError(f"Operador '{nodo.operador}' no implementado")
        
        # Evaluar una operación unaria
        elif isinstance(nodo, ast.OperacionUnaria):
            operando = self.evaluar(nodo.operando, entorno)  # Evaluar el operando
            
            if nodo.operador == 'MENOS':
                if operando.tipo in ['entero', 'decimal']:
                    return Valor(operando.tipo, -operando.valor)
                else:
                    raise TypeError(f"Operador '-' no aplicable a tipo '{operando.tipo}'")
            elif nodo.operador == 'NO':
                if operando.tipo == 'booleano':
                    return Valor('booleano', not operando.valor)
                else:
                    raise TypeError(f"Operador 'no' no aplicable a tipo '{operando.tipo}'")
        
        # Evaluar un condicional (if-else)
        elif isinstance(nodo, ast.Condicional):
            condicion = self.evaluar(nodo.condicion, entorno)  # Evaluar la condición
            
            if condicion.tipo != 'booleano':
                raise TypeError(f"La condición debe ser de tipo 'booleano', se obtuvo '{condicion.tipo}'")
            
            if condicion.valor:  # Si la condición es verdadera
                for statement in nodo.cuerpo:
                    self.evaluar(statement, entorno)
            elif nodo.sino:  # Si hay un bloque else
                for statement in nodo.sino:
                    self.evaluar(statement, entorno)
            return Valor('nulo', None)
        
        # Evaluar un bucle while
        elif isinstance(nodo, ast.BucleWhile):
            while True:
                condicion = self.evaluar(nodo.condicion, entorno)  # Evaluar la condición
                
                if condicion.tipo != 'booleano':
                    raise TypeError(f"La condición debe ser de tipo 'booleano', se obtuvo '{condicion.tipo}'")
                
                if not condicion.valor:  # Si la condición es falsa, salir del bucle
                    break
                
                for statement in nodo.cuerpo:  # Ejecutar el cuerpo del bucle
                    self.evaluar(statement, entorno)
            return Valor('nulo', None)
        
        # Evaluar un bucle for
        elif isinstance(nodo, ast.BucleFor):
            # Inicialización
            self.evaluar(nodo.inicializacion, entorno)
            resultado = Valor('nulo', None)
            
            while True:
                # Condición
                condicion = self.evaluar(nodo.condicion, entorno)
                
                if condicion.tipo != 'booleano':
                    raise TypeError(f"La condición debe ser de tipo 'booleano', se obtuvo '{condicion.tipo}'")
                
                if not condicion.valor:
                    break
                
                # Cuerpo
                for statement in nodo.cuerpo:
                    try:
                        resultado = self.evaluar(statement, entorno)
                    except RetornoExcepcion as r:
                        raise r
                
                # Incremento
                self.evaluar(nodo.incremento, entorno)
            
            return resultado
        
        # Evaluar un bucle foreach
        elif isinstance(nodo, ast.BucleForEach):
            iterable = self.evaluar(nodo.iterable, entorno)
            resultado = Valor('nulo', None)
            
            # Verificar que sea un tipo iterable
            if iterable.tipo not in ['lista', 'cadena', 'diccionario']:
                raise TypeError(f"Tipo '{iterable.tipo}' no es iterable")
            
            iter_values = iterable.valor
            if iterable.tipo == 'diccionario':
                iter_values = iter_values.keys()
            
            for valor in iter_values:
                # Crear nuevo entorno para cada iteración
                entorno_bucle = Entorno(entorno)
                
                # Definir variable de iteración
                if iterable.tipo == 'lista':
                    entorno_bucle.definir_variable(nodo.variable, valor)
                elif iterable.tipo == 'cadena':
                    entorno_bucle.definir_variable(nodo.variable, Valor('cadena', valor))
                elif iterable.tipo == 'diccionario':
                    entorno_bucle.definir_variable(nodo.variable, Valor('cadena', valor))
                
                # Ejecutar cuerpo
                for statement in nodo.cuerpo:
                    try:
                        resultado = self.evaluar(statement, entorno_bucle)
                    except RetornoExcepcion as r:
                        raise r
            
            return resultado
        
        # Evaluar una declaración de función
        elif isinstance(nodo, ast.DeclaracionFuncion):
            entorno.definir_funcion(nodo.nombre, nodo)
            return Valor('funcion', nodo.nombre)
        
        # Evaluar una llamada a función
        elif isinstance(nodo, ast.LlamadaFuncion):
            funcion = entorno.obtener_funcion(nodo.nombre)  # Obtener la función del entorno
            
            # Verificar el número de argumentos
            if len(nodo.argumentos) != len(funcion.parametros):
                raise TypeError(f"Función '{nodo.nombre}' espera {len(funcion.parametros)} argumentos, pero se proporcionaron {len(nodo.argumentos)}")
            
            # Evaluar los argumentos
            valores_args = [self.evaluar(arg, entorno) for arg in nodo.argumentos]
            
            # Crear un nuevo entorno para la función
            entorno_funcion = Entorno(entorno)
            
            # Asociar los argumentos con los parámetros
            for i, param in enumerate(funcion.parametros):
                entorno_funcion.definir_variable(param['nombre'], valores_args[i])
            
            # Ejecutar el cuerpo de la función
            for statement in funcion.cuerpo:
                self.evaluar(statement, entorno_funcion)
            return Valor('nulo', None)
        
        # Evaluar una instrucción "mostrar"
        elif isinstance(nodo, ast.Mostrar):
            valor = self.evaluar(nodo.expresion, entorno)  # Evaluar la expresión
            print(valor.valor)  # Imprimir el valor en la consola
            return Valor('nulo', None)
        
        # Evaluar un retorno de función
        elif isinstance(nodo, ast.RetornoFuncion):
            valor = Valor('nulo', None) if nodo.valor is None else self.evaluar(nodo.valor, entorno)
            raise RetornoExcepcion(valor)
        
        # Evaluar una lista de valores
        elif isinstance(nodo, ast.ListaValores):
            valores = []
            for expr in nodo.valores:
                valores.append(self.evaluar(expr, entorno))
            return Valor('lista', valores)
        
        # Evaluar un diccionario
        elif isinstance(nodo, ast.Diccionario):
            diccionario = {}
            for clave, valor in nodo.pares:
                clave_eval = self.evaluar(clave, entorno)
                valor_eval = self.evaluar(valor, entorno)
                
                # Verificar que la clave sea inmutable
                if clave_eval.tipo not in ['entero', 'decimal', 'cadena', 'booleano']:
                    raise TypeError(f"La clave del diccionario debe ser inmutable, no '{clave_eval.tipo}'")
                
                diccionario[clave_eval.valor] = valor_eval
            
            return Valor('diccionario', diccionario)
        
        # Evaluar un elemento HTML
        elif isinstance(nodo, ast.ElementoHTML):
            # Evaluar atributos
            atributos_eval = {}
            for nombre, valor in nodo.atributos.items():
                atributos_eval[nombre] = self.evaluar(valor, entorno)
            
            # Evaluar contenido
            contenido_eval = []
            for item in nodo.contenido:
                contenido_eval.append(self.evaluar(item, entorno))
            
            # Construir HTML (simplificado)
            return Valor('html', {
                'tipo': nodo.tipo,
                'atributos': atributos_eval,
                'contenido': contenido_eval
            })
        
        # Evaluar un estilo CSS
        elif isinstance(nodo, ast.EstiloCSS):
            # Construir CSS (simplificado)
            return Valor('css', {
                'selector': nodo.selector,
                'propiedades': nodo.propiedades
            })
        
        else:
            raise NotImplementedError(f"Tipo de nodo no implementado: {type(nodo).__name__}")
    
    # Método para ejecutar el código fuente
    def ejecutar(self, codigo: str) -> Any:
        from lexer import Lexer  # Importar el analizador léxico
        
        lexer = Lexer()  # Crear una instancia del lexer
        tokens = lexer.tokenizar(codigo)  # Tokenizar el código fuente
        
        parser = Parser(tokens)  # Crear una instancia del parser
        ast = parser.analizar()  # Analizar los tokens y generar el AST
        
        return self.evaluar(ast, self.entorno_global)  # Evaluar el AST en el entorno global
