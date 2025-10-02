import json
from json import JSONDecodeError
from pathlib import Path
from datetime import datetime

DB_PATH = Path("task_db.json")

Status = {
    "NEW": "New",
    "INPROG": "In progress",
    "DONE": "Done",
}

def now() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def load_tasks() -> list[dict]:
    if not DB_PATH.exists() or DB_PATH.stat().st_size == 0:
        return []
    try:
        with DB_PATH.open("r", encoding="utf-8") as f:
            data = json.load(f)
            return data if isinstance(data, list) else []
    except JSONDecodeError:
        return []

def save_tasks(tasks: list[dict]) -> None:
    with DB_PATH.open("w", encoding="utf-8") as f:
        json.dump(tasks, f, indent=4, ensure_ascii=False)

def next_id(tasks: list[dict]) -> int:
    return (max((t.get("id", 0) for t in tasks), default=0) + 1)

def find_by_id(tasks: list[dict], task_id: int) -> dict | None:
    for t in tasks:
        if t.get("id") == task_id:
            return t
    return None

def ask(prompt: str) -> str:
    # Egységes input: körbevág, kisbetűs változat is visszaadható, stb.
    return input(prompt).strip()

def create_task():
    tasks = load_tasks()
    description = ask("Enter description for the task: ").capitalize()
    new_task = {
        "id": next_id(tasks),
        "description": description,
        "status": Status["NEW"],
        "created_at": now(),
        "updated_at": now(),
    }
    tasks.append(new_task)
    save_tasks(tasks)
    print("New task successfully saved.")

def modify_task():
    tasks = load_tasks()
    raw = ask("Select task by id: ")
    if not raw.isdigit():
        print("Invalid id.")
        return
    task = find_by_id(tasks, int(raw))
    if not task:
        print("Task not found.")
        return

    print(f"\nCurrent values:\n  id: {task['id']}\n  Description: {task['description']}\n  Status: {task['status']}\n  Created at: {task['created_at']}\n")

    print("Select what you wish to modify:")
    print("1. Description")
    print("2. Status (In progress)")
    print("Type 'skip' to cancel.")
    choice = ask("Your choice (1/2/skip): ").lower()

    if choice == "1":
        task["description"] = ask("Enter new description: ").capitalize()
        task["updated_at"] = now()
    elif choice == "2":
        task["status"] = Status["INPROG"]
        task["updated_at"] = now()
    elif choice == "skip":
        return
    else:
        print("Invalid choice.")
        return

    save_tasks(tasks)
    print("Task updated.")

def change_status_to_done():
    tasks = load_tasks()
    raw = ask("Select task by id: ")
    if not raw.isdigit():
        print("Invalid id.")
        return
    task = find_by_id(tasks, int(raw))
    if not task:
        print("Task not found.")
        return
    task["status"] = Status["DONE"]
    task["updated_at"] = now()
    save_tasks(tasks)
    print("Task marked as DONE.")

def delete_task():
    tasks = load_tasks()
    raw = ask("Select which task you wish to delete (by id): ")
    if not raw.isdigit():
        print("Invalid id.")
        return
    tid = int(raw)
    new_tasks = [t for t in tasks if t.get("id") != tid]
    if len(new_tasks) == len(tasks):
        print("Task not found.")
        return
    save_tasks(new_tasks)
    print("Task deleted.")

def list_tasks(status_filters: list[str]):
    tasks = load_tasks()
    # normalizáljuk a szűrőket kisbetűre
    wanted = {s.lower() for s in status_filters}
    shown = [t for t in tasks if t.get("status","").lower() in wanted]
    print(f"\nTasks with status in {status_filters}:")
    if not shown:
        print("(none)")
        return
    for t in shown:
        print(
            f"\n id: {t['id']}\n Description: {t['description']}\n Status: {t['status']}\n Created: {t['created_at']}\n Updated: {t.get('updated_at','-')}"
        )

def print_overview():
    tasks = load_tasks()
    if not tasks:
        print("Currently there is no task recorded in the application.")
        return
    print("Currently recorded tasks:")
    for t in tasks:
        print(f"{t['id']} - {t['description']} - {t['status']}")

def main():
    print("***** Task Tracker Application *****")
    actions = {
        "1": create_task,
        "2": modify_task,
        "3": change_status_to_done,
        "4": delete_task,
        "5": lambda: list_tasks([Status["NEW"], Status["INPROG"], Status["DONE"]]),
        "6": lambda: list_tasks([Status["DONE"]]),
        "7": lambda: list_tasks([Status["NEW"], Status["INPROG"]]),
        "8": lambda: list_tasks([Status["INPROG"]]),
    }

    while True:
        print("\nSelect an action:")
        print("1. Add new task")
        print("2. Modify Description / Set task to In progress.")
        print("3. Mark as Done.")
        print("4. Delete task")
        print("5. List all tasks")
        print("6. List all Done tasks.")
        print("7. List all Not Done tasks")
        print("8. List all tasks that are In Progress")
        print("Type 'exit' to quit.\n")

        print_overview()
        choice = ask("\nAction (1-8 or 'exit'): ").lower()
        if choice == "exit":
            print("Goodbye!")
            break
        action = actions.get(choice)
        if action:
            action()
        else:
            print("Invalid choice.")

if __name__ == "__main__":
    main()
