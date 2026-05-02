const BASE = "http://localhost:8000/api";

const headers: HeadersInit = {
  "Content-Type": "application/json",
};

const json = async <T>(r: Response): Promise<T> => {
  if (!r.ok) {
    throw new Error(`HTTP ${r.status}`);
  }
  return r.status === 204 ? (null as T) : r.json();
};


export interface Query {
  id: number;
  text: string;
  createdAt: string;
}

export interface FetchQueriesParams {
  page: number;
  pageSize: number;
  sortBy?: string;
  sortDir?: "asc" | "desc";
}

export interface FetchQueriesResponse {
  data: Query[];
  total: number;
}

export interface CreateQueryPayload {
  text: string;
}

export type UpdateQueryPayload = Partial<CreateQueryPayload>;

/* ===== API ===== */

export const fetchQueries = ({
  page,
  pageSize,
  sortBy,
  sortDir,
}: FetchQueriesParams): Promise<FetchQueriesResponse> => {
  const params = new URLSearchParams({
    page: String(page),
    page_size: String(pageSize),
    ...(sortBy ? { sort_by: sortBy } : {}),
    ...(sortDir ? { sort_dir: sortDir } : {}),
  });

  return fetch(`${BASE}/queries?${params.toString()}`).then((r) =>
    json<FetchQueriesResponse>(r),
  );
};

export const createQuery = (
  data: CreateQueryPayload,
): Promise<Query> => {
  return fetch(`${BASE}/queries`, {
    method: "POST",
    headers,
    body: JSON.stringify(data),
  }).then((r) => json<Query>(r));
};

export const updateQuery = (
  id: number,
  data: UpdateQueryPayload,
): Promise<Query> => {
  return fetch(`${BASE}/queries/${id}`, {
    method: "PUT",
    headers,
    body: JSON.stringify(data),
  }).then((r) => json<Query>(r));
};

export const deleteQuery = (id: number): Promise<null> => {
  return fetch(`${BASE}/queries/${id}`, {
    method: "DELETE",
  }).then((r) => json<null>(r));
};

export const bulkDeleteQueries = (
  ids: number[],
): Promise<null> => {
  return fetch(`${BASE}/queries`, {
    method: "DELETE",
    headers,
    body: JSON.stringify({ ids }),
  }).then((r) => json<null>(r));
};
