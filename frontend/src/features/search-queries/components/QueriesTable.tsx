export interface Query {
  id: number;
  name: string;
  created_at: string;
  updated_at: string;
  is_active: boolean;
  owner: string;
  deadline: string | null;
  results_count: number;
}

type SortDir = "asc" | "desc";

interface Props {
  items: Query[];
  sortBy: string;
  sortDir: SortDir;
  onSort: (key: string) => void;
  onEdit: (row: Query) => void;
  onDelete: (row: Query) => void;
  selected: Set<number>;
  onSelect: (id: number, checked: boolean) => void;
  onSelectAll: (checked: boolean) => void;
}

const fmt = (iso?: string | null): string => {
  if (!iso) return "—";
  const d = new Date(iso);

  return (
    d.toLocaleDateString("ru-RU", {
      day: "2-digit",
      month: "2-digit",
      year: "numeric",
    }) +
    " " +
    d.toLocaleTimeString("ru-RU", {
      hour: "2-digit",
      minute: "2-digit",
    })
  );
};

const fmtNum = (n: number): string => n.toLocaleString("ru-RU");

function isExpired(deadline?: string | null): boolean {
  if (!deadline) {
    return false;
  }

  function parseUTC(dateStr: string): Date {
    return new Date(dateStr.endsWith("Z") ? dateStr : dateStr + "Z");
  }

  const deadlineDate = parseUTC(deadline);
  const now = new Date();

  return deadlineDate < now;
}

interface SortIconProps {
  active: boolean;
  dir: SortDir;
}

const SortIcon: React.FC<SortIconProps> = ({ active, dir }) => (
  <span className={`sort-icon ${active ? "sort-icon--active" : ""}`}>
    {active ? (dir === "asc" ? "↑" : "↓") : "↕"}
  </span>
);

const COLUMNS: { key: keyof Query; label: string }[] = [
  { key: "name", label: "Название" },
  { key: "created_at", label: "Создан" },
  { key: "updated_at", label: "Изменён" },
  { key: "is_active", label: "Статус" },
  { key: "owner", label: "Владелец" },
  { key: "deadline", label: "Дедлайн" },
  { key: "results_count", label: "Результатов" },
];

const QueriesTable: React.FC<Props> = ({
  items,
  sortBy,
  sortDir,
  onSort,
  onEdit,
  onDelete,
  selected,
  onSelect,
  onSelectAll,
}) => {
  const allSelected =
    items.length > 0 && items.every((r) => selected.has(r.id));

  return (
    <div className="table-wrapper">
      <table className="queries-table">
        <thead>
          <tr>
            <th className="col-check">
              <input
                type="checkbox"
                checked={allSelected}
                onChange={(e: React.ChangeEvent<HTMLInputElement>) =>
                  onSelectAll(e.target.checked)
                }
                title="Выбрать всё на странице"
              />
            </th>

            {COLUMNS.map(({ key, label }) => (
              <th
                key={key}
                onClick={() => onSort(key as string)}
                className="sortable-th"
              >
                <span className="th-inner">
                  {label}
                  <SortIcon active={sortBy === key} dir={sortDir} />
                </span>
              </th>
            ))}

            <th className="col-actions">Действия</th>
          </tr>
        </thead>

        <tbody>
          {items.map((row) => {
            const expired = isExpired(row.deadline);

            return (
              <tr key={row.id} className={expired ? "row--expired" : ""}>
                <td className="col-check">
                  <input
                    type="checkbox"
                    checked={selected.has(row.id)}
                    onChange={(e: React.ChangeEvent<HTMLInputElement>) =>
                      onSelect(row.id, e.target.checked)
                    }
                  />
                </td>

                <td className="cell-name" title={row.name}>
                  {row.name}
                </td>

                <td className="cell-mono">{fmt(row.created_at)}</td>
                <td className="cell-mono">{fmt(row.updated_at)}</td>

                <td>
                  <span
                    className={`badge ${
                      row.is_active ? "badge--active" : "badge--inactive"
                    }`}
                  >
                    {row.is_active ? "Активен" : "Неактивен"}
                  </span>
                </td>

                <td className="cell-owner" title={row.owner}>
                  {row.owner}
                </td>

                <td className={`cell-mono ${expired ? "cell-expired" : ""}`}>
                  {expired && <span className="expired-marker">⚠ </span>}
                  {fmt(row.deadline)}
                </td>

                <td className="cell-mono cell-num">
                  {fmtNum(row.results_count)}
                </td>

                <td className="col-actions">
                  <button
                    className="btn-icon btn-icon--edit"
                    title="Редактировать"
                    onClick={() => onEdit(row)}
                  >
                    <svg
                      width="12px"
                      height="12px"
                      viewBox="0 0 24 24"
                      fill="none"
                      xmlns="http://www.w3.org/2000/svg"
                    >
                      <path
                        fillRule="evenodd"
                        clipRule="evenodd"
                        d="M16.2929 2.29289C17.6834 0.902369 19.9383 0.902369 21.3288 2.29289C22.7193 3.68342 22.7193 5.93827 21.3288 7.3288L8.70711 19.9505C8.31658 20.341 7.81618 20.6071 7.27164 20.7143L3.85355 21.3536C2.96252 21.5206 2.17936 20.7375 2.3464 19.8464L2.9857 16.4284C3.09286 15.8838 3.35896 15.3834 3.74949 14.9929L16.2929 2.29289ZM19.9146 3.70711C19.3041 3.09662 18.3176 3.09662 17.7071 3.70711L16.4142 5L18.9999 7.58579L20.2929 6.29289C20.9034 5.68241 20.9034 4.6959 20.2929 4.08541L19.9146 3.70711ZM17.5857 9L15 6.41421L5.1637 16.2505C5.0241 16.3901 4.92895 16.5679 4.89023 16.7615L4.50006 18.9L6.63857 18.5098C6.83215 18.4711 7.00996 18.376 7.14956 18.2364L17.5857 9Z"
                        fill="currentColor"
                      />
                    </svg>
                  </button>
                  <button
                    className="btn-icon btn-icon--delete"
                    title="Удалить"
                    onClick={() => onDelete(row)}
                  >
                    <svg
                      width="12px"
                      height="12px"
                      viewBox="0 0 24 24"
                      fill="none"
                      xmlns="http://www.w3.org/2000/svg"
                    >
                      <path
                        fillRule="evenodd"
                        clipRule="evenodd"
                        d="M9 3C8.44772 3 8 3.44772 8 4V5H5C4.44772 5 4 5.44772 4 6C4 6.55228 4.44772 7 5 7H19C19.5523 7 20 6.55228 20 6C20 5.44772 19.5523 5 19 5H16V4C16 3.44772 15.5523 3 15 3H9ZM10 5V5H14V5H10ZM6 9C6 8.44772 6.44772 8 7 8H17C17.5523 8 18 8.44772 18 9V19C18 20.1046 17.1046 21 16 21H8C6.89543 21 6 20.1046 6 19V9ZM9 11C9.55228 11 10 11.4477 10 12V17C10 17.5523 9.55228 18 9 18C8.44772 18 8 17.5523 8 17V12C8 11.4477 8.44772 11 9 11ZM15 11C15.5523 11 16 11.4477 16 12V17C16 17.5523 15.5523 18 15 18C14.4477 18 14 17.5523 14 17V12C14 11.4477 14.4477 11 15 11Z"
                        fill="currentColor"
                      />
                    </svg>
                  </button>
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
};

export default QueriesTable;
