#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vi:ts=4 sw=4 et foldmethod=indent foldlevel=1

import unittest
import string
from logica import *


class TestarExpressoes(unittest.TestCase):
    def setUp(self):
        # Ugly... Writing to globals()...
        # But it is damn handy! :)
        criar_simbolos_no_namespace(string.uppercase, globals())

    def tearDown(self):
        for i in string.uppercase:
            del globals()[i]

    #################################################################
    # Testes de operadores

    def test_simbolos_iguais(self):
        self.assertEqual(
            ExpressaoSimbolo("x"),
            ExpressaoSimbolo("x")
        )

    def test_simbolos_diferentes(self):
        self.assertNotEqual(
            ExpressaoSimbolo("x"),
            ExpressaoSimbolo("y")
        )

    def test_operador_parentese(self):
        e = Expressao(A)
        self.assertEqual(
            len(e.children),
            1
        )
        self.assertEqual(
            e.children[0],
            A
        )

    def test_operador_not(self):
        self.assertEqual(
            ExpressaoNot(A),
            ~ A
        )

    def test_operador_not_duplicado(self):
        self.assertEqual(
            ExpressaoNot(ExpressaoNot(A)),
            ~ ~ A
        )

    def test_operador_and(self):
        self.assertEqual(
            ExpressaoAnd(A, B),
            A & B
        )

    def test_operador_or(self):
        self.assertEqual(
            ExpressaoOr(A, B),
            A | B
        )

    def test_operador_implica(self):
        self.assertEqual(
            ExpressaoOr(ExpressaoNot(A), B),
            A > B
        )

    def test_precedencia_and_not(self):
        self.assertEqual(
            ExpressaoAnd(ExpressaoNot(A), ExpressaoNot(B)),
            ~A & ~B
        )

    def test_precedencia_or_not(self):
        self.assertEqual(
            ExpressaoOr(ExpressaoNot(A), ExpressaoNot(B)),
            ~A | ~B
        )

    def test_precedencia_implica_not(self):
        self.assertEqual(
            ExpressaoOr(ExpressaoNot(ExpressaoNot(A)), ExpressaoNot(B)),
            ~A > ~B
        )

    #################################################################
    # Testes de manipulações
    #
    # Muitos dos testes abaixos exigem que a expressão seja
    # encapsulada num parêntese, usando Expressao(). Isto é
    # necessário porque a maioria das manipulações consegue
    # operar apenas nos filhos.

    def test_remover_dupla_negacao(self):
        e = Expressao(~ ~ A)
        e.remover_duplas_negacoes()
        self.assertEqual(
            Expressao(A),
            e
        )

    def test_demorgan_and(self):
        e = Expressao(~ (A & B))
        e.interiorizar_negacao()
        self.assertEqual(
            ExpressaoOr(ExpressaoNot(A), ExpressaoNot(B)),
            e.children[0]
        )

    def test_demorgan_or(self):
        e = Expressao(~ (A | B))
        e.interiorizar_negacao()
        self.assertEqual(
            ExpressaoAnd(ExpressaoNot(A), ExpressaoNot(B)),
            e.children[0]
        )

    def test_demorgan_and_remover_dupla_negacao(self):
        e = Expressao(~ (~A & ~B))
        e.interiorizar_negacao()
        self.assertEqual(
            ExpressaoOr(A, B),
            e.children[0]
        )

    def test_demorgan_or_remover_dupla_negacao(self):
        e = Expressao(~ (~A | ~B))
        e.interiorizar_negacao()
        self.assertEqual(
            ExpressaoAnd(A, B),
            e.children[0]
        )

    def test_demorgan_remover_dupla_negacao_1(self):
        e = Expressao(~(~ ~ A & ~ ~ (~B & C)))
        e.interiorizar_negacao()
        self.assertEqual(
            Expressao(~ A | (B | ~ C)),
            e
        )

    def test_demorgan_remover_dupla_negacao_2(self):
        """Ao executar .interiorizar_negacao(), a remoção automática da dupla negação deve acontecer de forma não recursiva."""
        e = Expressao(~(~ ~ ~ A & ~ ~ (~B & C)))
        e.interiorizar_negacao()
        self.assertEqual(
            Expressao(~ ~ A | (B | ~ C)),
            e
        )

    def test_demorgan_remover_dupla_negacao_3(self):
        """Ao executar .interiorizar_negacao(), a remoção automática da dupla negação deve acontecer de forma não recursiva."""
        e = Expressao(~(~ A & ~ ~ B & ~ ~ ~ C) & ~ ~ D)
        e.interiorizar_negacao()
        self.assertEqual(
            Expressao((A | ~ B | ~ ~ C) & ~ ~ D),
            e
        )

    def test_remover_associativas_and(self):
        e = A & B & C & D
        e.remover_associativas()
        self.assertEqual(
            ExpressaoAnd(A, B, C, D),
            e
        )

    def test_remover_associativas_or(self):
        e = A | B | C | D
        e.remover_associativas()
        self.assertEqual(
            ExpressaoOr(A, B, C, D),
            e
        )

    def test_interiorizar_or_1(self):
        e = Expressao(A | (B & C))
        r = Expressao( (A | B) & (A | C) )
        e.remover_associativas()
        r.remover_associativas()
        e.interiorizar_or()
        self.assertEqual(e, r)

    def test_interiorizar_or_2(self):
        e = Expressao(A | (X & Y & Z))
        r = Expressao( (A | X) & (A | Y) & (A | Z) )
        e.remover_associativas()
        r.remover_associativas()
        e.interiorizar_or()
        self.assertEqual(e, r)

    def test_interiorizar_or_3(self):
        e = Expressao(A | B | (X & Y & Z) | C)
        r = Expressao( (A | B | X | C) & (A | B | Y | C) & (A | B | Z | C) )
        e.remover_associativas()
        r.remover_associativas()
        e.interiorizar_or()
        self.assertEqual(e, r)



    #################################################################
    # Testes de lista de símbolos

    def test_listar_simbolos_1(self):
        e = A & B & C
        self.assertEqual(
            set(['A', 'B', 'C']),
            e.simbolos()
        )

    def test_listar_simbolos_2(self):
        e = (A & B & C) | (~A & ~B & ~C) | (B & D)
        self.assertEqual(
            set(['A', 'B', 'C', 'D']),
            e.simbolos()
        )

    #################################################################
    # Testes de eval()

    def test_eval_simbolo(self):
        e = A
        for valor in (True, False, Verdadeiro, Falso):
            d = {"A": valor}
            self.assertEqual(e.eval(d), valor)

    def test_eval_parentese_1(self):
        e = Expressao(A)
        for valor in (True, False, Verdadeiro, Falso):
            d = {"A": valor}
            self.assertEqual(e.eval(d), valor)

    def test_eval_parentese_2(self):
        e = Expressao(Expressao(A))
        for valor in (True, False, Verdadeiro, Falso):
            d = {"A": valor}
            self.assertEqual(e.eval(d), valor)

    # TODO? Testar também com True/False, além de Verdadeiro/Falso
    def test_eval_not_1(self):
        e = ~A
        for valor in (Verdadeiro, Falso):
            d = {"A": valor}
            self.assertEqual(e.eval(d), ~ valor)

    def test_eval_not_2(self):
        e = ~A
        for valor, negacao in (
            #(True, False),
            #(False, True),
            (Verdadeiro, Falso),
            (Falso, Verdadeiro),
        ):
            d = {"A": valor}
            self.assertEqual(e.eval(d), negacao)

    def test_eval_parentese_not_parentese(self):
        e = Expressao(ExpressaoNot(Expressao(ExpressaoSimbolo("A"))))
        for valor, negacao in (
            #(True, False),
            #(False, True),
            (Verdadeiro, Falso),
            (Falso, Verdadeiro),
        ):
            d = {"A": valor}
            self.assertEqual(e.eval(d), negacao)

    def test_eval_and(self):
        e = A & B
        for valorA, valorB, resultado in (
            (Verdadeiro, Verdadeiro, Verdadeiro),
            (Verdadeiro, Falso     , Falso     ),
            (Falso     , Verdadeiro, Falso     ),
            (Falso     , Falso     , Falso     ),
        ):
            d = {"A": valorA, "B": valorB}
            self.assertEqual(e.eval(d), resultado)

    def test_eval_or(self):
        e = A | B
        for valorA, valorB, resultado in (
            (Verdadeiro, Verdadeiro, Verdadeiro),
            (Verdadeiro, Falso     , Verdadeiro),
            (Falso     , Verdadeiro, Verdadeiro),
            (Falso     , Falso     , Falso     ),
        ):
            d = {"A": valorA, "B": valorB}
            self.assertEqual(e.eval(d), resultado)

    def test_eval_implica(self):
        e = A > B
        for valorA, valorB, resultado in (
            (Verdadeiro, Verdadeiro, Verdadeiro),
            (Verdadeiro, Falso     , Falso     ),
            (Falso     , Verdadeiro, Verdadeiro),
            (Falso     , Falso     , Verdadeiro),
        ):
            d = {"A": valorA, "B": valorB}
            self.assertEqual(e.eval(d), resultado)



if __name__ == '__main__':
    unittest.main()
