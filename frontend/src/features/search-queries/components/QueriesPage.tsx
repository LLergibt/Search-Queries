import { useState, useCallback } from "react";
import { useQueries } from "../hooks/useQueries";
import QueriesTable from "./QueriesTable";
import QueryModal from "./QueryModal";
import Pagination from "../../../shared/ui/Pagination";
import type {
  Query,
  CreateQueryPayload,
  UpdateQueryPayload,
} from "../api/queriesApi";

export default function QueriesPage(): JSX.Element {
  const {
    data,
    loading,
    error,
    params,
    setPage,
    setSort,
    setPageSize,
    createQuery,
    updateQuery,
    deleteQuery,
    bulkDelete,
  } = useQueries();

  const [selected, setSelected] = useState<Set<number>>(new Set());
  const [editRow, setEditRow] = useState<Query | null>(null);
  const [showCreate, setShowCreate] = useState<boolean>(false);
  const [confirmRow, setConfirmRow] = useState<Query | null>(null);

  const handleSelect = useCallback((id: number, checked: boolean): void => {
    setSelected((prev) => {
      const next = new Set(prev);
      checked ? next.add(id) : next.delete(id);
      return next;
    });
  }, []);

  const handleSelectAll = useCallback(
    (checked: boolean): void => {
      if (!data) return;
      setSelected(checked ? new Set(data.items.map((r) => r.id)) : new Set());
    },
    [data],
  );

  const handleCreate = async (formData: CreateQueryPayload): Promise<void> => {
    await createQuery(formData);
    setShowCreate(false);
  };

  const handleUpdate = async (formData: UpdateQueryPayload): Promise<void> => {
    if (!editRow) return;
    await updateQuery(editRow.id, formData);
    setEditRow(null);
  };

  const handleDeleteConfirmed = async (): Promise<void> => {
    if (!confirmRow) return;
    await deleteQuery(confirmRow.id);
    setConfirmRow(null);

    setSelected((prev) => {
      const n = new Set(prev);
      n.delete(confirmRow.id);
      return n;
    });
  };

  const handleBulkDelete = async (): Promise<void> => {
    if (!selected.size) return;
    if (!window.confirm(`Удалить ${selected.size} запросов?`)) return;

    await bulkDelete([...selected]);
    setSelected(new Set());
  };

  return (
    <div className="page">
      <header className="page-header">
        <div className="page-title">
          {data && (
            <span className="page-title__count">
              {data.total.toLocaleString("ru-RU")}
            </span>
          )}
        </div>

        <div className="toolbar">
          {selected.size > 0 && (
            <button className="btn btn-danger" onClick={handleBulkDelete}>
              Удалить выбранные ({selected.size})
              <svg
                width="12px"
                height="12px"
                viewBox="0 0 24 24"
                fill="none"
                xmlns="http://www.w3.org/2000/svg"
              >
                <path
                  fill-rule="evenodd"
                  clip-rule="evenodd"
                  d="M20.8477 1.87868C19.6761 0.707109 17.7766 0.707105 16.605 1.87868L2.44744 16.0363C2.02864 16.4551 1.74317 16.9885 1.62702 17.5692L1.03995 20.5046C0.760062 21.904 1.9939 23.1379 3.39334 22.858L6.32868 22.2709C6.90945 22.1548 7.44285 21.8693 7.86165 21.4505L22.0192 7.29289C23.1908 6.12132 23.1908 4.22183 22.0192 3.05025L20.8477 1.87868ZM18.0192 3.29289C18.4098 2.90237 19.0429 2.90237 19.4335 3.29289L20.605 4.46447C20.9956 4.85499 20.9956 5.48815 20.605 5.87868L17.9334 8.55027L15.3477 5.96448L18.0192 3.29289ZM13.9334 7.3787L3.86165 17.4505C3.72205 17.5901 3.6269 17.7679 3.58818 17.9615L3.00111 20.8968L5.93645 20.3097C6.13004 20.271 6.30784 20.1759 6.44744 20.0363L16.5192 9.96448L13.9334 7.3787Z"
                  fill="#0F0F0F"
                />
              </svg>
            </button>
          )}
          <button
            className="btn btn-primary"
            onClick={() => setShowCreate(true)}
          >
            + Новый запрос
          </button>
        </div>
      </header>

      {error && <div className="error-banner">Ошибка загрузки: {error}</div>}

      <div className="table-container">
        {loading && <div className="loading-overlay">Загрузка…</div>}

        {data && (
          <QueriesTable
            items={data.items}
            sortBy={params.sortBy}
            sortDir={params.sortDir}
            onSort={setSort}
            onEdit={setEditRow}
            onDelete={setConfirmRow}
            selected={selected}
            onSelect={handleSelect}
            onSelectAll={handleSelectAll}
          />
        )}
      </div>

      {data && (
        <footer className="page-footer">
          <div className="page-size-selector">
            <label>Строк на странице:</label>
            <select
              value={params.pageSize}
              onChange={(e) => setPageSize(Number(e.target.value))}
            >
              {[10, 25, 50, 100, 200].map((n) => (
                <option key={n} value={n}>
                  {n}
                </option>
              ))}
            </select>
          </div>

          <Pagination
            page={data.page}
            totalPages={data.total_pages}
            onPage={setPage}
          />

          <span className="pagination-info">
            {((data.page - 1) * data.page_size + 1).toLocaleString("ru-RU")}–
            {Math.min(data.page * data.page_size, data.total).toLocaleString(
              "ru-RU",
            )}{" "}
            из {data.total.toLocaleString("ru-RU")}
          </span>
        </footer>
      )}

      {showCreate && (
        <QueryModal
          onSave={handleCreate}
          onClose={() => setShowCreate(false)}
        />
      )}

      {editRow && (
        <QueryModal
          query={editRow}
          onSave={handleUpdate}
          onClose={() => setEditRow(null)}
        />
      )}

      {confirmRow && (
        <div className="confirm-overlay" onClick={() => setConfirmRow(null)}>
          <div
            className="confirm-box"
            onClick={(e: React.MouseEvent) => e.stopPropagation()}
          >
            <p>
              {console.log(confirmRow)}
              Удалить запрос{" "}
              <strong className="confirm-delete">«{confirmRow.name}»</strong>?
            </p>
            <div className="modal-actions">
              <button
                className="btn btn-ghost"
                onClick={() => setConfirmRow(null)}
              >
                Отмена
              </button>
              <button
                className="btn btn-danger"
                onClick={handleDeleteConfirmed}
              >
                Удалить
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
