from collections import defaultdict
from typing import Any

from fastapi import HTTPException

from app.core.schemas import DetailScheme


def build_responses(*exceptions: HTTPException) -> dict[int | str, Any]:
    grouped: dict[int, list[HTTPException]] = defaultdict(list)
    for exc in exceptions:
        grouped[exc.status_code].append(exc)

    responses: dict[int | str, Any] = {}
    for code, errs in grouped.items():
        if len(errs) == 1:
            e = errs[0]
            responses[code] = {
                "description": e.detail,
                "model": DetailScheme,
                "content": {"application/json": {"example": {"detail": e.detail}}},
            }
        else:
            examples = {}
            for err in errs:
                examples[err.detail] = {
                    "summary": err.detail,
                    "value": {"detail": err.detail},
                }
            responses[code] = {
                "description": errs[0].detail,
                "model": DetailScheme,
                "content": {"application/json": {"examples": examples}},
            }

    return responses
