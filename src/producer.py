"""
Producer - tworzy i zapisuje zadania do kolejki
"""
import argparse
from datetime import datetime
from models import Task
from task_manager import add_tasks, get_all_tasks
from config import PRODUCER_DEFAULT_COUNT, TASK_DESCRIPTIONS, STATUS_PENDING


def generate_phone_call_tasks(count: int = PRODUCER_DEFAULT_COUNT) -> list:
    """Generuje zadania rozmów telefonicznych"""
    tasks = []
    now = datetime.now().isoformat()

    # Pobierz ostatnie ID aby uniknąć konfliktów
    existing_tasks = get_all_tasks()
    start_id = len(existing_tasks) + 1 if existing_tasks else 1

    for i in range(start_id, start_id + count):
        task = Task(
            id=i,
            description=TASK_DESCRIPTIONS[(i - 1) % len(TASK_DESCRIPTIONS)],
            status=STATUS_PENDING,
            created_at=now
        )
        tasks.append(task)

    return tasks


def main():
    """Główna funkcja producera"""
    parser = argparse.ArgumentParser(description="Producer - tworzy zadania do kolejki")
    parser.add_argument("--count", type=int, default=100, help="Liczba zadań do utworzenia (domyślnie 100)")
    args = parser.parse_args()

    print(f"[PRODUCER] Tworzę {args.count} zadań...")
    tasks = generate_phone_call_tasks(args.count)

    if add_tasks(tasks):
        print(f"[PRODUCER] ✓ Pomyślnie dodano {args.count} zadań do kolejki!")
    else:
        print(f"[PRODUCER] ✗ Błąd przy dodawaniu zadań!")


if __name__ == "__main__":
    main()

