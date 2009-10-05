#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vi:ts=4 sw=4 et foldmethod=indent foldlevel=1

import unittest
import string
import sys
from logica import *

# Este arquivo executa dois tipos de teste:
# * testes unitários, usando o módulo 'unittest'
# * testes de documentação, usando o módulo 'doctest'


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
            ~ A ,
            ExpressaoNot(A)
        )

    def test_operador_not_duplicado(self):
        self.assertEqual(
            ~ ~ A ,
            ExpressaoNot(ExpressaoNot(A))
        )

    def test_operador_and(self):
        self.assertEqual(
            A & B ,
            ExpressaoAnd(A, B)
        )

    def test_operador_or(self):
        self.assertEqual(
            A | B ,
            ExpressaoOr(A, B)
        )

    def test_operador_implica(self):
        self.assertEqual(
            A > B ,
            ExpressaoOr(ExpressaoNot(A), B)
        )

    def test_precedencia_and_not(self):
        self.assertEqual(
            ~A & ~B ,
            ExpressaoAnd(ExpressaoNot(A), ExpressaoNot(B))
        )

    def test_precedencia_or_not(self):
        self.assertEqual(
            ~A | ~B ,
            ExpressaoOr(ExpressaoNot(A), ExpressaoNot(B))
        )

    def test_precedencia_implica_not(self):
        self.assertEqual(
            ~A > ~B ,
            ExpressaoOr(ExpressaoNot(ExpressaoNot(A)), ExpressaoNot(B))
        )

    #################################################################
    # Testes de comparações

    def test_comparar_ignorando_ordem(self):
        expressoes = (
            (
                A,
                A,
                True,  # ==
                True,  # .comparar_ignorando_ordem()
            ),
            (
                A,
                B,
                False,
                False,
            ),
            (
                A,
                ~ A,
                False,
                False,
            ),
            (
                A & B,
                A & B,
                True,
                True,
            ),
            (
                A | B,
                A | B,
                True,
                True,
            ),
            (
                A & B,
                B & A,
                False,
                True,
            ),
            (
                A | B,
                B | A,
                False,
                True,
            ),
            (
                A & (C | B),
                A & (B | C),
                False,
                True,
            ),
            (
                (C | B) & A,
                A & (B | C),
                False,
                True,
            ),
            (
                (A & B) | (C & D),
                (A & B) | (C & D),
                True,
                True,
            ),
            (
                (B & A) | (D & C),
                (A & B) | (C & D),
                False,
                True,
            ),
            (
                (B & A) | (D & C),
                (C & D) | (A & B),
                False,
                True,
            ),
            (
                A > B,
                ~ A | B,
                True,
                True,
            ),
            (
                A > B,
                B | ~ A,
                False,
                True,
            ),
            (
                A & B & C & D,
                A & B & C & D,
                True,
                True,
            ),
            (
                A & B & C & D,
                A & D & B & C,
                False,
                True,
            ),
            (
                A & B & C & D,
                D & C & B & A,
                False,
                True,
            ),
            (
                A | B | C | D,
                A | B | C | D,
                True,
                True,
            ),
            (
                A | B | C | D,
                A | D | B | C,
                False,
                True,
            ),
            (
                A | B | C | D,
                D | C | B | A,
                False,
                True,
            ),
        )
        for e, f, equal, comparacao in expressoes:
            e.remover_associativas()
            f.remover_associativas()
            e.generate_sort_keys()
            f.generate_sort_keys()
            self.assertEqual(e == f, equal, "%s == %s  ==>  %s" % (str(e), str(f), not equal))
            self.assertEqual(e.comparar_ignorando_ordem(f), comparacao, "%s .comparar_ignorando_ordem( %s )  ==>  return '%s' == '%s'" % (str(e), str(f), e.sort_key, f.sort_key))

    #################################################################
    # Testes de manipulações
    #
    # Muitos dos testes abaixos exigem que a expressão seja
    # encapsulada num parêntese, usando Expressao(). Isto é
    # necessário porque a maioria das manipulações consegue
    # operar apenas nos filhos.

    def test_remover_dupla_negacao(self):
        expressoes = (
            (
                ~ A,
                ~ A
            ),
            (
                ~ ~ A,
                A
            ),
            (
                ~ ~ ~ A,
                ~ A
            ),
            (
                ~ ~ ~ ~ A,
                A
            ),
            (
                ~ ~ ~ ~ ~ A,
                ~ A
            ),
            (
                ~ ~ ~ ~ ~ ~ A,
                A
            ),
        )
        for antes, depois in expressoes:
            e = Expressao(antes)
            r = Expressao(depois)
            e.remover_duplas_negacoes()
            self.assertEqual(e, r)

    def test_remover_dupla_negacao_e_associativa_nao_1(self):
        e = Expressao(A & ~ ~ (B & C))
        r = Expressao(ExpressaoAnd(A, ExpressaoAnd(B, C)))
        e.remover_duplas_negacoes(auto_remover_associativas=False)
        self.assertEqual(e, r)

    def test_remover_dupla_negacao_e_associativa_sim_1(self):
        e = Expressao(A & ~ ~ (B & C))
        r = Expressao(ExpressaoAnd(A, B, C))
        e.remover_duplas_negacoes(auto_remover_associativas=True)
        self.assertEqual(e, r)

    def test_remover_dupla_negacao_e_associativa_nao_2(self):
        e = Expressao(A | ~ ~ (B | C))
        r = Expressao(ExpressaoOr(A, ExpressaoOr(B, C)))
        e.remover_duplas_negacoes(auto_remover_associativas=False)
        self.assertEqual(e, r)

    def test_remover_dupla_negacao_e_associativa_sim_2(self):
        e = Expressao(A | ~ ~ (B | C))
        r = Expressao(ExpressaoOr(A, B, C))
        e.remover_duplas_negacoes(auto_remover_associativas=True)
        self.assertEqual(e, r)

    def test_demorgan_and(self):
        e = Expressao(~(A & B))
        r = Expressao(ExpressaoOr(ExpressaoNot(A), ExpressaoNot(B)))
        e.interiorizar_negacao()
        self.assertEqual(e, r)

    def test_demorgan_or(self):
        e = Expressao(~ (A | B))
        r = Expressao(ExpressaoAnd(ExpressaoNot(A), ExpressaoNot(B)))
        e.interiorizar_negacao()
        self.assertEqual(e, r)

    def test_demorgan_and_remover_dupla_negacao(self):
        e = Expressao(~ (~A & ~B))
        r = Expressao(ExpressaoOr(A, B))
        e.interiorizar_negacao()
        self.assertEqual(e, r)

    def test_demorgan_or_remover_dupla_negacao(self):
        e = Expressao(~ (~A | ~B))
        r = Expressao(ExpressaoAnd(A, B))
        e.interiorizar_negacao()
        self.assertEqual(e, r)

    def test_demorgan_remover_dupla_negacao_1(self):
        e = Expressao(~(~ ~ A & ~ ~ (~B & C)))
        r = Expressao(~ A | (B | ~ C))
        e.interiorizar_negacao()
        self.assertEqual(e, r)

    def test_demorgan_remover_dupla_negacao_2(self):
        e = Expressao(~(~ ~ ~ A & ~ ~ (~B & C)))
        r = Expressao(A | (B | ~ C))
        e.interiorizar_negacao()
        self.assertEqual(e, r)

    def test_demorgan_remover_dupla_negacao_3(self):
        """Ao executar .interiorizar_negacao(), a remoção automática da dupla negação deve acontecer de forma não recursiva."""
        e = Expressao(~(~ A & ~ ~ B & ~ ~ ~ C) & ~ ~ D)
        r = Expressao((A | ~ B | C) & ~ ~ D)
        e.interiorizar_negacao()
        self.assertEqual(e, r)

    def test_demorgan_remover_dupla_negacao_4(self):
        """Ao executar .interiorizar_negacao(), a remoção automática da dupla negação deve acontecer de forma não recursiva."""
        e = Expressao(~(~ A & ~ (B | ~ ~ ~ C)) )
        r = Expressao(A | (B | ~ ~ ~ C) )
        e.interiorizar_negacao()
        self.assertEqual(e, r)

    def test_remover_associativas_and(self):
        e = A & B & C & D
        r = ExpressaoAnd(A, B, C, D)
        e.remover_associativas()
        self.assertEqual(e, r)

    def test_remover_associativas_or(self):
        e = A | B | C | D
        r = ExpressaoOr(A, B, C, D)
        e.remover_associativas()
        self.assertEqual(e, r)

    def test_interiorizar_or_1(self):
        e = Expressao(A | (B & C))
        r = Expressao( (A | B) & (A | C) )
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

    def test_interiorizar_or_4(self):
        e = Expressao( (A & B) | (C & D) )
        r1 = Expressao( ((A | C) & (A | D)) & ((B | C) & (B | D)) )
        r2 = Expressao( ((A | C) & (A | D)) & ((B | C) & (B | D)) )
        r2.remover_associativas()
        e.interiorizar_or()
        self.assertTrue(e == r1 or e == r2)

    def test_interiorizar_or_5(self):
        e = Expressao( (A & (X | Y)) | (C & (J | K)) )
        r1 = Expressao(((A | C) & (A | (J | K))) & (((X | Y) | C) & ((X | Y) | (J | K))))
        r2 = Expressao(((A | C) & (A | (J | K))) & (((X | Y) | C) & ((X | Y) | (J | K))))
        r2.remover_associativas()
        e.interiorizar_or()
        self.assertTrue(e == r1 or e == r2)

    def test_interiorizar_or_6(self):
        e = Expressao( (A & B & C) | (D & E & F) )
        r = Expressao( (A | D) & (A | E) & (A | F) & (B | D) & (B | E) & (B | F) & (C | D) & (C | E) & (C | F) )
        r.remover_associativas()
        e.interiorizar_or()
        e.remover_associativas()
        self.assertEqual(e, r)

    def test_interiorizar_or_7(self):
        e = Expressao( A | B | (X & (J | K) & Y) | C )
        r1 = Expressao( ExpressaoAnd( ExpressaoOr(A, B, X, C), ExpressaoOr(A, B, (J | K), C), ExpressaoOr(A, B, Y, C) ) )
        r2 = Expressao( ExpressaoAnd( ExpressaoOr(A, B, X, C), ExpressaoOr(A, B, (J | K), C), ExpressaoOr(A, B, Y, C) ) )
        e.remover_associativas()
        r2.remover_associativas()
        e.interiorizar_or()
        self.assertTrue(e == r1 or e == r2)

    def test_transformar_em_forma_normal_conjuntiva(self):
        expressoes = (
            (
                A ,
                A
            ),
            (
                ~ A ,
                ~ A
            ),
            (
                ~ ~ A ,
                A
            ),
            (
                ~ ~ A | B | C ,
                A | B | C
            ),
            (
                ~ ~ (A | B | C) ,
                A | B | C
            ),
            (
                A & B & C ,
                A & B & C
            ),
            (
                ~ (A | B | C) ,
                ~A & ~B & ~C
            ),
            (
                ~ (A & B & C) ,
                ~A | ~B | ~C
            ),
            (
                A & ~ ~ (B & C) ,
                A & B & C
            ),
            (
                A | ~ ~ (B | C) ,
                A | B | C
            ),
            (
                ~(~ ~ A & ~ ~ (~B & C)) ,
                ~ A | B | ~ C
            ),
            (
                ~(~ ~ ~ A & ~ ~ (~B & C)) ,
                A | B | ~ C
            ),
            (
                ~(~ A & ~ ~ B & ~ ~ ~ C) & ~ ~ D ,
                (A | ~ B | C) & D
            ),
            (
                ~(~ A & ~ (B | ~ ~ ~ C)) ,
                A | B | ~ C
            ),
            (
                (A | B) & (C | D) ,
                (A | B) & (C | D)
            ),
            (
                A | (X & Y & Z) ,
                (A | X) & (A | Y) & (A | Z)
            ),
            (
                A | B | (X & Y & Z) | C ,
                (A | B | X | C) & (A | B | Y | C) & (A | B | Z | C)
            ),
            (
                (A & B) | (C & D) ,
                (A | C) & (A | D) & (B | C) & (B | D)
            ),
            (
                (A & (X | Y)) | (C & (J | K)) ,
                (A | C) & (A | J | K) & (X | Y | C) & (X | Y | J | K)
            ),
            (
                (A & B & C) | (D & E & F) ,
                (A | D) & (A | E) & (A | F) & (B | D) & (B | E) & (B | F) & (C | D) & (C | E) & (C | F) 
            ),
            (
                A | B | (X & (J | K) & Y) | C ,
                (A | B | X | C) & (A | B | J | K | C) & (A | B | Y | C)
            ),
            (  # Fórmula do XOR
                (A | B) & ~(A & B) ,
                (A | B) & (~A | ~B)
            ),
        )
        for antes, depois in expressoes:
            e = Expressao(antes)
            r = Expressao(depois)
            r.remover_associativas()
            e.transformar_em_forma_normal_conjuntiva()
            self.assertEqual(e, r)

    def test_remover_operacoes_vazias(self):
        expressoes = (
            Expressao(ExpressaoAnd()),
            Expressao(ExpressaoOr()),
            Expressao(ExpressaoNot(ExpressaoAnd())),
            Expressao(ExpressaoNot(ExpressaoOr())),
            Expressao(ExpressaoNot(ExpressaoNot(ExpressaoAnd()))),
            Expressao(ExpressaoNot(ExpressaoNot(ExpressaoOr()))),
            Expressao(ExpressaoNot(ExpressaoNot(ExpressaoNot(ExpressaoAnd())))),
            Expressao(ExpressaoNot(ExpressaoNot(ExpressaoNot(ExpressaoOr())))),
            Expressao(ExpressaoNot(Expressao(ExpressaoNot(ExpressaoAnd())))),
            Expressao(ExpressaoNot(Expressao(ExpressaoNot(ExpressaoOr())))),
            Expressao(Expressao(Expressao(Expressao(ExpressaoAnd())))),
            Expressao(Expressao(Expressao(Expressao(ExpressaoOr())))),
            Expressao(ExpressaoAnd(ExpressaoAnd(),ExpressaoAnd())),
            Expressao(ExpressaoOr(ExpressaoAnd(),ExpressaoAnd())),
            Expressao(ExpressaoAnd(ExpressaoOr(),ExpressaoOr())),
            Expressao(ExpressaoOr(ExpressaoOr(),ExpressaoOr())),
            Expressao(ExpressaoAnd(ExpressaoAnd(),ExpressaoOr())),
            Expressao(ExpressaoOr(ExpressaoAnd(),ExpressaoOr())),
            Expressao(ExpressaoAnd(ExpressaoOr(),ExpressaoAnd())),
            Expressao(ExpressaoOr(ExpressaoOr(),ExpressaoAnd())),
            Expressao(ExpressaoAnd(ExpressaoAnd(Expressao(ExpressaoOr())),ExpressaoAnd(ExpressaoNot(ExpressaoOr())))),
        )
        for antes in expressoes:
            e = antes
            r = Expressao(A)
            r.children = []
            e.remover_operacoes_vazias()
            self.assertEqual(e, r)

# TODO:
#  * Testar transformar_em_forma_normal_conjuntiva() com expressões com
#    operador implica.
#  * Criar funcao "remover tautologias" e "remover contradicoes"
#  * Criar algum tipo de integração entre as classes Formula e Expressao.
#  * Possível expressão para usar em testes:
#    Manipular XOR: (~A & B) | (A & ~B)  <==> (A | B) & ~(A & B)


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
        for valor in (Verdadeiro, Falso):
            d = {"A": valor}
            self.assertEqual(e.eval(d), valor)

    def test_eval_parentese_1(self):
        e = Expressao(A)
        for valor in (Verdadeiro, Falso):
            d = {"A": valor}
            self.assertEqual(e.eval(d), valor)

    def test_eval_parentese_2(self):
        e = Expressao(Expressao(A))
        for valor in (Verdadeiro, Falso):
            d = {"A": valor}
            self.assertEqual(e.eval(d), valor)

    def test_eval_not_1(self):
        e = ~A
        for valor in (Verdadeiro, Falso):
            d = {"A": valor}
            self.assertEqual(e.eval(d), ~ valor)

    def test_eval_not_2(self):
        e = ~A
        for valor, negacao in (
            (Verdadeiro, Falso),
            (Falso, Verdadeiro),
        ):
            d = {"A": valor}
            self.assertEqual(e.eval(d), negacao)

    def test_eval_parentese_not_parentese(self):
        e = Expressao(ExpressaoNot(Expressao(ExpressaoSimbolo("A"))))
        for valor, negacao in (
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





class TestarExpressoesTrueFalse(unittest.TestCase):
    """Esta classe contém apenas testes não críticos"""

    def setUp(self):
        # Ugly... Writing to globals()...
        # But it is damn handy! :)
        criar_simbolos_no_namespace(string.uppercase, globals())

    def tearDown(self):
        for i in string.uppercase:
            del globals()[i]

    def test_eval_simbolo(self):
        e = A
        for valor in (True, False):
            d = {"A": valor}
            self.assertEqual(e.eval(d), valor)

    def test_eval_parentese_1(self):
        e = Expressao(A)
        for valor in (True, False):
            d = {"A": valor}
            self.assertEqual(e.eval(d), valor)

    def test_eval_parentese_2(self):
        e = Expressao(Expressao(A))
        for valor in (True, False):
            d = {"A": valor}
            self.assertEqual(e.eval(d), valor)

    def test_eval_not(self):
        e = ~A
        for valor, negacao in (
            (True, False),
            (False, True),
        ):
            d = {"A": valor}
            self.assertEqual(e.eval(d), negacao)

    def test_eval_parentese_not_parentese(self):
        e = Expressao(ExpressaoNot(Expressao(ExpressaoSimbolo("A"))))
        for valor, negacao in (
            (True, False),
            (False, True),
        ):
            d = {"A": valor}
            self.assertEqual(e.eval(d), negacao)
            d = {"A": valorA, "B": valorB}
            self.assertEqual(e.eval(d), resultado)



class _TerseTextTestResult(unittest._TextTestResult):
    def printErrorList(self, flavour, errors):
        for test, err in errors:
            #self.stream.writeln(self.separator1)
            self.stream.writeln("%s: %s" % (flavour,self.getDescription(test)))
            #self.stream.writeln(self.separator2)
            #self.stream.writeln("%s" % err)


class TerseTextTestRunner(unittest.TextTestRunner):
    def _makeResult(self):
        return _TerseTextTestResult(self.stream, self.descriptions, self.verbosity)



if __name__ == '__main__':
    #unittest.main()

    testar_bool = False
    if testar_bool:
        sys.stderr.write("Running non-critical tests:\n")
        non_critical_suite = unittest.TestLoader().loadTestsFromTestCase(TestarExpressoesTrueFalse)
        TerseTextTestRunner(verbosity=1).run(non_critical_suite)
        #unittest.TextTestRunner(verbosity=1).run(non_critical_suite)

        sys.stderr.write("\n")

    sys.stderr.write("Running CRITICAL tests:\n")
    suite = unittest.TestLoader().loadTestsFromTestCase(TestarExpressoes)
    unittest.TextTestRunner(verbosity=1).run(suite)

    # Also running doctest:
    import doctest
    import logica
    doctest.testmod(logica)
