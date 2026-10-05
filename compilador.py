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


            caractere = self._peek()
            linha_token = self.linha   

            if caractere.isdigit():
                inicio = self.pos
                while self._peek().isdigit():
                    self.pos += 1
                if self._peek() == ".":
                    if not self._peek(1).isdigit():
                        raise ErroCompilador(
                            "léxico", "número de ponto flutuante não informado corretamente",
                            linha_token)
                    self.pos += 1
                    while self._peek().isdigit():
                        self.pos += 1
                if self._peek().isalpha():
                    lido = self.texto[inicio:self.pos + 1]
                    raise ErroCompilador(
                        "léxico", f"número seguido de letra: '{lido}'",
                        linha_token)
                return Token("num", self.texto[inicio:self.pos], linha_token)

            if caractere.isalpha() and caractere.isascii():
                inicio = self.pos
                while self._peek().isalpha() and self._peek().isascii():
                    self.pos += 1
                lexema = self.texto[inicio:self.pos]
                if self._peek().isdigit():
                    raise ErroCompilador(
                        "léxico", 
                        f"identificador só pode conter letras: " f"'{lexema}{self._peek()}'",
                        linha_token)
                tipo = PALAVRAS_RESERVADAS.get(lexema, "id")
                return Token(tipo, lexema, linha_token)                      
            
            if caractere in SIMBOLOS:
                self.pos += 1
                return Token(caractere, caractere, linha_token)

            raise ErroCompilador(
                "léxico", f"caractere inválido '{caractere}'",
                linha_token
            )    

class AnalisadorSintatico:
    def __init__(self, texto):
        self.lexico = AnalisadorLexico(texto)
        self.token_atual = self.lexico.proximo_token()
        self.posfixa = []
        self.escopos = []
        self.traducoes = []

    def _avanca(self):
        self.token_atual = self.lexico.proximo_token()

    def _descricao(self, token):
        if token.tipo == "EOF":
            return "fim do código"
        return f"'{token.lexema}'"
        