from __future__ import annotations

from typing import Generic, TypeVar
from fastapi import Query
from fastapi_pagination.bases import AbstractParams, RawParams, AbstractPage
from fastapi_pagination.customization import CustomizedPage, UseFieldsAliases
from pydantic import BaseModel, Field

from schemas import MovieDetailSchema

T = TypeVar("T")


class Params(BaseModel, AbstractParams):
    page: int = Query(1, ge=1, description="Page number")
    per_page: int = Query(10, ge=1, le=20, description="Page size")

    def to_raw_params(self) -> RawParams:
        return RawParams(
            limit=self.per_page if self.per_page is not None else None,
            offset=self.per_page * (self.page - 1)
            if self.page is not None and self.per_page is not None
            else None,
        )


class Page(AbstractPage[T], Generic[T]):
    results: list[T]
    total_items: int
    total_pages: int
    next_page: str | None = Field(
        default=None, examples=["/url_path/?page=1&per_page=10"]
    )
    prev_page: str | None = Field(
        default=None, examples=["/url_path/?page=3&per_page=10"]
    )

    __params_type__ = Params

    @classmethod
    def create(
        cls,
        items: list[T],
        params: Params,
        *,
        total: int | None = None,
        url: str | None = None,
        results_field: str = "results",
        **kwargs: dict,
    ) -> Page[T]:
        assert total is not None, "total_items must be provided"
        assert url is not None, "url must be provided"

        total_pages = (total + params.per_page - 1) // params.per_page

        return cls(
            results=items,
            total_items=total,
            total_pages=(total + params.per_page - 1) // params.per_page,
            next_page=f"{url}?page={params.page + 1}&per_page={params.per_page}"
            if params.page < total_pages
            else None,
            prev_page=f"{url}?page={params.page - 1}&per_page={params.per_page}"
            if params.page > 1
            else None,
        )


Page = CustomizedPage[
    Page[MovieDetailSchema],
    UseFieldsAliases(results="movies"),
]
