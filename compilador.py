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

class AnalisadorLexico:
    def __init__(self, texto):
        self.texto = texto
        self.posicao = 0
        self.linha = 1
    
    def _peek(self, deslocamento=0):
        indice = self.posicao + deslocamento
        if indice < len(self.texto):
            return self.texto[indice]
        return ""

    def proximo_token(self):
            