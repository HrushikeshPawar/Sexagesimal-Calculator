from .sexagesimal import Sexagesimal


def test_IntegralModN():
    A = Sexagesimal('274.778')
    print(hasattr(A, 'S'))
    print(hasattr(A, 'Decimal2Sexagesimal'))
    print(hasattr(A, 'IntegralModN'))
    assert A.IntegralModN('274.778', 30).S == '09,04;46,40,48'


def test_Decimal2Sexagesimal():
    A = 1.23456
    assert Sexagesimal.Decimal2Sexagesimal(A, 2).S == "01;13,48"
