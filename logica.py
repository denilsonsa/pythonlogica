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
__all__ = ["Boolean", "Verdadeiro", "Falso"]



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
