# html_renderer.py
from interpreter import Valor
class HTMLRenderer:
    @staticmethod
    def convertir_a_html(valor: Valor) -> str:
        if valor.tipo != 'html':
            return str(valor.valor)
        
        elemento = valor.valor
        tipo = elemento['tipo']
        atributos = elemento['atributos']
        contenido = elemento['contenido']
        
        # Construir atributos HTML
        attr_str = ""
        for nombre, valor_attr in atributos.items():
            attr_str += f' {nombre}="{valor_attr.valor}"'
        
        # Construir contenido HTML
        contenido_str = ""
        for item in contenido:
            contenido_str += HTMLRenderer.convertir_a_html(item)
        
        # Devolver HTML completo
        return f"<{tipo}{attr_str}>{contenido_str}</{tipo}>"
    
    @staticmethod
    def convertir_a_css(valor: Valor) -> str:
        if valor.tipo != 'css':
            return ""
        
        estilo = valor.valor
        selector = estilo['selector']
        propiedades = estilo['propiedades']
        
        # Construir CSS
        props_str = ""
        for nombre, valor_prop in propiedades.items():
            props_str += f"  {nombre}: {valor_prop};\n"
        
        return f"{selector} {{\n{props_str}}}"