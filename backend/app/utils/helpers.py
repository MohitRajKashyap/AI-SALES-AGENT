from typing import TypeVar, Generic, List, Any
from math import ceil

T = TypeVar("T")


def paginate(items: List[Any], page: int, page_size: int) -> dict:
    total = len(items)
    pages = ceil(total / page_size) if total > 0 else 1
    start = (page - 1) * page_size
    end = start + page_size
    return {
        "items": items[start:end],
        "total": total,
        "page": page,
        "page_size": page_size,
        "pages": pages,
    }


def clamp(value: int, min_val: int, max_val: int) -> int:
    return max(min_val, min(max_val, value))


def truncate(text: str, max_length: int = 200) -> str:
    if len(text) <= max_length:
        return text
    return text[:max_length - 3] + "..."
