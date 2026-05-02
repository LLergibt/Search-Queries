import React from "react";

type PaginationProps = {
  page: number;
  totalPages: number;
  onPage: (page: number) => void;
};

export default function Pagination({
  page,
  totalPages,
  onPage,
}: PaginationProps) {
  if (totalPages <= 1) return null;

  const windowSize = 2;
  const pages: (number | string)[] = [];

  const start = Math.max(1, page - windowSize);
  const end = Math.min(totalPages, page + windowSize);

  if (start > 1) pages.push(1);
  if (start > 2) pages.push("…");

  for (let p = start; p <= end; p++) pages.push(p);

  if (end < totalPages - 1) pages.push("…");
  if (end < totalPages) pages.push(totalPages);

  return (
    <nav className="pagination">
      <button
        className="page-btn"
        disabled={page === 1}
        onClick={() => onPage(1)}
        title="Первая"
      >
        «
      </button>

      <button
        className="page-btn"
        disabled={page === 1}
        onClick={() => onPage(page - 1)}
        title="Предыдущая"
      >
        ‹
      </button>

      {pages.map((p, i) =>
        p === "…" ? (
          <span key={`ellipsis-${i}`} className="page-ellipsis">
            …
          </span>
        ) : (
          <button
            key={p}
            className={`page-btn ${p === page ? "page-btn--active" : ""}`}
            onClick={() => onPage(p)}
          >
            {p}
          </button>
        )
      )}

      <button
        className="page-btn"
        disabled={page === totalPages}
        onClick={() => onPage(page + 1)}
        title="Следующая"
      >
        ›
      </button>

      <button
        className="page-btn"
        disabled={page === totalPages}
        onClick={() => onPage(totalPages)}
        title="Последняя"
      >
        »
      </button>
    </nav>
  );
}
