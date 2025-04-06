# parser.py
# Este archivo contiene la implementación del analizador sintáctico (Parser),
# que toma una lista de tokens generados por el analizador léxico (Lexer)
# y construye un árbol sintáctico abstracto (AST).

from typing import List  # Importaciones para anotaciones de tipos
from lexer import Token  # Importar la clase Token del analizador léxico
import ast_nodes as ast  # Importar los nodos del árbol sintáctico desde ast_nodes

# Clase principal del analizador sintáctico
class Parser:
    # Constructor de la clase Parser
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens  # Lista de tokens generados por el lexer
        self.posicion_actual = 0  # Posición actual en la lista de tokens
        self.token_actual = self.tokens[0]  # Token actual que se está procesando

    # Método para avanzar al siguiente token
    def avanzar(self) -> None:
        self.posicion_actual += 1  # Incrementar la posición actual
        if self.posicion_actual < len(self.tokens):  # Si no se ha llegado al final
            self.token_actual = self.tokens[self.posicion_actual]  # Actualizar el token actual
        else:
            self.token_actual = None  # Si se llega al final, no hay más tokens

    # Método para verificar si el token actual coincide con un tipo específico
    def coincidir(self, tipo: str) -> bool:
        if self.token_actual and self.token_actual.tipo == tipo:  # Si el tipo coincide
            self.avanzar()  # Avanzar al siguiente token
            return True
        return False  # Si no coincide, devolver False

    # Método para esperar un token específico y avanzar, o lanzar un error si no coincide
    def esperar(self, tipo: str) -> Token:
        if self.token_actual and self.token_actual.tipo == tipo:  # Si el tipo coincide
            token = self.token_actual  # Guardar el token actual
            self.avanzar()  # Avanzar al siguiente token
            return token  # Devolver el token consumido
        # Lanzar un error si el token no coincide
        raise SyntaxError(
            f"Se esperaba '{tipo}' pero se encontró '{self.token_actual.tipo}' en línea {self.token_actual.linea}, columna {self.token_actual.columna}"
        )

    # Método principal para analizar el programa completo
    def analizar(self) -> ast.Programa:
        nodos = []  # Lista de nodos del programa
        while self.token_actual and self.token_actual.tipo != 'EOF':  # Mientras no se llegue al final
            nodos.append(self.analizar_declaracion())  # Analizar cada declaración
        return ast.Programa(nodos)  # Retornar el nodo raíz del programa

    # Método para analizar una declaración (como variables, condicionales, bucles, etc.)
    def analizar_declaracion(self) -> ast.Nodo:
        if self.coincidir('VARIABLE'):  # Si es una declaración de variable
            return self.analizar_declaracion_variable()
        elif self.coincidir('SI'):  # Si es un condicional
            return self.analizar_condicional()
        elif self.coincidir('MIENTRAS'):  # Si es un bucle while
            return self.analizar_bucle_while()
        elif self.coincidir('PARA'):  # Si es un bucle for
            if self.coincidir('CADA'):  # Si es un bucle foreach
                return self.analizar_bucle_foreach()
            return self.analizar_bucle_for()
        elif self.coincidir('FUNCION'):  # Si es una declaración de función
            return self.analizar_declaracion_funcion()
        elif self.coincidir('DEVOLVER'):  # Si es una instrucción de retorno
            return self.analizar_retorno()
        else:
            self.coincidir('PUNTO_COMA')  # Consumir punto y coma si está presente
            return self.analizar_expresion()  # Analizar una expresión

    # Método para analizar una declaración de variable
    def analizar_declaracion_variable(self) -> ast.DeclaracionVariable:
        nombre = self.esperar('IDENTIFICADOR').valor  # Obtener el nombre de la variable
        tipo = None  # Tipo de la variable (opcional)

        if self.coincidir('DOS_PUNTOS'):  # Si se especifica un tipo
            tipo = self.esperar('IDENTIFICADOR').valor  # Obtener el tipo

        self.esperar('IGUAL')  # Esperar el operador de asignación
        valor = self.analizar_expresion()  # Analizar la expresión asignada

        self.coincidir('PUNTO_COMA')  # Consumir el punto y coma al final

        return ast.DeclaracionVariable(nombre, tipo, valor)  # Retornar el nodo de la declaración

    # Método para analizar un condicional (if-else)
    def analizar_condicional(self) -> ast.Condicional:
        self.esperar('PARENTESIS_IZQ')  # Esperar el paréntesis de apertura
        condicion = self.analizar_expresion()  # Analizar la condición
        self.esperar('PARENTESIS_DER')  # Esperar el paréntesis de cierre

        self.esperar('LLAVE_IZQ')  # Esperar la llave de apertura
        cuerpo = []  # Lista de declaraciones dentro del cuerpo
        while self.token_actual and self.token_actual.tipo != 'LLAVE_DER':  # Mientras no se cierre el bloque
            cuerpo.append(self.analizar_declaracion())  # Analizar cada declaración
        self.esperar('LLAVE_DER')  # Esperar la llave de cierre

        sino = None  # Bloque else (opcional)
        if self.coincidir('SINO'):  # Si hay un bloque else
            if self.coincidir('SI'):  # Si es un "else if"
                return ast.Condicional(condicion, cuerpo, [self.analizar_condicional()])
            else:  # Si es un "else"
                self.esperar('LLAVE_IZQ')  # Esperar la llave de apertura
                sino = []  # Lista de declaraciones dentro del bloque else
                while self.token_actual and self.token_actual.tipo != 'LLAVE_DER':  # Mientras no se cierre el bloque
                    sino.append(self.analizar_declaracion())  # Analizar cada declaración
                self.esperar('LLAVE_DER')  # Esperar la llave de cierre

        return ast.Condicional(condicion, cuerpo, sino)  # Retornar el nodo del condicional

    # Método para analizar un bucle while
    def analizar_bucle_while(self) -> ast.BucleWhile:
        self.esperar('PARENTESIS_IZQ')  # Esperar el paréntesis de apertura
        condicion = self.analizar_expresion()  # Analizar la condición
        self.esperar('PARENTESIS_DER')  # Esperar el paréntesis de cierre

        self.esperar('LLAVE_IZQ')  # Esperar la llave de apertura
        cuerpo = []  # Lista de declaraciones dentro del cuerpo
        while self.token_actual and self.token_actual.tipo != 'LLAVE_DER':  # Mientras no se cierre el bloque
            cuerpo.append(self.analizar_declaracion())  # Analizar cada declaración
        self.esperar('LLAVE_DER')  # Esperar la llave de cierre

        return ast.BucleWhile(condicion, cuerpo)  # Retornar el nodo del bucle while

    # Método para analizar un bucle for
    def analizar_bucle_for(self) -> ast.BucleFor:
        self.esperar('PARENTESIS_IZQ')  # Esperar el paréntesis de apertura
        inicializacion = self.analizar_declaracion()  # Analizar la inicialización
        self.esperar('PUNTO_COMA')  # Esperar el punto y coma
        condicion = self.analizar_expresion()  # Analizar la condición
        self.esperar('PUNTO_COMA')  # Esperar el punto y coma
        incremento = self.analizar_expresion()  # Analizar el incremento
        self.esperar('PARENTESIS_DER')  # Esperar el paréntesis de cierre

        self.esperar('LLAVE_IZQ')  # Esperar la llave de apertura
        cuerpo = []  # Lista de declaraciones dentro del cuerpo
        while self.token_actual and self.token_actual.tipo != 'LLAVE_DER':  # Mientras no se cierre el bloque
            cuerpo.append(self.analizar_declaracion())  # Analizar cada declaración
        self.esperar('LLAVE_DER')  # Esperar la llave de cierre

        return ast.BucleFor(inicializacion, condicion, incremento, cuerpo)  # Retornar el nodo del bucle for

    # Método para analizar un bucle foreach
    def analizar_bucle_foreach(self) -> ast.BucleForEach:
        variable = self.esperar('IDENTIFICADOR').valor  # Obtener el nombre de la variable
        self.esperar('EN')  # Esperar la palabra clave "en"
        iterable = self.analizar_expresion()  # Analizar la expresión iterable

        self.esperar('LLAVE_IZQ')  # Esperar la llave de apertura
        cuerpo = []  # Lista de declaraciones dentro del cuerpo
        while self.token_actual and self.token_actual.tipo != 'LLAVE_DER':  # Mientras no se cierre el bloque
            cuerpo.append(self.analizar_declaracion())  # Analizar cada declaración
        self.esperar('LLAVE_DER')  # Esperar la llave de cierre

        return ast.BucleForEach(variable, iterable, cuerpo)  # Retornar el nodo del bucle foreach

    # Método para analizar una declaración de función
    def analizar_declaracion_funcion(self) -> ast.DeclaracionFuncion:
        nombre = self.esperar('IDENTIFICADOR').valor  # Obtener el nombre de la función

        self.esperar('PARENTESIS_IZQ')  # Esperar el paréntesis de apertura
        parametros = []  # Lista de parámetros

        if self.token_actual and self.token_actual.tipo != 'PARENTESIS_DER':  # Si hay parámetros
            # Primer parámetro
            param_nombre = self.esperar('IDENTIFICADOR').valor  # Obtener el nombre del parámetro
            param_tipo = None  # Tipo del parámetro (opcional)
            if self.coincidir('DOS_PUNTOS'):  # Si se especifica un tipo
                param_tipo = self.esperar('IDENTIFICADOR').valor  # Obtener el tipo
            parametros.append({'nombre': param_nombre, 'tipo': param_tipo})  # Agregar el parámetro a la lista

            # Más parámetros
            while self.coincidir('COMA'):  # Mientras haya más parámetros separados por comas
                param_nombre = self.esperar('IDENTIFICADOR').valor  # Obtener el nombre del parámetro
                param_tipo = None  # Tipo del parámetro (opcional)
                if self.coincidir('DOS_PUNTOS'):  # Si se especifica un tipo
                    param_tipo = self.esperar('IDENTIFICADOR').valor  # Obtener el tipo
                parametros.append({'nombre': param_nombre, 'tipo': param_tipo})  # Agregar el parámetro a la lista

        self.esperar('PARENTESIS_DER')  # Esperar el paréntesis de cierre

        tipo_retorno = None  # Tipo de retorno de la función (opcional)
        if self.coincidir('DOS_PUNTOS'):  # Si se especifica un tipo de retorno
            tipo_retorno = self.esperar('IDENTIFICADOR').valor  # Obtener el tipo de retorno

        self.esperar('LLAVE_IZQ')  # Esperar la llave de apertura
        cuerpo = []  # Lista de declaraciones dentro del cuerpo
        while self.token_actual and self.token_actual.tipo != 'LLAVE_DER':  # Mientras no se cierre el bloque
            cuerpo.append(self.analizar_declaracion())  # Analizar cada declaración
        self.esperar('LLAVE_DER')  # Esperar la llave de cierre

        return ast.DeclaracionFuncion(nombre, parametros, tipo_retorno, cuerpo)  # Retornar el nodo de la declaración de función

    # Método para analizar una instrucción de retorno
    def analizar_retorno(self) -> ast.RetornoFuncion:
        valor = None  # Valor de retorno (opcional)
        if self.token_actual and self.token_actual.tipo != 'PUNTO_COMA':  # Si hay un valor de retorno
            valor = self.analizar_expresion()  # Analizar la expresión de retorno
        return ast.RetornoFuncion(valor)  # Retornar el nodo de la instrucción de retorno

    # falta implementar métodos para analizar expresiones (factor, término, etc.)
    # Estos métodos dependen de la precedencia de los operadores

    # Método para analizar una expresión
    def analizar_expresion(self) -> ast.Nodo:
        # Simplificado para este ejemplo
        return self.analizar_comparacion()

    # Método para analizar una comparación
    def analizar_comparacion(self) -> ast.Nodo:
        expr = self.analizar_suma()  # Analizar la suma

        while self.token_actual and self.token_actual.tipo in ['IGUAL_IGUAL', 'DIFERENTE', 'MAYOR', 'MENOR', 'MAYOR_IGUAL', 'MENOR_IGUAL']:
            operador = self.token_actual.tipo  # Obtener el operador de comparación
            self.avanzar()  # Avanzar al siguiente token
            derecha = self.analizar_suma()  # Analizar la suma a la derecha del operador
            expr = ast.OperacionBinaria(expr, operador, derecha)  # Crear un nodo de operación binaria

        return expr  # Retornar la expresión

    # Método para analizar una suma
    def analizar_suma(self) -> ast.Nodo:
        expr = self.analizar_termino()  # Analizar el término

        while self.token_actual and self.token_actual.tipo in ['MAS', 'MENOS']:
            operador = self.token_actual.tipo  # Obtener el operador de suma/resta
            self.avanzar()  # Avanzar al siguiente token
            derecha = self.analizar_termino()  # Analizar el término a la derecha del operador
            expr = ast.OperacionBinaria(expr, operador, derecha)  # Crear un nodo de operación binaria

        return expr  # Retornar la expresión

    # Método para analizar un término
    def analizar_termino(self) -> ast.Nodo:
        expr = self.analizar_factor()  # Analizar el factor

        while self.token_actual and self.token_actual.tipo in ['MULTIPLICACION', 'DIVISION', 'MODULO']:
            operador = self.token_actual.tipo  # Obtener el operador de multiplicación/división/módulo
            self.avanzar()  # Avanzar al siguiente token
            derecha = self.analizar_factor()  # Analizar el factor a la derecha del operador
            expr = ast.OperacionBinaria(expr, operador, derecha)  # Crear un nodo de operación binaria

        return expr  # Retornar la expresión

    # Método para analizar un factor
    def analizar_factor(self) -> ast.Nodo:
        print(f"Token actual: {self.token_actual.tipo}, Token siguiente: {self.tokens[self.posicion_actual + 1].tipo}")

        if self.coincidir('PARENTESIS_IZQ'):
            expr = self.analizar_expresion()
            self.esperar('PARENTESIS_DER')
            return expr
        elif self.coincidir('MENOS'):
            return ast.OperacionUnaria('MENOS', self.analizar_factor())
        elif self.coincidir('NO'):
            return ast.OperacionUnaria('NO', self.analizar_factor())
        elif self.token_actual.tipo == 'ENTERO':
            valor = int(self.token_actual.valor)
            self.avanzar()
            return ast.ValorLiteral(valor, 'entero')
        elif self.token_actual.tipo == 'DECIMAL':
            valor = float(self.token_actual.valor)
            self.avanzar()
            return ast.ValorLiteral(valor, 'decimal')
        elif self.token_actual.tipo == 'CADENA':
            valor = self.token_actual.valor[1:-1]  # Quitar comillas
            self.avanzar()
            return ast.ValorLiteral(valor, 'cadena')
        elif self.coincidir('VERDADERO'):
            return ast.ValorLiteral(True, 'booleano')
        elif self.coincidir('FALSO'):
            return ast.ValorLiteral(False, 'booleano')
        elif self.coincidir('MOSTRAR'):
            self.avanzar()  
            expr = self.analizar_expresion()  
            self.esperar('PARENTESIS_DER') 
            
            return ast.Mostrar(expr)  
        elif self.coincidir('NULO'):
            return ast.ValorLiteral(None, 'nulo')
        elif self.token_actual.tipo == 'IDENTIFICADOR':
            nombre = self.token_actual.valor
            self.avanzar()
            
            # Verificar si hay un operador de asignación después del identificador
            if self.coincidir('IGUAL'):
                valor_asignado = self.analizar_expresion()  # Analizar lo que se va a asignar
                return ast.AsignacionVariable(nombre, valor_asignado)
            else:
                return ast.Identificador(nombre)
        elif self.coincidir('CORCHETE_IZQ'):
            return self.analizar_lista()
        elif self.coincidir('LLAVE_IZQ'):
            return self.analizar_diccionario()
        else:
            raise SyntaxError(f"Token inesperado: {self.token_actual.tipo} en línea {self.token_actual.linea}, columna {self.token_actual.columna}")

    # Método para analizar una llamada a función
    def analizar_llamada_funcion(self) -> ast.LlamadaFuncion:
        nombre = self.esperar('IDENTIFICADOR').valor  # Obtener el nombre de la función
        self.esperar('PARENTESIS_IZQ')  # Esperar el paréntesis de apertura
        argumentos = []  # Lista de argumentos

        if self.token_actual and self.token_actual.tipo != 'PARENTESIS_DER':  # Si hay argumentos
            argumentos.append(self.analizar_expresion())  # Analizar el primer argumento
            while self.coincidir('COMA'):  # Mientras haya más argumentos separados por comas
                argumentos.append(self.analizar_expresion())  # Analizar cada argumento

        self.esperar('PARENTESIS_DER')  # Esperar el paréntesis de cierre
        return ast.LlamadaFuncion(nombre, argumentos)  # Retornar el nodo de la llamada a función

    # Método para analizar una lista
    def analizar_lista(self) -> ast.ListaValores:
        valores = []  # Lista de valores

        if self.token_actual and self.token_actual.tipo != 'CORCHETE_DER':  # Si la lista no está vacía
            valores.append(self.analizar_expresion())  # Analizar el primer valor
            while self.coincidir('COMA'):  # Mientras haya más valores separados por comas
                valores.append(self.analizar_expresion())  # Analizar cada valor

        self.esperar('CORCHETE_DER')  # Esperar el corchete de cierre
        return ast.ListaValores(valores)  # Retornar el nodo de la lista

    # Método para analizar un diccionario
    def analizar_diccionario(self) -> ast.Diccionario:
        pares = []  # Lista de pares clave-valor

        if self.token_actual and self.token_actual.tipo != 'LLAVE_DER':  # Si el diccionario no está vacío
            clave = self.analizar_expresion()  # Analizar la clave
            self.esperar('DOS_PUNTOS')  # Esperar el separador ":"
            valor = self.analizar_expresion()  # Analizar el valor
            pares.append((clave, valor))  # Agregar el par clave-valor a la lista

            while self.coincidir('COMA'):  # Mientras haya más pares separados por comas
                clave = self.analizar_expresion()  # Analizar la clave
                self.esperar('DOS_PUNTOS')  # Esperar el separador ":"
                valor = self.analizar_expresion()  # Analizar el valor
                pares.append((clave, valor))  # Agregar el par clave-valor a la lista

        self.esperar('LLAVE_DER')  # Esperar la llave de cierre
        return ast.Diccionario(pares)  # Retornar el nodo del diccionario

    # Método para analizar un elemento HTML
    def analizar_elemento_html(self) -> ast.ElementoHTML:
        tipo = self.esperar('IDENTIFICADOR').valor  # Obtener el tipo del elemento HTML
        atributos = {}  # Diccionario de atributos

        # Análisis de atributos
        while self.token_actual and self.token_actual.tipo == 'IDENTIFICADOR' and self.tokens[self.posicion_actual + 1].tipo == 'IGUAL':
            nombre_attr = self.esperar('IDENTIFICADOR').valor  # Obtener el nombre del atributo
            self.esperar('IGUAL')  # Esperar el signo "="
            valor_attr = self.analizar_expresion()  # Analizar el valor del atributo
            atributos[nombre_attr] = valor_attr  # Agregar el atributo al diccionario

        # Contenido del elemento HTML
        contenido = []  # Lista de contenido
        if self.coincidir('PARENTESIS_IZQ'):  # Si hay contenido entre paréntesis
            if self.token_actual and self.token_actual.tipo != 'PARENTESIS_DER':  # Si el contenido no está vacío
                contenido.append(self.analizar_expresion())  # Analizar el primer elemento del contenido
                while self.coincidir('COMA'):  # Mientras haya más elementos separados por comas
                    contenido.append(self.analizar_expresion())  # Analizar cada elemento del contenido
            self.esperar('PARENTESIS_DER')  # Esperar el paréntesis de cierre

        return ast.ElementoHTML(tipo, atributos, contenido)  # Retornar el nodo del elemento HTML

