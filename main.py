import os
import time
import random
from datetime import datetime, timedelta

SCRIPT_DIR = os.path.join(os.getcwd(), 'skrip')
SCRIPTS = ['wrap_unwrap.py', 'uni.py', 'aPriori.py', 'kitsu.py']

def run_script(script_name):
    script_path = os.path.join(SCRIPT_DIR, script_name)
    try:
        print(f"Running {script_name}...")
        os.system(f'python "{script_path}"')
        print(f"{script_name} completed!\n")
    except Exception as e:
        print(f"Error running {script_name}: {e}")

def wait_until_tomorrow():
    now = datetime.now()
    next_day = now + timedelta(days=1)
    random_hour = random.randint(7, 12)
    random_minute = random.randint(0, 59)
    run_time = next_day.replace(hour=random_hour, minute=random_minute, second=0, microsecond=0)
    
    wait_time = (run_time - now).total_seconds()
    print(f"Waiting until {run_time.strftime('%Y-%m-%d %H:%M:%S')}...\n")
    time.sleep(wait_time)

def main():
    while True:
        for script in SCRIPTS:
            run_script(script)
        wait_until_tomorrow()

if __name__ == "__main__":
    main()
