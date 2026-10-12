import pytest

from app.confirmation import classify


@pytest.mark.parametrize("text", ["sí", "Si", "dale", "Confirmo", "hazlo", "Sí, hazlo", "¡Dale!", "ok"])
def test_yes_variants(text):
    assert classify(text) == "yes"


@pytest.mark.parametrize("text", ["no", "No.", "cancela", "Mejor no", "no gracias"])
def test_no_variants(text):
    assert classify(text) == "no"


@pytest.mark.parametrize("text", ["¿qué hora es?", "sí pero mañana", "nose", "", "dale al otro"])
def test_anything_else_is_other(text):
    assert classify(text) == "other"
