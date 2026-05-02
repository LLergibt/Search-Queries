import { useState, useEffect } from "react";
import Modal from "../../../shared/ui/Modal";
import type {
  Query,
  CreateQueryPayload,
  UpdateQueryPayload,
} from "../api/queriesApi";

interface Props {
  query?: Query | null;
  onSave: (data: CreateQueryPayload | UpdateQueryPayload) => Promise<void>;
  onClose: () => void;
}

interface Errors {
  name?: string;
  submit?: string;
}

const toInputDate = (iso?: string | null): string => {
  if (!iso) return "";

  const date = new Date(iso);
  const pad = (n: number) => String(n).padStart(2, "0");

  return `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(
    date.getDate(),
  )}T${pad(date.getHours())}:${pad(date.getMinutes())}`;
};

const fromInputDate = (value: string): string | null => {
  if (!value) return null;

  const date = new Date(value);
  return date.toISOString();
};

export default function QueryModal({
  query,
  onSave,
  onClose,
}: Props): JSX.Element {
  const isEdit = Boolean(query);

  const [name, setName] = useState<string>(query?.name ?? "");
  const [isActive, setIsActive] = useState<boolean>(query?.is_active ?? true);
  const [deadline, setDeadline] = useState<string>(
    toInputDate(query?.deadline),
  );
  const [saving, setSaving] = useState<boolean>(false);
  const [errors, setErrors] = useState<Errors>({});

  useEffect(() => {
    setName(query?.name ?? "");
    setIsActive(query?.is_active ?? true);
    setDeadline(toInputDate(query?.deadline));
    setErrors({});
  }, [query]);

  const validate = (): Errors => {
    const e: Errors = {};
    if (!name.trim()) e.name = "Название обязательно";
    return e;
  };

  const handleSubmit = async (
    e: React.FormEvent<HTMLFormElement>,
  ): Promise<void> => {
    e.preventDefault();

    const e2 = validate();
    if (Object.keys(e2).length) {
      setErrors(e2);
      return;
    }

    setSaving(true);

    try {
      await onSave({
        name: name.trim(),
        is_active: isActive,
        deadline: fromInputDate(deadline),
      });
      onClose();
    } catch {
      setErrors({ submit: "Ошибка при сохранении" });
    } finally {
      setSaving(false);
    }
  };

  const nowInput = toInputDate(new Date().toISOString());

  return (
    <Modal
      title={isEdit ? "Редактировать запрос" : "Новый запрос"}
      onClose={onClose}
    >
      <form onSubmit={handleSubmit} className="modal-form">
        <div className="field">
          <label>Название</label>
          <input
            type="text"
            value={name}
            onChange={(e) => setName(e.target.value)}
            placeholder="sales_report_q1"
            autoFocus
          />
          {errors.name && <span className="field-error">{errors.name}</span>}
        </div>

        <div className="field">
          <label>Статус</label>
          <div className="toggle-row">
            <button
              type="button"
              className={`toggle-btn ${isActive ? "toggle-active" : ""}`}
              onClick={() => setIsActive(true)}
            >
              Активен
            </button>
            <button
              type="button"
              className={`toggle-btn ${!isActive ? "toggle-inactive" : ""}`}
              onClick={() => setIsActive(false)}
            >
              Неактивен
            </button>
          </div>
        </div>

        <div className="field">
          <label>Дедлайн</label>
          <input
            type="datetime-local"
            value={deadline}
            onChange={(e) => setDeadline(e.target.value)}
            min={nowInput}
            step={60}
          />
          {deadline && (
            <button
              type="button"
              className="clear-btn"
              onClick={() => setDeadline("")}
            >
              Очистить
            </button>
          )}
        </div>

        {errors.submit && <div className="field-error">{errors.submit}</div>}

        <div className="modal-actions">
          <button type="button" className="btn btn-ghost" onClick={onClose}>
            Отмена
          </button>
          <button type="submit" className="btn btn-primary" disabled={saving}>
            {saving ? "Сохранение…" : isEdit ? "Сохранить" : "Создать"}
          </button>
        </div>
      </form>
    </Modal>
  );
}
