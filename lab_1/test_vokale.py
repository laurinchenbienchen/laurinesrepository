# import pytest

from lab_1 import vokale


def test_1():
    assert vokale.vokale_zaehlen('hallo') is 2, "hat 2 vokale"


def test_2():
    assert vokale.vokale_zaehlen('fghkl') is 0, "hat keine vokale"

def test_3():
    assert vokale.vokale_zaehlen('AEIOU') is 5

