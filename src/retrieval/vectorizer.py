from __future__ import annotations

import hashlib
from typing import Iterable


def text_to_vector(text: str, dim: int = 8) -> list[float]:
    """Convierte o texto em um vetor determinístico de dimensão `dim`."""
    normalized = text.strip() or "empty"
    data = hashlib.sha256(normalized.encode("utf-8")).digest()
    vector: list[float] = []
    length = len(data)
    for i in range(dim):
        idx = (i * 2) % length
        byte1 = data[idx]
        byte2 = data[(idx + 1) % length]
        value = (byte1 << 8) + byte2
        vector.append((value / 65535.0) * 2 - 1)
    return vector
