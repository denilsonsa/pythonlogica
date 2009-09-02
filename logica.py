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
__all__ = ["Boolean", "Verdadeiro", "Falso", "Formula"]



# The following is based on:
# http://www.python.org/dev/peps/pep-0285/

class Boolean(int):
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
    Por este motivo, "not A" vai retornar um tipo "bool", e não o tipo Boolean().
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
        return self and Boolean(other)
    __rand__ = __and__

    def __or__(self, other):
        # This is the bitwise | operator
        return self or Boolean(other)
    __ror__ = __or__

    def __xor__(self, other):
        # This is the bitwise ^ operator
        return Boolean(int.__xor__(self, other))
    __rxor__ = __xor__

    def __neg__(self):
        # This is the numeric - operator
        return Boolean(not self)
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
Verdadeiro = int.__new__(Boolean, 1)
Falso      = int.__new__(Boolean, 0)






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

        # Just to prevent out-of-memory.
        # This limit can be raised if needed.
        assert nvars < 10

        self.calcular_tabela_verdade()

    def __eq__(self, other):
        """Compara a tabela verdade de duas fórmulas."""
        return self.tbverdade == other.tbverdade

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
