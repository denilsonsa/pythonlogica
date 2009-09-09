#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vi:ts=4 sw=4 et foldmethod=indent

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


if __name__ == '__main__':
    unittest.main()
