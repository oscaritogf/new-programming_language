# parser.py
from typing import List
from lexer import Token
import ast_nodes as ast

class Parser:
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.posicion_actual = 0
        self.token_actual = self.tokens[0]
    
    def avanzar(self) -> None:
        self.posicion_actual += 1
        if self.posicion_actual < len(self.tokens):
            self.token_actual = self.tokens[self.posicion_actual]
        else:
            self.token_actual = None
    
    def coincidir(self, tipo: str) -> bool:
        if self.token_actual and self.token_actual.tipo == tipo:
            self.avanzar()
            return True
        return False
    
    def esperar(self, tipo: str) -> Token:
        if self.token_actual and self.token_actual.tipo == tipo:
            token = self.token_actual
            self.avanzar()
            return token
        raise SyntaxError(f"Se esperaba '{tipo}' pero se encontró '{self.token_actual.tipo}' en línea {self.token_actual.linea}, columna {self.token_actual.columna}")
    
    def analizar(self) -> ast.Programa:
        nodos = []
        while self.token_actual and self.token_actual.tipo != 'EOF':
            nodos.append(self.analizar_declaracion())
        return ast.Programa(nodos)
    
    def analizar_declaracion(self) -> ast.Nodo:
        if self.coincidir('VARIABLE'):
            return self.analizar_declaracion_variable()
        elif self.coincidir('SI'):
            return self.analizar_condicional()
        elif self.coincidir('MIENTRAS'):
            return self.analizar_bucle_while()
        elif self.coincidir('PARA'):
            if self.coincidir('CADA'):
                return self.analizar_bucle_foreach()
            return self.analizar_bucle_for()
        elif self.coincidir('FUNCION'):
            return self.analizar_declaracion_funcion()
        elif self.coincidir('DEVOLVER'):
            return self.analizar_retorno()
        else:
            self.coincidir('PUNTO_COMA')
            return self.analizar_expresion()
            return expr
    
    def analizar_declaracion_variable(self) -> ast.DeclaracionVariable:
        nombre = self.esperar('IDENTIFICADOR').valor
        tipo = None
        
        if self.coincidir('DOS_PUNTOS'):
            tipo = self.esperar('IDENTIFICADOR').valor
        
        self.esperar('IGUAL')
        valor = self.analizar_expresion()

        self.coincidir('PUNTO_COMA')
        
        return ast.DeclaracionVariable(nombre, tipo, valor)
    
    def analizar_condicional(self) -> ast.Condicional:
        self.esperar('PARENTESIS_IZQ')
        condicion = self.analizar_expresion()
        self.esperar('PARENTESIS_DER')
        
        self.esperar('LLAVE_IZQ')
        cuerpo = []
        while self.token_actual and self.token_actual.tipo != 'LLAVE_DER':
            cuerpo.append(self.analizar_declaracion())
        self.esperar('LLAVE_DER')
        
        sino = None
        if self.coincidir('SINO'):
            if self.coincidir('SI'):
                # Caso 'sino si'
                return ast.Condicional(condicion, cuerpo, [self.analizar_condicional()])
            else:
                # Caso 'sino'
                self.esperar('LLAVE_IZQ')
                sino = []
                while self.token_actual and self.token_actual.tipo != 'LLAVE_DER':
                    sino.append(self.analizar_declaracion())
                self.esperar('LLAVE_DER')
        
        return ast.Condicional(condicion, cuerpo, sino)
    
    def analizar_bucle_while(self) -> ast.BucleWhile:
        self.esperar('PARENTESIS_IZQ')
        condicion = self.analizar_expresion()
        self.esperar('PARENTESIS_DER')
        
        self.esperar('LLAVE_IZQ')
        cuerpo = []
        while self.token_actual and self.token_actual.tipo != 'LLAVE_DER':
            cuerpo.append(self.analizar_declaracion())
        self.esperar('LLAVE_DER')
        
        return ast.BucleWhile(condicion, cuerpo)
    
    def analizar_bucle_for(self) -> ast.BucleFor:
        self.esperar('PARENTESIS_IZQ')
        inicializacion = self.analizar_declaracion()
        self.esperar('PUNTO_COMA')
        condicion = self.analizar_expresion()
        self.esperar('PUNTO_COMA')
        incremento = self.analizar_expresion()
        self.esperar('PARENTESIS_DER')
        
        self.esperar('LLAVE_IZQ')
        cuerpo = []
        while self.token_actual and self.token_actual.tipo != 'LLAVE_DER':
            cuerpo.append(self.analizar_declaracion())
        self.esperar('LLAVE_DER')
        
        return ast.BucleFor(inicializacion, condicion, incremento, cuerpo)
    
    def analizar_bucle_foreach(self) -> ast.BucleForEach:
        variable = self.esperar('IDENTIFICADOR').valor
        self.esperar('EN')
        iterable = self.analizar_expresion()
        
        self.esperar('LLAVE_IZQ')
        cuerpo = []
        while self.token_actual and self.token_actual.tipo != 'LLAVE_DER':
            cuerpo.append(self.analizar_declaracion())
        self.esperar('LLAVE_DER')
        
        return ast.BucleForEach(variable, iterable, cuerpo)
    
    def analizar_declaracion_funcion(self) -> ast.DeclaracionFuncion:
        nombre = self.esperar('IDENTIFICADOR').valor
        
        self.esperar('PARENTESIS_IZQ')
        parametros = []
        
        if self.token_actual and self.token_actual.tipo != 'PARENTESIS_DER':
            # Primer parámetro
            param_nombre = self.esperar('IDENTIFICADOR').valor
            param_tipo = None
            if self.coincidir('DOS_PUNTOS'):
                param_tipo = self.esperar('IDENTIFICADOR').valor
            parametros.append({'nombre': param_nombre, 'tipo': param_tipo})
            
            # Más parámetros
            while self.coincidir('COMA'):
                param_nombre = self.esperar('IDENTIFICADOR').valor
                param_tipo = None
                if self.coincidir('DOS_PUNTOS'):
                    param_tipo = self.esperar('IDENTIFICADOR').valor
                parametros.append({'nombre': param_nombre, 'tipo': param_tipo})
        
        self.esperar('PARENTESIS_DER')
        
        tipo_retorno = None
        if self.coincidir('DOS_PUNTOS'):
            tipo_retorno = self.esperar('IDENTIFICADOR').valor
        
        self.esperar('LLAVE_IZQ')
        cuerpo = []
        while self.token_actual and self.token_actual.tipo != 'LLAVE_DER':
            cuerpo.append(self.analizar_declaracion())
        self.esperar('LLAVE_DER')
        
        return ast.DeclaracionFuncion(nombre, parametros, tipo_retorno, cuerpo)
    
    def analizar_retorno(self) -> ast.RetornoFuncion:
        valor = None
        if self.token_actual and self.token_actual.tipo != 'PUNTO_COMA':
            valor = self.analizar_expresion()
        return ast.RetornoFuncion(valor)
    
    # Implementar métodos para analizar expresiones (factor, término, etc.)
    # Estos métodos dependen de la precedencia de los operadores
    
    def analizar_expresion(self) -> ast.Nodo:
        # Simplificado para este ejemplo
        return self.analizar_comparacion()
    
    def analizar_comparacion(self) -> ast.Nodo:
        expr = self.analizar_suma()
        
        while self.token_actual and self.token_actual.tipo in ['IGUAL_IGUAL', 'DIFERENTE', 'MAYOR', 'MENOR', 'MAYOR_IGUAL', 'MENOR_IGUAL']:
            operador = self.token_actual.tipo
            self.avanzar()
            derecha = self.analizar_suma()
            expr = ast.OperacionBinaria(expr, operador, derecha)
        
        return expr
    
    def analizar_suma(self) -> ast.Nodo:
        expr = self.analizar_termino()
        
        while self.token_actual and self.token_actual.tipo in ['MAS', 'MENOS']:
            operador = self.token_actual.tipo
            self.avanzar()
            derecha = self.analizar_termino()
            expr = ast.OperacionBinaria(expr, operador, derecha)
        
        return expr
    
    def analizar_termino(self) -> ast.Nodo:
        expr = self.analizar_factor()
        
        while self.token_actual and self.token_actual.tipo in ['MULTIPLICACION', 'DIVISION', 'MODULO']:
            operador = self.token_actual.tipo
            self.avanzar()
            derecha = self.analizar_factor()
            expr = ast.OperacionBinaria(expr, operador, derecha)
        
        return expr
    
    def analizar_factor(self) -> ast.Nodo:
        print(f"Token actual: {self.token_actual.tipo}, Token siguiente: {self.tokens[self.posicion_actual + 1].tipo}")

        if self.coincidir('PARENTESIS_IZQ'):
            expr = self.analizar_expresion()
            self.esperar('PARENTESIS_DER')
            #self.esperar('PUNTO_COMA')
            siguiente = self.token_actual.tipo
            if siguiente in ['PARENTESIS_IZQ', 'ENTERO', 'DECIMAL', 'IDENTIFICADOR']:
                derecha = self.analizar_factor()
                return ast.OperacionBinaria(expr, 'MULTIPLICACION', derecha)
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
            self.avanzar()  # Avanzamos al siguiente token
            expr = self.analizar_expresion()  # Analizamos la expresión que sigue
            self.esperar('PARENTESIS_DER')  # Esperamos el paréntesis derecho
            #self.esperar('PUNTO_COMA')  # Esperamos el punto y coma
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
            

    
    def analizar_llamada_funcion(self) -> ast.LlamadaFuncion:
        nombre = self.esperar('IDENTIFICADOR').valor
        self.esperar('PARENTESIS_IZQ')
        argumentos = []
        
        if self.token_actual and self.token_actual.tipo != 'PARENTESIS_DER':
            argumentos.append(self.analizar_expresion())
            while self.coincidir('COMA'):
                argumentos.append(self.analizar_expresion())
        
        self.esperar('PARENTESIS_DER')
        return ast.LlamadaFuncion(nombre, argumentos)
    
    def analizar_lista(self) -> ast.ListaValores:
        valores = []
        
        if self.token_actual and self.token_actual.tipo != 'CORCHETE_DER':
            valores.append(self.analizar_expresion())
            while self.coincidir('COMA'):
                valores.append(self.analizar_expresion())
        
        self.esperar('CORCHETE_DER')
        return ast.ListaValores(valores)
    
    def analizar_diccionario(self) -> ast.Diccionario:
        pares = []
        
        if self.token_actual and self.token_actual.tipo != 'LLAVE_DER':
            clave = self.analizar_expresion()
            self.esperar('DOS_PUNTOS')
            valor = self.analizar_expresion()
            pares.append((clave, valor))
            
            while self.coincidir('COMA'):
                clave = self.analizar_expresion()
                self.esperar('DOS_PUNTOS')
                valor = self.analizar_expresion()
                pares.append((clave, valor))
        
        self.esperar('LLAVE_DER')
        return ast.Diccionario(pares)
    
    def analizar_elemento_html(self) -> ast.ElementoHTML:
        tipo = self.esperar('IDENTIFICADOR').valor
        atributos = {}
        
        # Análisis de atributos
        while self.token_actual and self.token_actual.tipo == 'IDENTIFICADOR' and self.tokens[self.posicion_actual + 1].tipo == 'IGUAL':
            nombre_attr = self.esperar('IDENTIFICADOR').valor
            self.esperar('IGUAL')
            valor_attr = self.analizar_expresion()
            atributos[nombre_attr] = valor_attr
        
        # Contenido
        contenido = []
        if self.coincidir('PARENTESIS_IZQ'):
            if self.token_actual and self.token_actual.tipo != 'PARENTESIS_DER':
                contenido.append(self.analizar_expresion())
                while self.coincidir('COMA'):
                    contenido.append(self.analizar_expresion())
            self.esperar('PARENTESIS_DER')
        
        return ast.ElementoHTML(tipo, atributos, contenido)
    
