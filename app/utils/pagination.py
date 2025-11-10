"""Simple list paginator helper used by controllers to provide a pagination-like
object compatible with the templates' expectations.

This avoids adding a dependency on Flask-SQLAlchemy's Pagination everywhere
and provides the attributes that templates use: page, per_page, total, pages,
has_prev, has_next, prev_num, next_num and items.
"""
from math import ceil
from types import SimpleNamespace
from urllib.parse import urlencode


class SimplePagination:
    def __init__(self, page: int, per_page: int, total: int, items: list):
        self.page = max(1, int(page))
        self.per_page = max(1, int(per_page))
        self.total = int(total)
        self.items = items
        self.pages = int(ceil(self.total / float(self.per_page))) if self.per_page > 0 else 0
        # prev/next helpers expected by templates
        self.has_prev = self.page > 1
        self.has_next = self.page < self.pages
        self.prev_num = self.page - 1 if self.has_prev else None
        self.next_num = self.page + 1 if self.has_next else None


def paginate_list(all_items: list, page: int = 1, per_page: int = 20):
    """Paginate a plain list and return (paged_items, SimplePagination).

    all_items: the full sequence (list) of items
    page/per_page: ints, defensive conversion performed by callers
    """
    total = len(all_items)
    try:
        page = int(page)
    except Exception:
        page = 1
    try:
        per_page = int(per_page)
    except Exception:
        per_page = 20

    if per_page <= 0:
        per_page = 20
    if page <= 0:
        page = 1

    start = (page - 1) * per_page
    end = start + per_page
    items = all_items[start:end]
    pagination = SimplePagination(page=page, per_page=per_page, total=total, items=items)
    return items, pagination
