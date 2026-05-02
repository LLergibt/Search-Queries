import { useState, useEffect, useCallback } from "react";
import * as api from "../api/queriesApi";
import type {
  FetchQueriesParams,
  FetchQueriesResponse,
  CreateQueryPayload,
  UpdateQueryPayload,
} from "../api/queriesApi";

interface UseQueriesState {
  data: FetchQueriesResponse | null;
  loading: boolean;
  error: string | null;
  params: FetchQueriesParams;
}

interface UseQueriesActions {
  setPage: (page: number) => void;
  setSort: (sortBy: string) => void;
  setPageSize: (pageSize: number) => void;
  createQuery: (formData: CreateQueryPayload) => Promise<void>;
  updateQuery: (id: number, formData: UpdateQueryPayload) => Promise<void>;
  deleteQuery: (id: number) => Promise<void>;
  bulkDelete: (ids: number[]) => Promise<void>;
}

const DEFAULT_PARAMS: FetchQueriesParams = {
  page: 1,
  pageSize: 50,
  sortBy: "created_at",
  sortDir: "desc",
};

export function useQueries(): UseQueriesState & UseQueriesActions {
  const [data, setData] = useState<FetchQueriesResponse | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [params, setParams] = useState<FetchQueriesParams>(DEFAULT_PARAMS);

  const load = useCallback(async (): Promise<void> => {
    setLoading(true);
    setError(null);

    try {
      const result = await api.fetchQueries(params);
      setData(result);
    } catch (e) {
      const message = e instanceof Error ? e.message : "Unknown error";
      setError(message);
    } finally {
      setLoading(false);
    }
  }, [params]);

  useEffect(() => {
    load();
  }, [load]);

  const setPage = (page: number): void => setParams((p) => ({ ...p, page }));

  const setSort = (sortBy: string): void =>
    setParams((p) => ({
      ...p,
      sortBy,
      sortDir: p.sortBy === sortBy && p.sortDir === "asc" ? "desc" : "asc",
      page: 1,
    }));

  const setPageSize = (pageSize: number): void =>
    setParams((p) => ({ ...p, pageSize, page: 1 }));

  const createQuery = async (formData: CreateQueryPayload): Promise<void> => {
    await api.createQuery(formData);
    setParams((p) => ({ ...p, page: 1 }));
  };

  const updateQuery = async (
    id: number,
    formData: UpdateQueryPayload,
  ): Promise<void> => {
    await api.updateQuery(id, formData);
    await load();
  };

  const deleteQuery = async (id: number): Promise<void> => {
    await api.deleteQuery(id);
    await load();
  };

  const bulkDelete = async (ids: number[]): Promise<void> => {
    await api.bulkDeleteQueries(ids);
    await load();
  };

  return {
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
  };
}
