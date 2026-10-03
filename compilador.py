import sys

class ErroCompilador(Exception):
    def __init__(self, tipo, msg, linha):
        super().__init__(f"Erro {tipo} (linha {linha}): {msg}")

class Token:
    def __init__(self, tipo, lexema, linha):
        self.tipo, self.lexema, self.linha = tipo, lexema, linha

    def __repr__(self):
        return f"<{self.tipo}, {self.lexema!r}, l.{self.linha}>"


PALAVRAS_RESERVADAS = {
    "Matexpr": "Matexpr",
    "int": "type",
    "float": "type",
}
SIMBOLOS = set("{}();+*/")