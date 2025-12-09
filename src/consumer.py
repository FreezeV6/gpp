"""
Consumer - konsumuje i wykonuje zadania z kolejki
"""
import time
import argparse
import sys
from datetime import datetime
from task_manager import get_pending_tasks, update_task_status
from config import (
    CONSUMER_DEFAULT_TASK_DURATION,
    CONSUMER_DEFAULT_CHECK_INTERVAL,
    STATUS_PENDING,
    STATUS_IN_PROGRESS,
    STATUS_DONE
)


class Consumer:
    """Klasa reprezentująca konsumenta"""

    def __init__(self, consumer_id: int, task_duration: int = CONSUMER_DEFAULT_TASK_DURATION, check_interval: int = CONSUMER_DEFAULT_CHECK_INTERVAL):
        """
        Inicjalizuje konsumenta

        Args:
            consumer_id: Unikalny identyfikator konsumenta
            task_duration: Czas wykonywania jednego zadania w sekundach
            check_interval: Przedział czasu między sprawdzeniami kolejki w sekundach
        """
        self.consumer_id = consumer_id
        self.task_duration = task_duration
        self.check_interval = check_interval
        self.tasks_completed = 0

    def execute_task(self, task_id: int, description: str) -> bool:
        """
        Wykonuje zadanie

        Args:
            task_id: ID zadania
            description: Opis zadania

        Returns:
            True jeśli zadanie zostało wykonane, False inaczej
        """
        now = datetime.now().isoformat()

        # Zmiana statusu na in_progress
        if not update_task_status(task_id, STATUS_IN_PROGRESS, started_at=now, expected_status=STATUS_PENDING):
            print(f"[CONSUMER-{self.consumer_id}] ⚠ Zadanie {task_id} zostało już przejęte. Szukam dalej...")
            return False

        print(f"[CONSUMER-{self.consumer_id}] ▶ Rozpoczynam wykonywanie zadania #{task_id}: {description}")

        # Symulacja wykonywania zadania
        start_time = time.time()
        while time.time() - start_time < self.task_duration:
            elapsed = int(time.time() - start_time)
            remaining = self.task_duration - elapsed
            if elapsed == 0 or elapsed % 5 == 0:
                print(f"[CONSUMER-{self.consumer_id}]   ⏳ Zadanie #{task_id}: {remaining}s pozostało...")
            time.sleep(1)

        # Zmiana statusu na done
        now = datetime.now().isoformat()
        if not update_task_status(task_id, STATUS_DONE, completed_at=now, expected_status=STATUS_IN_PROGRESS):
            print(f"[CONSUMER-{self.consumer_id}] ✗ Nie udało się zaznaczyć zadania {task_id} jako ukończone")
            return False

        self.tasks_completed += 1
        print(f"[CONSUMER-{self.consumer_id}] ✓ Zadanie #{task_id} ukończone! (Razem: {self.tasks_completed})")
        return True

    def run(self):
        """Główna pętla konsumenta"""
        print(f"[CONSUMER-{self.consumer_id}] Uruchomiono konsumenta. Czekam na zadania...")

        try:
            while True:
                # Pobierz zadania w statusie pending
                pending_tasks = get_pending_tasks()

                if pending_tasks:
                    # Weź pierwsze zadanie
                    task = pending_tasks[0]
                    task_id = int(task["id"])
                    description = task["description"]

                    # Wykonaj zadanie
                    self.execute_task(task_id, description)
                else:
                    print(f"[CONSUMER-{self.consumer_id}] Brak zadań. Czekam {self.check_interval}s...")
                    time.sleep(self.check_interval)

        except KeyboardInterrupt:
            print(f"\n[CONSUMER-{self.consumer_id}] Zatrzymano. Wykonano {self.tasks_completed} zadań.")
            sys.exit(0)
        except Exception as e:
            print(f"[CONSUMER-{self.consumer_id}] ✗ Błąd: {e}")
            sys.exit(1)


def main():
    """Główna funkcja konsumera"""
    parser = argparse.ArgumentParser(description="Consumer - konsumuje zadania z kolejki")
    parser.add_argument("--id", type=int, default=1, help="ID konsumera (domyślnie 1)")
    parser.add_argument("--task-duration", type=int, default=30, help="Czas wykonywania zadania w sekundach (domyślnie 30)")
    parser.add_argument("--check-interval", type=int, default=5, help="Przedział sprawdzania kolejki w sekundach (domyślnie 5)")
    args = parser.parse_args()

    consumer = Consumer(
        consumer_id=args.id,
        task_duration=args.task_duration,
        check_interval=args.check_interval
    )
    consumer.run()


if __name__ == "__main__":
    main()
