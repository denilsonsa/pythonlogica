#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vi:ts=4 sw=4 et foldmethod=indent foldlevel=1


"""
Módulo prático com utilitários para resolução de exercícios do curso de Lógica
do DCC/UFRJ.

Modo de uso:
$ ipython
>>> from logica import *
>>>
>>> import string
>>> criar_simbolos_no_namespace(string.uppercase, globals())
>>>
>>> # As duas linhas acima sao equivalentes a:
>>> # criar_simbolos_no_namespace("ABCDEFGHIJKLMNOPQRSTUVWXYZ", globals())
>>>
>>> e = A & B
>>> str(e)
'(A & B)'
>>> repr(e)
"ExpressaoAnd(ExpressaoSimbolo('A'), ExpressaoSimbolo('B'))"
>>> e.eval({'A': Verdadeiro, 'B': Falso})
Falso
>>> e = Expressao(e)
>>> str(e)
'((A & B))'
>>> repr(e)
"Expressao(ExpressaoAnd(ExpressaoSimbolo('A'), ExpressaoSimbolo('B')))"
>>>
>>> e = Expressao( (A & ~B) | (B & ~A) )
>>> str(e)
'(((A & ~ B) | (B & ~ A)))'
>>> repr(e)
"Expressao(ExpressaoOr(ExpressaoAnd(ExpressaoSimbolo('A'), ExpressaoNot(ExpressaoSimbolo('B'))), ExpressaoAnd(ExpressaoSimbolo('B'), ExpressaoNot(ExpressaoSimbolo('A')))))"
>>> e.transformar_em_forma_normal_conjuntiva()
>>> str(e)
'(((A | B) & (A | ~ A) & (~ B | B) & (~ B | ~ A)))'
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

    is_symbol = False
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

    def __eq__(self, other):
        """Compara se duas expressões são iguais.

        A comparação é feita comparando a árvore de ambas as expressões, então
        na verdade isto apenas compara se as expressões são *estruturalmente*
        iguais.

        Note que:
          (A & B) == (A & B)
        porém:
          (A & B) != (B & A)
        """
        return (
                type(self) == type(other)
            ) and (
                self.children == other.children
            )

    def __ne__(self, other):
        return not (self == other)

    def generate_sort_key(self, sorted_list):
        self.sort_key = "(%s)" % (self.operator_str.join(x.sort_key for x in sorted_list), )

    def generate_sort_keys(self, recursive=True):
        if recursive:
            for e in self.children:
                e.generate_sort_keys(recursive=recursive)

        self.generate_sort_key(
            sorted(self.children, key=lambda x: x.sort_key)
        )

    def comparar_ignorando_ordem(self, other):
        """Compara se duas expressões são iguais, através da comparação da
        árvore das duas expressões. A ordem dos operandos será ignorada.

        É necessário chamar .generate_sort_keys() antes de realizar a
        comparação, caso contrário os resultados são indeterminados.

        >>> A = ExpressaoSimbolo('A')
        >>> B = ExpressaoSimbolo('B')
        >>> e = A & B
        >>> f = B & A
        >>> e == f
        False
        >>> e.generate_sort_keys()
        >>> f.generate_sort_keys()
        >>> e.comparar_ignorando_ordem(f)
        True
        """
        return self.sort_key == other.sort_key

    def simbolos(self):
        """Retorna um set() com os símbolos proposicionais presentes nesta expressão."""
        l = set()
        for e in self.children:
            l.update(e.simbolos())
        return l

    def eval(self, valores):
        """Avalia a expressão, retornando o valor da expressão dados os valores dos símbolos passados."""
        return self.children[0].eval(valores)

    def remover_associativas(self, recursive=True):
        """Remove as operações associativas, transformando uma sequência de
        expressões binárias iguais em um única expressão n-ária.

        (A & (B & (C & D)))  ==>  (A & B & C & D)

        Este método opera a partir de um objeto AND/OR.
        ExpressaoAnd(A, ExpressaoAnd(B, C)) ==> (A & B & C)
        """
        newchildren = []
        for e in self.children:
            if recursive:
                e.remover_associativas(recursive=recursive)

            # self and child are both AND or OR
            if (e.is_and or e.is_or) and (type(e) == type(self)):
                # (A & (B & C)) ==>  (A & B & C)
                # (A | (B | C)) ==>  (A | B | C)
                newchildren.extend(e.children)

            else:
                # Doing nothing
                newchildren.append(e)
        self.children = newchildren

    def remover_duplas_negacoes(self, recursive=True, auto_remover_associativas=False):
        """Remove duplas negações.

        (~ (~ A)) ==> A

        Este método opera a partir de um objeto pai em relação ao NOT.
        Expressao(ExpressaoNot(ExpressaoNot(A)) ==> Expressao(A)

        Este método pode opcionalmente chamar .remover_associativas(),
        dependendo do parâmetro auto_remover_associativas:
          auto_remover_associativas = False:
            (A & ~ ~ (B & C)) ==> (A & (B & C))
          auto_remover_associativas = True:
            (A & ~ ~ (B & C)) ==> (A & B & C)
        """
        modified = False
        newchildren = []
        for e in self.children:
            # child is NOT
            while e.is_not:
                f = e.children[0]  # there should be only one child
                # grandchild is also NOT
                if f.is_not:
                    # Removing (~ (~ A))
                    e = f.children[0]
                    modified = True
                # grandchild is something else
                else:
                    # Doing nothing
                    break
            newchildren.append(e)
        self.children = newchildren

        if modified and auto_remover_associativas:
            self.remover_associativas(recursive=False)

        if recursive:
            for e in self.children:
                e.remover_duplas_negacoes(
                    recursive=recursive,
                    auto_remover_associativas=auto_remover_associativas
                )

    def interiorizar_negacao(self, recursive=True):
        """Interioriza a negação, aplicando as leis de De Morgan.

        (~(A & B)) ==> ((~ A) | (~ B))
        (~(A | B)) ==> ((~ A) & (~ B))

        Este método opera a partir de um objeto pai em relação ao NOT.
        Expressao(~(A & B)) ==> Expressao((~A) | (~B))
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
                    newchildren[-1].remover_duplas_negacoes(recursive=False)
                # grandchild is something else
                else:
                    newchildren.append(e)

            else:
                newchildren.append(e)
        self.children = newchildren

        if recursive:
            for e in self.children:
                e.interiorizar_negacao(recursive=recursive)

    def interiorizar_or(self):
        """Interioriza o OR, aplicando:
        (A | (B & C))  ==>  ((A | B) & (A | C))

        Este método opera a partir de um objeto pai em relação ao OR.
        Expressao(A | (B & C)) ==> Expressao((A | B) & (A | C))

        Este método não remove associativas automaticamente, portanto,
        é recomendável executar .remover_associativas() após chamar este
        método.
        """
        newchildren = []
        for e in self.children:
            # child is OR
            if e.is_or:
                # Looking for AND inside OR
                for f in e.children:
                    # grandchild is AND
                    if f.is_and:
                        novo_and = []
                        for filho_do_and in f.children:
                            # Criando um OR para cada operando do AND
                            novo_or = []
                            for filho_do_or in e.children:
                                if filho_do_or == f:
                                    novo_or.append(filho_do_and)
                                else:
                                    novo_or.append(filho_do_or)
                            novo_and.append(ExpressaoOr(*novo_or))
                        # Finally, replacing old OR by the new AND
                        newchildren.append(ExpressaoAnd(*novo_and))
                        break
                # OR has no AND inside it
                else:  # for-else
                    newchildren.append(e)
            # child is something else
            else:
                newchildren.append(e)

        self.children = newchildren
        for e in self.children:
            e.interiorizar_or()

    def transformar_em_forma_normal_conjuntiva(self):
        self.remover_duplas_negacoes()
        self.remover_associativas()
        self.interiorizar_negacao()
        self.interiorizar_or()
        self.remover_associativas()

    def remover_operacoes_vazias(self, recursive=True):
        """Remove as operações vazias, ou seja, operações/operadores que
        possuam zero operandos.

        Este método é útil para remover operações vazias em decorrência da
        manipulação da árvore.

        Este método opera a partir de um objeto pai em relação às operações
        vazias.
        Expressao(ExpressaoAnd()) ==> Expressao()
        """
        if recursive:
            for e in self.children:
                e.remover_operacoes_vazias(recursive=recursive)

        newchildren = []
        for e in self.children:
            # Child is an operator with zero operands
            if not e.is_symbol and len(e.children) == 0:
                pass
            else:
                newchildren.append(e)
        self.children = newchildren




class ExpressaoSimbolo(Expressao):
    """Representa um símbolo proposicional (um átomo)."""

    is_symbol = True
    operator_str = ""

    def __init__(self, name=""):
        #super(ExpressaoSimbolo, self).__init__()
        self.children = []
        self.name = name

    def __repr__(self):
        return "%s(%s)" % (self.__class__.__name__, repr(self.name))

    def __str__(self):
        return str(self.name)

    def __eq__(self, other):
        """Compara se dois símbolos têm o mesmo nome."""
        return (
                type(self) == type(other)
            ) and (
                self.children == other.children
            ) and (
                self.name == other.name
            )

    def generate_sort_keys(self, recursive=True):
        self.sort_key = self.name

    def simbolos(self):
        return set(self.name)

    def eval(self, valores):
        return valores[self.name]



class ExpressaoNot(Expressao):
    """Representa o operador NOT"""

    is_not = True
    operator_str = ""

    def __init__(self, child):
        #super(ExpressaoNot, self).__init__()
        self.children = [child]

    def __str__(self):
        return "~ %s" % (str(self.children[0]), )
        #return "(~ %s)" % (str(self.children[0]), )

    def generate_sort_key(self, sorted_list):
        self.sort_key = "(~ %s)" % (sorted_list[0].sort_key, )

    def eval(self, valores):
        return ~ self.children[0].eval(valores)


class ExpressaoBinaria(Expressao):
    """Representa um operador binário (ou n-ário)"""

    def __init__(self, *children):
        #super(ExpressaoBinaria, self).__init__()
        self.children = list(children)


class ExpressaoAnd(ExpressaoBinaria):
    """Representa o operador AND"""

    is_and = True
    operator_str = " & "

    def eval(self, valores):
        return reduce(lambda x,y: x.eval(valores) & y.eval(valores), self.children)


class ExpressaoOr(ExpressaoBinaria):
    """Representa o operador OR"""

    is_or = True
    operator_str = " | "

    def eval(self, valores):
        return reduce(lambda x,y: x.eval(valores) | y.eval(valores), self.children)






def criar_simbolos_no_namespace(simbolos, namespace):
    """Exemplo de uso:
    import string
    criar_simbolos_no_namespace(string.uppercase, locals())
    """
    for simbolo in simbolos:
        namespace[simbolo] = ExpressaoSimbolo(simbolo)
