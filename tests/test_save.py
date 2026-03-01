import tempfile
import pytest

from xsection._benchmarks import load_shape

def test_save():
    shape = load_shape(1)
    with tempfile.NamedTemporaryFile(suffix=".json", mode="w+", encoding="utf-8") as tmp:
        shape.save(tmp)
        tmp.flush()
        tmp.seek(0)
        shape2 = type(shape).load(tmp)

    

