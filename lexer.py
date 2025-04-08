# lexer.py
import re
from typing import List, Tuple, Optional

class Token:
    def __init__(self, tipo: str, valor: str, linea: int, columna: int):
        self.tipo = tipo
        self.valor = valor
        self.linea = linea
        self.columna = columna
    
    def __repr__(self):
        return f"Token({self.tipo}, '{self.valor}', {self.linea}, {self.columna})"

class Lexer:
    def __init__(self):
        # Palabras clave
        self.palabras_clave = {
            'variable': 'VARIABLE',
            'si': 'SI',
            'sino': 'SINO',
            'para': 'PARA',
            'mientras': 'MIENTRAS',
            'funcion': 'FUNCION',
            'devolver': 'DEVOLVER',
            'mostrar': 'MOSTRAR',
            'verdadero': 'VERDADERO',
            'falso': 'FALSO',
            'nulo': 'NULO',
            'y': 'Y',
            'o': 'O',
            'no': 'NO',
            'cada': 'CADA',
            'en': 'EN',
            'llamado': 'LLAMADO'
        }
        
        # Patrones de token usando expresiones regulares
        self.patrones = [
            (r'[ \t]+', None),  # Espacios y tabulaciones
            (r'\n', None),
            (r'#.*', None),  # Comentarios
            (r'\(', 'PARENTESIS_IZQ'),
            (r'\)', 'PARENTESIS_DER'),
            (r'\{', 'LLAVE_IZQ'),
            (r'\}', 'LLAVE_DER'),
            (r'\[', 'CORCHETE_IZQ'),
            (r'\]', 'CORCHETE_DER'),
            (r';', 'PUNTO_COMA'),
            (r',', 'COMA'),
            (r':', 'DOS_PUNTOS'),
            (r'\.', 'PUNTO'),
            (r'=', 'IGUAL'),
            (r'\+', 'MAS'),
            (r'-', 'MENOS'),
            (r'\*', 'MULTIPLICACION'),
            (r'/', 'DIVISION'),
            (r'%', 'MODULO'),
            (r'\^', 'POTENCIA'),
            (r'==', 'IGUAL_IGUAL'),
            (r'!=', 'DIFERENTE'),
            (r'>=', 'MAYOR_IGUAL'),
            (r'<=', 'MENOR_IGUAL'),
            (r'>', 'MAYOR'),
            (r'<', 'MENOR'),
            (r'"[^"]*"|\'[^\']*\'', 'CADENA'),
            (r'\d+\.\d+', 'DECIMAL'),
            (r'\d+', 'ENTERO'),
            (r'[a-zA-ZñÑáéíóúÁÉÍÓÚ_][a-zA-ZñÑáéíóúÁÉÍÓÚ0-9_]*', 'IDENTIFICADOR')
        ]
    
    def tokenizar(self, codigo: str) -> List[Token]:
        tokens = []
        linea = 1
        columna = 1
        
        i = 0
        while i < len(codigo):
            match = None
            
            # Intentar coincidir con un patrón
            for patron, tipo in self.patrones:
                regex = re.compile(patron)
                match = regex.match(codigo, i)
                if match:
                    texto = match.group(0)
                    if tipo:
                        # Comprobar si es una palabra clave
                        if tipo == 'IDENTIFICADOR' and texto in self.palabras_clave:
                            tokens.append(Token(self.palabras_clave[texto], texto, linea, columna))
                        else:
                            tokens.append(Token(tipo, texto, linea, columna))
                    
                    # Actualizar posición
                    if tipo == 'SALTO_LINEA':
                        linea += 1
                        columna = 1
                    else:
                        columna += len(texto)
                    
                    i = match.end()
                    break
            
            if not match:
                # Si no hay coincidencia, reportar error
                raise SyntaxError(f"Carácter no reconocido: '{codigo[i]}' en línea {linea}, columna {columna}")
        
        # Añadir token de fin de archivo
        tokens.append(Token('EOF', '', linea, columna))
        return tokens