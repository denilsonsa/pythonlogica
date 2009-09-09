#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vi:ts=4 sw=4 et


"""
Módulo prático com utilitários para resolução de exercícios do curso de Lógica
do DCC/UFRJ.

Modo de uso:
 from logica import *
"""


#import foobar


# You can use "from logica import *"
__all__ = [
    "Booleano",
    "Verdadeiro",
    "Falso",

    "Formula",

    "Expressao",
    "ExpressaoSimbolo",
    "ExpressaoNot",
    "ExpressaoBinaria",
    "ExpressaoAnd",
    "ExpressaoOr",

    "criar_simbolos_no_namespace",
]



# The following is based on:
# http://www.python.org/dev/peps/pep-0285/

class Booleano(int):
    """Tipo booleano com operadores redefinidos.

    Este tipo inclui um operador implica, usando a notação "A > B".
    Este tipo suporta os seguintes operadores (usando lógica booleana):
        &  AND
        |  OR
        ^  XOR
        ~  NOT
    É possível usar os operadores "and" e "or" no lugar de "&" e "|".
    Não é recomendado usar o operador "not", prefira usar "~".

    Limitação: não é possível redefinir os operadores "and", "or" e "not".
    Por este motivo, "not A" vai retornar um tipo "bool", e não o tipo Booleano().
    Por outro lado, "and" e "or" vão funcionar corretamente.
    """

    def __new__(cls, val=0):
        if val:
            return Verdadeiro
        else:
            return Falso

    def __repr__(self):
        if self:
            return "Verdadeiro"
        else:
            return "Falso"

    __str__ = __repr__

    # Note: boolean operators (and, or, not) can't be overridden

    def __and__(self, other):
        # This is the bitwise & operator
        return self and Booleano(other)
    __rand__ = __and__

    def __or__(self, other):
        # This is the bitwise | operator
        return self or Booleano(other)
    __ror__ = __or__

    def __xor__(self, other):
        # This is the bitwise ^ operator
        return Booleano(int.__xor__(self, other))
    __rxor__ = __xor__

    def __neg__(self):
        # This is the numeric - operator
        return Booleano(not self)
    # This is the bitwise ~ operator
    __invert__ = __neg__

    def __pos__(self):
        # This is the numeric + operator
        return self

    # No need to override this method
    #def __nonzero__(self):
    #    return self
    def __gt__(self, other):
        """A > B  significa  "A -> B", ou seja, "A implica em B"
        É equivalente a (not A or B).
        """
        return ~ self or other
        # Using "not" will return a bool() type
        #return not self or other


# Bootstrapping the two values:
Verdadeiro = int.__new__(Booleano, 1)
Falso      = int.__new__(Booleano, 0)






class Formula(object):
    """Classe que analisa uma fórmula (ou expressão) e permite:
    * Gerar a tabela verdade.
    * Comparar duas fórmulas quanto à equivalência.
    * Dizer se é tautologia ou contradição.
    """

    def __init__(self, expr, nvars):
        """Formula(expr, nvars)

        expr  -> Função (normalmente um lambda)
        nvars -> Quantidade de variáveis dessa função
        """
        self.expr = expr
        self.nvars = nvars
        self.tbverdade = []

        # Just to prevent out-of-memory and too long operations.
        # This limit can be raised if needed.
        assert nvars < 16

        self.calcular_tabela_verdade()

    def __eq__(self, other):
        """Compara a tabela verdade de duas fórmulas."""
        return Booleano(self.tbverdade == other.tbverdade)

    def calcular_tabela_verdade(self):
        def recursivo(self, valores):
            assert len(valores) <= self.nvars

            if len(valores) == self.nvars:
                #self.tbverdade.append((valores, self.expr(*valores)))
                self.tbverdade.append(self.expr(*valores))
            else:
                recursivo(self,valores + [Verdadeiro])
                recursivo(self,valores + [Falso])

        self.tbverdade = []
        if self.nvars > 0:
            recursivo(self, [])

    def tautologia(self):
        """Retorna Verdadeiro se a fórmula é uma tautologia.
        
        Uma fórmula é tautologia se, e somente se, a tabela verdade é sempre verdadeira."""
        if (self.tbverdade.count(Falso) + self.tbverdade.count(False)) == 0:
            return Verdadeiro
        else:
            return Falso

    def contradicao(self):
        """Retorna Verdadeiro se a fórmula é uma contradição.
        
        Uma fórmula é contradição se, e somente se, a tabela verdade é sempre falsa."""
        if (self.tbverdade.count(Verdadeiro) + self.tbverdade.count(True)) == 0:
            return Verdadeiro
        else:
            return Falso




class Expressao(object):
    """Classe abstrata que representa uma expressão lógica.

    A idéia desta classe e suas derivadas é permitir representar e manipular
    uma expressão lógica.
    """

    symbol = False
    is_not = False
    is_and = False
    is_or  = False
    operator_str = " "

    def __init__(self, child):
        self.children = [child]

    def __repr__(self):
        return "%s(%s)" % (self.__class__.__name__, ', '.join(repr(x) for x in self.children))

    def __str__(self):
        return "(%s)" % (self.operator_str.join(str(x) for x in self.children), )

    def __and__(self, other):
        # This is the bitwise & operator
        return ExpressaoAnd(self, other)
    __rand__ = __and__

    def __or__(self, other):
        # This is the bitwise | operator
        return ExpressaoOr(self, other)
    __ror__ = __or__

    def __xor__(self, other):
        # This is the bitwise ^ operator
        return ExpressaoOr(
            ExpressaoAnd(ExpressaoNot(self), other),
            ExpressaoAnd(self, ExpressaoNot(other))
        )
    __rxor__ = __xor__

    def __neg__(self):
        # This is the numeric - operator
        return ExpressaoNot(self)
    # This is the bitwise ~ operator
    __invert__ = __neg__

    def __pos__(self):
        # This is the numeric + operator
        return self

    def __gt__(self, other):
        """A > B  significa  "A -> B", ou seja, "A implica em B"
        É equivalente a (not A or B).
        """
        return ExpressaoOr(ExpressaoNot(self), other)

    def normalizar(self):
        """Normaliza a expressão, transformando uma sequência de expressões
        binárias iguais em um única expressão n-ária. Também remove duplas
        negações.

        Exemplo:
          (A & (B & (C & D)))  ==>  (A & B & C & D)
          (~ (~ A)) ==> A
        """

        newchildren = []
        for e in self.children:
            e.normalizar()

            # child is NOT
            if e.is_not:
                f = e.children[0]  # there should be only one child
                if f.is_not:
                    # Removing (~ (~ A))
                    newchildren.append(f.children[0])
                else:
                    # Doing nothing
                    newchildren.append(e)

            # self and child are both AND or OR
            elif (e.is_and or e.is_or) and (type(e) == type(self)):
                # (A & (B & C)) ==>  (A & B & C)
                # (A | (B | C)) ==>  (A | B | C)
                newchildren.extend(e.children)

            else:
                # Doing nothing
                newchildren.append(e)
        self.children = newchildren

    def interiorizar_negacao(self):
        """Interioriza a negação, aplicando as leis de De Morgan.

        (~(A & B)) ==> ((~ A) | (~ B))
        (~(A | B)) ==> ((~ A) & (~ B))
        """
        newchildren = []
        for e in self.children:
            # child is NOT
            if e.is_not:
                f = e.children[0]  # there should be only one child
                # grandchild is AND or OR
                if f.is_and or f.is_or:
                    if f.is_and:
                        new_op = ExpressaoOr
                    elif f.is_or:
                        new_op = ExpressaoAnd
                    newchildren.append(
                        new_op(
                            *[ExpressaoNot(x) for x in f.children]
                        )
                    )
                # grandchild is something else
                else:
                    newchildren.append(e)

            else:
                newchildren.append(e)
        self.children = newchildren

        for e in self.children:
            e.interiorizar_negacao()



class ExpressaoSimbolo(Expressao):
    """Representa um símbolo proposicional (um átomo)."""

    symbol = True
    operator_str = ""

    def __init__(self, name=""):
        #super(ExpressaoSimbolo, self).__init__()
        self.name = name

    def __repr__(self):
        return "%s(%s)" % (self.__class__.__name__, repr(self.name))

    def __str__(self):
        return str(self.name)


    def normalizar(self):
        pass

    def interiorizar_negacao(self):
        pass


class ExpressaoNot(Expressao):
    """Representa o operador NOT"""

    is_not = True
    tperador_str = "~ "

    def __init__(self, child):
        #super(ExpressaoNot, self).__init__()
        self.children = [child]

    def __str__(self):
        return "(~ %s)" % (str(self.children[0]), )


class ExpressaoBinaria(Expressao):
    """Representa um operador binário (ou n-ário)"""

    def __init__(self, *children):
        #super(ExpressaoBinaria, self).__init__()
        self.children = list(children)


class ExpressaoAnd(ExpressaoBinaria):
    """Representa o operador AND"""

    is_and = True
    operator_str = " & "


class ExpressaoOr(ExpressaoBinaria):
    """Representa o operador OR"""

    is_or = True
    operator_str = " | "






def criar_simbolos_no_namespace(simbolos, namespace):
    """Exemplo de uso:
    import string
    criar_simbolos_no_namespace(string.uppercase, locals())
    """
    for simbolo in simbolos:
        namespace[simbolo] = ExpressaoSimbolo(simbolo)
