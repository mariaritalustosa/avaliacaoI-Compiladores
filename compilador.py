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
            while True:
                caractere = self._peek()
                if caractere == "":
                    return Token("EOF", "", self.linha)

                if caractere in " \t\r\f\v":
                    self.pos += 1

                elif caractere == "\n":
                    self.linha += 1
                    self.pos += 1
                
                elif caractere == "/" and self._espia(1) == "*":
                    linha_inicio = self.linha
                    self.pos += 2
                    while not (self._peek() == "*" and self._peek(1) == "/"):
                        if self._peek() == "":
                            raise ErroCompilador(
                                "léxico", "comentário '/*' não foi fechado",
                                linha_inicio)
                        if self._peek() == "\n":
                            self.linha += 1
                        self.pos += 1
                    self.pos += 2

                elif caractere == "/" and self._peek(1) == "/":
                    while self._peek() not in ("", "\n"):
                        self.pos += 1

                else:
                    break                            
