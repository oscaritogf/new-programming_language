# interpreter.py
from typing import Dict, Any, List, Optional, Union
import ast_nodes as ast
from parser import Parser

class Valor:
    def __init__(self, tipo: str, valor: Any):
        self.tipo = tipo
        self.valor = valor
    
    def __repr__(self):
        return f"Valor({self.tipo}, {self.valor})"

class Entorno:
    def __init__(self, padre=None):
        self.variables: Dict[str, Valor] = {}
        self.funciones: Dict[str, ast.DeclaracionFuncion] = {}
        self.padre = padre
    
    def definir_variable(self, nombre: str, valor: Valor) -> None:
        self.variables[nombre] = valor
    
    def asignar_variable(self, nombre: str, valor: Valor) -> None:
        if nombre in self.variables:
            self.variables[nombre] = valor
        elif self.padre:
            self.padre.asignar_variable(nombre, valor)
        else:
            raise NameError(f"Variable '{nombre}' no definida")
    
    def obtener_variable(self, nombre: str) -> Valor:
        if nombre in self.variables:
            return self.variables[nombre]
        elif self.padre:
            return self.padre.obtener_variable(nombre)
        else:
            raise NameError(f"Variable '{nombre}' no definida")
    
    def definir_funcion(self, nombre: str, funcion: ast.DeclaracionFuncion) -> None:
        self.funciones[nombre] = funcion
    
    def obtener_funcion(self, nombre: str) -> ast.DeclaracionFuncion:
        if nombre in self.funciones:
            return self.funciones[nombre]
        elif self.padre:
            return self.padre.obtener_funcion(nombre)
        else:
            raise NameError(f"Función '{nombre}' no definida")

class RetornoExcepcion(Exception):
    def __init__(self, valor: Optional[Valor] = None):
        self.valor = valor
        super().__init__(self)

class Interprete:
    def __init__(self):
        self.entorno_global = Entorno()
        self.inicializar_entorno_global()
    
    def inicializar_entorno_global(self) -> None:
        # Funciones nativas
        # Ejemplos: mostrar, alerta, etc.
        pass
    
    def evaluar(self, nodo: ast.Nodo, entorno: Entorno) -> Valor:
        # Programa
        if isinstance(nodo, ast.Programa):
            resultado = None
            for statement in nodo.cuerpo:
                resultado = self.evaluar(statement, entorno)
            return resultado or Valor('nulo', None)
        
        # Declaración de variable
        elif isinstance(nodo, ast.DeclaracionVariable):
            valor = self.evaluar(nodo.valor, entorno)
            
            # Verificar tipo si se especificó
            if nodo.tipo and nodo.tipo != valor.tipo:
                raise TypeError(f"Se esperaba tipo '{nodo.tipo}' pero se obtuvo '{valor.tipo}'")
            
            entorno.definir_variable(nodo.nombre, valor)
            return valor
        
        # Asignación de variable
        elif isinstance(nodo, ast.AsignacionVariable):
            valor = self.evaluar(nodo.valor, entorno)
            entorno.asignar_variable(nodo.nombre, valor)
            return valor
        
        # Valor literal
        elif isinstance(nodo, ast.ValorLiteral):
            return Valor(nodo.tipo, nodo.valor)
        
        # Identificador
        elif isinstance(nodo, ast.Identificador):
            return entorno.obtener_variable(nodo.nombre)
        
        # Operación binaria
        elif isinstance(nodo, ast.OperacionBinaria):
            izquierda = self.evaluar(nodo.izquierda, entorno)
            derecha = self.evaluar(nodo.derecha, entorno)
            
            # Lógica para operaciones basadas en el operador y tipos
            if nodo.operador == 'MAS':
                if izquierda.tipo in ['entero', 'decimal'] and derecha.tipo in ['entero', 'decimal']:
                    resultado = izquierda.valor + derecha.valor
                    tipo = 'decimal' if 'decimal' in [izquierda.tipo, derecha.tipo] else 'entero'
                    return Valor(tipo, resultado)
                elif izquierda.tipo == 'cadena' or derecha.tipo == 'cadena':
                    # Concatenación
                    return Valor('cadena', str(izquierda.valor) + str(derecha.valor))
                else:
                    raise TypeError(f"Operación no soportada entre '{izquierda.tipo}' y '{derecha.tipo}'")
            
            # Implementar el resto de operadores...
            
        # Operación unaria
        elif isinstance(nodo, ast.OperacionUnaria):
            operando = self.evaluar(nodo.operando, entorno)
            
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
        
        # Condicional
        elif isinstance(nodo, ast.Condicional):
            condicion = self.evaluar(nodo.condicion, entorno)
            
            if condicion.tipo != 'booleano':
                raise TypeError(f"La condición debe ser de tipo 'booleano', se obtuvo '{condicion.tipo}'")
            
            if condicion.valor:
                # Ejecutar bloque 'si'
                resultado = None
                for statement in nodo.cuerpo:
                    try:
                        resultado = self.evaluar(statement, entorno)
                    except RetornoExcepcion as r:
                        raise r
                return resultado or Valor('nulo', None)
            elif nodo.sino:
                # Ejecutar bloque 'sino'
                resultado = None
                for statement in nodo.sino:
                    try:
                        resultado = self.evaluar(statement, entorno)
                    except RetornoExcepcion as r:
                        raise r
                return resultado or Valor('nulo', None)
            else:
                return Valor('nulo', None)
        
        # Bucle while
        elif isinstance(nodo, ast.BucleWhile):
            resultado = Valor('nulo', None)
            
            while True:
                condicion = self.evaluar(nodo.condicion, entorno)
                
                if condicion.tipo != 'booleano':
                    raise TypeError(f"La condición debe ser de tipo 'booleano', se obtuvo '{condicion.tipo}'")
                
                if not condicion.valor:
                    break
                
                for statement in nodo.cuerpo:
                    try:
                        resultado = self.evaluar(statement, entorno)
                    except RetornoExcepcion as r:
                        raise r
            
            return resultado
        
        # Bucle for
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
        
        # Bucle foreach
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
        
        # Declaración de función
        elif isinstance(nodo, ast.DeclaracionFuncion):
            entorno.definir_funcion(nodo.nombre, nodo)
            return Valor('funcion', nodo.nombre)
        
        # Llamada a función
        elif isinstance(nodo, ast.LlamadaFuncion):
            funcion = entorno.obtener_funcion(nodo.nombre)
            
            # Verificar número de argumentos
            if len(nodo.argumentos) != len(funcion.parametros):
                raise TypeError(f"Función '{nodo.nombre}' espera {len(funcion.parametros)} argumentos, pero se proporcionaron {len(nodo.argumentos)}")
            
            # Evaluar argumentos
            valores_args = []
            for arg in nodo.argumentos:
                valores_args.append(self.evaluar(arg, entorno))
            
            # Crear nuevo entorno para la función
            entorno_funcion = Entorno(entorno)
            
            # Asociar argumentos con parámetros
            for i, param in enumerate(funcion.parametros):
                # Verificar tipo si se especificó
                if param['tipo'] and param['tipo'] != valores_args[i].tipo:
                    raise TypeError(f"Parámetro '{param['nombre']}' espera tipo '{param['tipo']}', pero se proporcionó '{valores_args[i].tipo}'")
                
                entorno_funcion.definir_variable(param['nombre'], valores_args[i])
            
            # Ejecutar cuerpo de la función
            resultado = Valor('nulo', None)
            try:
                for statement in funcion.cuerpo:
                    resultado = self.evaluar(statement, entorno_funcion)
            except RetornoExcepcion as r:
                return r.valor or Valor('nulo', None)
            
            # Verificar tipo de retorno si se especificó
            if funcion.tipo_retorno and resultado.tipo != funcion.tipo_retorno:
                raise TypeError(f"Función '{nodo.nombre}' debe retornar tipo '{funcion.tipo_retorno}', pero retornó '{resultado.tipo}'")
            
            return resultado
        
        # Retorno de función
        elif isinstance(nodo, ast.RetornoFuncion):
            valor = Valor('nulo', None) if nodo.valor is None else self.evaluar(nodo.valor, entorno)
            raise RetornoExcepcion(valor)
        
        # Lista de valores
        elif isinstance(nodo, ast.ListaValores):
            valores = []
            for expr in nodo.valores:
                valores.append(self.evaluar(expr, entorno))
            return Valor('lista', valores)
        
        # Diccionario
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
        
        # Elemento HTML
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
        
        # Estilo CSS
        elif isinstance(nodo, ast.EstiloCSS):
            # Construir CSS (simplificado)
            return Valor('css', {
                'selector': nodo.selector,
                'propiedades': nodo.propiedades
            })
        
        else:
            raise NotImplementedError(f"Tipo de nodo no implementado: {type(nodo).__name__}")
    
    def ejecutar(self, codigo: str) -> Any:
        from lexer import Lexer
        
        lexer = Lexer()
        tokens = lexer.tokenizar(codigo)
        
        parser = Parser(tokens)
        ast = parser.analizar()
        
        return self.evaluar(ast, self.entorno_global)
    