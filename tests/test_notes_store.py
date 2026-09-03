"""
Pruebas del almacenamiento de notas (jarvis/memory/notes_store.py).
"""

from jarvis.memory import notes_store


def test_list_notes_vacio_si_no_hay_archivo(tmp_path, monkeypatch):
    # tmp_path es una carpeta temporal que pytest crea y borra por prueba --
    # apuntamos NOTES_FILE ahí para no leer/escribir el data/notes.json real.
    monkeypatch.setattr(notes_store, "NOTES_FILE", tmp_path / "notes.json")

    assert notes_store.list_notes() == []


def test_add_note_y_list_notes_redondo(tmp_path, monkeypatch):
    monkeypatch.setattr(notes_store, "NOTES_FILE", tmp_path / "notes.json")

    notes_store.add_note("comprar leche")
    notas = notes_store.list_notes()

    assert len(notas) == 1
    assert notas[0]["texto"] == "comprar leche"
    assert "creada" in notas[0]


def test_add_note_conserva_notas_previas(tmp_path, monkeypatch):
    monkeypatch.setattr(notes_store, "NOTES_FILE", tmp_path / "notes.json")

    notes_store.add_note("primera")
    notes_store.add_note("segunda")

    textos = [n["texto"] for n in notes_store.list_notes()]
    assert textos == ["primera", "segunda"]


def test_delete_note_borra_la_nota_correcta(tmp_path, monkeypatch):
    monkeypatch.setattr(notes_store, "NOTES_FILE", tmp_path / "notes.json")
    notes_store.add_note("primera")
    notes_store.add_note("segunda")

    nota_borrada = notes_store.delete_note(1)

    assert nota_borrada["texto"] == "primera"
    textos = [n["texto"] for n in notes_store.list_notes()]
    assert textos == ["segunda"]


def test_delete_note_indice_invalido_no_borra_nada(tmp_path, monkeypatch):
    monkeypatch.setattr(notes_store, "NOTES_FILE", tmp_path / "notes.json")
    notes_store.add_note("única")

    resultado = notes_store.delete_note(99)

    assert resultado is None
    assert len(notes_store.list_notes()) == 1


def test_update_note_reemplaza_el_texto(tmp_path, monkeypatch):
    monkeypatch.setattr(notes_store, "NOTES_FILE", tmp_path / "notes.json")
    notes_store.add_note("comprar pan")

    nota_actualizada = notes_store.update_note(1, "comprar leche")

    assert nota_actualizada["texto"] == "comprar leche"
    assert "editada" in nota_actualizada
    assert notes_store.list_notes()[0]["texto"] == "comprar leche"


def test_update_note_conserva_fecha_de_creacion(tmp_path, monkeypatch):
    monkeypatch.setattr(notes_store, "NOTES_FILE", tmp_path / "notes.json")
    notes_store.add_note("comprar pan")
    creada_original = notes_store.list_notes()[0]["creada"]

    nota_actualizada = notes_store.update_note(1, "comprar leche")

    assert nota_actualizada["creada"] == creada_original


def test_update_note_indice_invalido_no_modifica_nada(tmp_path, monkeypatch):
    monkeypatch.setattr(notes_store, "NOTES_FILE", tmp_path / "notes.json")
    notes_store.add_note("única")

    resultado = notes_store.update_note(99, "texto nuevo")

    assert resultado is None
    assert notes_store.list_notes()[0]["texto"] == "única"
