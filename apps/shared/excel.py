from __future__ import annotations

import io
from collections.abc import Iterable, Sequence
from typing import Any

from openpyxl import Workbook
from openpyxl.worksheet.worksheet import Worksheet


def build_workbook(
    sheets: Sequence[tuple[str, Sequence[str], Iterable[Sequence[Any]]]],
) -> Workbook:
    workbook = Workbook()
    # openpyxl creates a default sheet on construction. Every workbook we
    # produce has explicit, named sheets — remove the default.
    default_sheet = workbook.active
    workbook.remove(default_sheet)

    for name, headers, rows in sheets:
        worksheet: Worksheet = workbook.create_sheet(title=name)
        worksheet.append(list(headers))
        for row in rows:
            worksheet.append(list(row))

    return workbook


def workbook_to_bytes(workbook: Workbook) -> bytes:
    """Serialize a Workbook to in-memory bytes for HTTP responses."""
    buffer = io.BytesIO()
    workbook.save(buffer)
    return buffer.getvalue()
