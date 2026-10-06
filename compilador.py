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
    
    def match(self, tipo_esperado):
        if self.token_atual.tipo == tipo_esperado:
            token = self.token_atual
            self._avanca()
            return token
        if tipo_esperado == "EOF":
            esperado = "fim do código"
        else:
            esperado = f"'{tipo_esperado}"
        raise ErroCompilador(
            "sintático",
            f"esperado {esperado}, encontrado " f"{self._descricao(self.token_atual)}",
            self.token_atual.linha)

    def _procura_variavel(self, nome):
        for escopo in reversed(self.escopos):
            if nome in escopo:
                return escopo[nome]
        return None

    def program(self):
        self.match("Matexpr")
        self.block()
        self.match("EOF")

    def block(self):
        self.match("{")
        self.escopos.append({})
        self.decls()
        self.stmts()
        self.match("}")
        self.escopos.pop()      

    def decls(self):
        while self.token_atual.tipo == "type":
            self.decl()
    
    def decl(self):
        tipo_variavel = self.match("type").lexema
        token_id = self.match("id")
        escopo_atual = self.escopos[-1]
        if token_id.lexema in escopo_atual:
            raise ErroCompilador(
                "semântico",
                f"variável '{token_id.lexema}' já declarada nesse local",
                token_id.linha)
        escopo_atual[token_id.lexema] = tipo_variavel
        self.match(";")
    
    def stmts(self):
        while self.token_atual.tipo in ("{", "(", "num","id"):
            self.stmt()
        if self.token_atual.tipo == "type":
            raise ErroCompilador(
                "sintático",
                "declarações devem vir antes dos comandos de bloco",
                self.token_atual.linha)
    
    def stmt(self):
        if self.token_atual.tipo == "{":
            self.block()
        else:
            self.posfixa = []
            self.expr()
            self.match(";")
            self.traducoes.append(" ".join(self.posfixa))
    
    def expr(self):
        self.term()
        while self.token_atual.tipo in ("+", "-"):
            operador = self.token_atual.tipo
            self._avanca()
            self.term()
            self.posfixa.append(operador)

    def term(self):
        self.fact()
        while self.token_atual.tipo in ("*", "/"):
            operador = self.token_atual.tipo
            self._avanca()
            self.fact()
            self.posfixa.append(operador)

    def fact(self):
        tipo = self.token_atual.tipo
        if tipo == "(":
            self._avanca()
            self.expr()
            self.match(")")
        elif tipo == "num":
            self.posfixa.append(self.token_atual.lexema)
            self._avanca()
        elif tipo == "id":
            nome = self.token_atual.lexema
            if self._procura_variavel(nome) is None:
                raise ErroCompilador(
                    "semântico", f"variável '{nome}' não declarada",
                    self.token_atual.linha)

            self.posfixa.append(nome)
            self._avanca()

        else:
            raise ErroCompilador(
                "sintático",
                f"esperado '(', número ou identificador, encontrado "
                f"{self._descricao(self.token_atual)}",
                self.token_atual.linha
                )