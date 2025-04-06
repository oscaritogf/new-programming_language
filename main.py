# main.py
# Importaciones necesarias para FastAPI y otras funcionalidades
from fastapi import FastAPI  # Framework para construir APIs
from pydantic import BaseModel  # Para definir modelos de datos
from interpreter import Interprete  # Importa la clase Interprete (lógica del intérprete)
from parser import Parser  # Importa la clase Parser (analizador sintáctico)
from html_renderer import HTMLRenderer  # Importa la clase HTMLRenderer (renderizador de HTML)
from fastapi.middleware.cors import CORSMiddleware  # Middleware para habilitar CORS

import traceback  # Para manejar y formatear errores
import uvicorn  # Para ejecutar el servidor FastAPI

# Crear una instancia de la aplicación FastAPI
app = FastAPI()

# Lista de orígenes permitidos para solicitudes CORS
origins = [
    "http://127.0.0.1:8000",  # Origen local
    "http://127.0.0.1",  # Origen local sin puerto
    "http://localhost:8000",  # Origen local con puerto
    "http://localhost:3000"  # Origen local para frontend (React, etc.)
]

# Configuración del middleware CORS para permitir solicitudes desde otros dominios
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permitir todas las orígenes (en producción, especificar dominios)
    allow_credentials=True,  # Permitir el uso de cookies/credenciales
    allow_methods=["*"],  # Permitir todos los métodos HTTP (GET, POST, etc.)
    allow_headers=["*"],  # Permitir todos los encabezados
)

# Modelo de datos para recibir el código como entrada en las solicitudes POST
class CodigoEntrada(BaseModel):
    codigo: str  # El código fuente que se enviará para interpretar

# Ruta raíz (GET) que devuelve un mensaje de bienvenida
@app.get("/")
async def home():
    return {"mensaje": "Bienvenido a la API del intérprete"}

# Ruta para interpretar el código enviado (POST)
@app.post("/interpretar")
async def interpretar_codigo(entrada: CodigoEntrada):
    try:
        # Crear una instancia del intérprete
        interprete = Interprete()
        
        # Ejecutar el código enviado y obtener el resultado
        resultado = interprete.ejecutar(entrada.codigo)
        
        # Construir la respuesta con el resultado
        respuesta = {
            "estado": "exito",  # Indica que la ejecución fue exitosa
            "resultado": str(resultado.valor) if resultado else "nulo",  # Valor del resultado
            "tipo": resultado.tipo if resultado else "nulo"  # Tipo del resultado
        }
        
        # Si el resultado es HTML o CSS, convertirlo a su representación adecuada
        if resultado and resultado.tipo == 'html':
            respuesta["html"] = HTMLRenderer.convertir_a_html(resultado)
        elif resultado and resultado.tipo == 'css':
            respuesta["css"] = HTMLRenderer.convertir_a_css(resultado)
        
        return respuesta  # Devolver la respuesta como JSON
    except Exception as e:
        # Manejar errores y construir una respuesta de error
        traceback_str = traceback.format_exc()  # Obtener el traceback completo
        mensaje_error = str(e)  # Mensaje de error
        
        # Extraer información de línea y columna si está disponible
        linea = None
        columna = None
        if hasattr(e, 'linea') and hasattr(e, 'columna'):
            linea = e.linea
            columna = e.columna
        
        return {
            "estado": "error",  # Indica que ocurrió un error
            "error": mensaje_error,  # Mensaje de error
            "traceback": traceback_str,  # Detalles del error
            "linea": linea,  # Línea donde ocurrió el error
            "columna": columna  # Columna donde ocurrió el error
        }

# Ruta para obtener el árbol sintáctico abstracto (AST) del código enviado (GET)
@app.get("/ast")
async def obtener_ast(codigo: str):
    try:
        # Importar y crear una instancia del analizador léxico
        from lexer import Lexer
        lexer = Lexer()
        
        # Tokenizar el código enviado
        tokens = lexer.tokenizar(codigo)
        
        # Crear una instancia del analizador sintáctico y analizar los tokens
        parser = Parser(tokens)
        ast_root = parser.analizar()
        
        # Función para serializar el AST en un formato JSON
        def serializar_ast(nodo):
            if nodo is None:
                return None
            
            # Construir un diccionario con los atributos del nodo
            result = {
                "tipo": type(nodo).__name__,  # Tipo del nodo
                "linea": getattr(nodo, "linea", None),  # Línea del nodo (si existe)
                "columna": getattr(nodo, "columna", None),  # Columna del nodo (si existe)
            }
            
            # Serializar los atributos del nodo
            for key, value in vars(nodo).items():
                if isinstance(value, list):  # Si el atributo es una lista, serializar cada elemento
                    result[key] = [serializar_ast(item) if hasattr(item, '__dict__') else item for item in value]
                elif hasattr(value, '__dict__'):  # Si el atributo es un objeto, serializarlo
                    result[key] = serializar_ast(value)
                else:  # Si es un valor simple, agregarlo directamente
                    result[key] = value
            
            return result
        
        # Devolver el AST serializado como JSON
        return {"estado": "exito", "ast": serializar_ast(ast_root)}
    except Exception as e:
        # Manejar errores y devolver una respuesta de error
        return {"estado": "error", "error": str(e)}

# Punto de entrada principal para ejecutar el servidor
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)  # Ejecutar el servidor en el puerto 8000