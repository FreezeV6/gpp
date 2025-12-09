"""
Moduł zarządzania zadaniami - operacje na pliku CSV
"""
import csv
import os
import fcntl
from contextlib import contextmanager
from pathlib import Path
from typing import List, Dict, Optional
from models import Task
from datetime import datetime
from config import TASKS_FILE, STATUS_PENDING
FIELDNAMES = ["id", "description", "status", "created_at", "started_at", "completed_at"]


@contextmanager
def _locked_file(path: str, mode: str, lock_type: int):
    """Zwraca uchwyt do pliku z ustawioną blokadą flock"""
    f = open(path, mode, newline="")
    try:
        fcntl.flock(f.fileno(), lock_type)
        yield f
    finally:
        fcntl.flock(f.fileno(), fcntl.LOCK_UN)
        f.close()


def ensure_file_exists():
    """Tworzy plik CSV jeśli nie istnieje"""
    if not os.path.exists(TASKS_FILE):
        with open(TASKS_FILE, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
            writer.writeheader()


def get_all_tasks() -> List[Dict]:
    """Pobiera wszystkie zadania z pliku"""
    ensure_file_exists()
    tasks = []
    try:
        with _locked_file(TASKS_FILE, "r", fcntl.LOCK_SH) as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row:  # Pomiń puste wiersze
                    tasks.append(row)
    except Exception as e:
        print(f"Błąd przy czytaniu pliku: {e}")
    return tasks


def add_task(task: Task) -> bool:
    """Dodaje nowe zadanie do pliku"""
    ensure_file_exists()
    try:
        with _locked_file(TASKS_FILE, "a", fcntl.LOCK_EX) as f:
            writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
            writer.writerow({
                "id": task.id,
                "description": task.description,
                "status": task.status,
                "created_at": task.created_at,
                "started_at": task.started_at,
                "completed_at": task.completed_at,
            })
        return True
    except Exception as e:
        print(f"Błąd przy zapisywaniu zadania: {e}")
        return False


def add_tasks(tasks: List[Task]) -> bool:
    """Dodaje wiele zadań do pliku"""
    ensure_file_exists()
    try:
        with _locked_file(TASKS_FILE, "a", fcntl.LOCK_EX) as f:
            writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
            for task in tasks:
                writer.writerow({
                    "id": task.id,
                    "description": task.description,
                    "status": task.status,
                    "created_at": task.created_at,
                    "started_at": task.started_at,
                    "completed_at": task.completed_at,
                })
        return True
    except Exception as e:
        print(f"Błąd przy zapisywaniu zadań: {e}")
        return False


def update_task_status(
    task_id: int,
    new_status: str,
    started_at: str = "",
    completed_at: str = "",
    expected_status: Optional[str] = None,
) -> bool:
    """Aktualizuje status zadania w sposób bezpieczny dla wielu konsumentów"""
    ensure_file_exists()
    try:
        updated = False
        with _locked_file(TASKS_FILE, "r+", fcntl.LOCK_EX) as f:
            reader = list(csv.DictReader(f))
            f.seek(0)
            f.truncate()
            writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
            writer.writeheader()

            for task in reader:
                if int(task["id"]) == task_id:
                    if expected_status and task["status"] != expected_status:
                        writer.writerow(task)
                        continue
                    task["status"] = new_status
                    if started_at:
                        task["started_at"] = started_at
                    if completed_at:
                        task["completed_at"] = completed_at
                    updated = True
                writer.writerow(task)
        return updated
    except Exception as e:
        print(f"Błąd przy aktualizacji statusu: {e}")
        return False


def get_pending_tasks() -> List[Dict]:
    """Pobiera wszystkie zadania w statusie 'pending'"""
    all_tasks = get_all_tasks()
    return [task for task in all_tasks if task["status"] == STATUS_PENDING]


def get_task_by_id(task_id: int) -> Optional[Dict]:
    """Pobiera zadanie po ID"""
    all_tasks = get_all_tasks()
    for task in all_tasks:
        if int(task["id"]) == task_id:
            return task
    return None
