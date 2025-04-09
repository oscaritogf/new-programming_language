# main.py
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from interpreter import Interprete
from parser import Parser
from html_renderer import HTMLRenderer
from fastapi.middleware.cors import CORSMiddleware



import traceback
import uvicorn

app = FastAPI()

origins = [
    "http://127.0.0.1:8000",
    "http://127.0.0.1",
    "http://localhost:8000",
    "http://localhost:3000"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permitir todas las orígenes
    allow_credentials=True,
    allow_methods=["*"],  # Permitir todos los métodos
    allow_headers=["*"],

  # Permitir todos los encabezados
)

# Configurar plantillas y archivos estáticos
"""templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")
"""
class CodigoEntrada(BaseModel):
    codigo: str

@app.get("/")
async def home():
    return {"mensaje": "Bienvenido a la API del intérprete"}
            
@app.post("/interpretar")
async def interpretar_codigo(entrada: CodigoEntrada):
    try:
        interprete = Interprete()
        resultado = interprete.ejecutar(entrada.codigo)
        
        # Construir respuesta
        respuesta = {
            "estado": "exito",
            "resultado": str(resultado.valor) if resultado else "nulo",
            "tipo": resultado.tipo if resultado else "nulo"
        }
        
        # Si el resultado es HTML o CSS, incluirlo
        if resultado and resultado.tipo == 'html':
            respuesta["html"] = HTMLRenderer.convertir_a_html(resultado)
        elif resultado and resultado.tipo == 'css':
            respuesta["css"] = HTMLRenderer.convertir_a_css(resultado)
        
        return respuesta
    except Exception as e:
        traceback_str = traceback.format_exc()
        # Extraer información relevante para un mensaje de error amigable
        mensaje_error = str(e)
        
        # Buscar información de línea y columna en el mensaje de error
        linea = None
        columna = None
        if hasattr(e, 'linea') and hasattr(e, 'columna'):
            linea = e.linea
            columna = e.columna
        
        return {
            "estado": "error",
            "error": mensaje_error,
            "traceback": traceback_str,
            "linea": linea,
            "columna": columna
        }



@app.get("/ast")
async def obtener_ast(codigo: str):
    try:
        from lexer import Lexer
        lexer = Lexer()
        tokens = lexer.tokenizar(codigo)
        
        parser = Parser(tokens)
        ast_root = parser.analizar()
        
        # Convertir AST a una estructura JSON mejorada
        def serializar_ast(nodo):
            if nodo is None:
                return None
            
            result = {
                "tipo": type(nodo).__name__,
                "linea": getattr(nodo, "linea", None),  # Agregar línea si existe
                "columna": getattr(nodo, "columna", None),
            }
            
            for key, value in vars(nodo).items():
                if isinstance(value, list):
                    result[key] = [serializar_ast(item) if hasattr(item, '__dict__') else item for item in value]
                elif hasattr(value, '__dict__'):
                    result[key] = serializar_ast(value)
                else:
                    result[key] = value
            
            return result
        
        return {"estado": "exito", "ast": serializar_ast(ast_root)}
    except Exception as e:
        return {"estado": "error", "error": str(e)}
    
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)