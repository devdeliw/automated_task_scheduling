import time, random, shutil, os, sys
import pandas as pd
from datetime import datetime, timedelta
from google_tts import speak
from task_check import * 


def loading_animation(duration = random.randint(1, 4), interval = 0.3): 
    # fake loading animation
    end_time = time.time() + duration
    message = 'Starting Up'

    while time.time() < end_time:
        for i in range(4):
            sys.stdout.write('\r' + message + ' ' + '.' * i)
            sys.stdout.flush()
            time.sleep(interval)

    sys.stdout.write('\r' + ' ' * (len(message) + 3 + 3) + '\r')
    sys.stdout.flush()

def format_datetime(dt): 
    # prints the current date and time in a human-like fashion
    month_name = dt.strftime("%B")
    day = dt.day
    day_suffix = 'th' if 11 <= day <= 13 else {1: 'st', 2: 'nd', 3: 'rd'}.get(day % 10, 'th')
    
    hour = dt.strftime("%I").lstrip('0')  
    am_pm = dt.strftime("%p")

    return f"{month_name} {day}{day_suffix}, at {hour}{am_pm}"

def get_tasks(): 
    tasks = []
    count = 1

    # prints output to match terminal width
    terminal_size = shutil.get_terminal_size()
    width = terminal_size.columns 

    # good morning message
    date_time_str = format_datetime(datetime.now())
    good_morning =  f"Hi Deval, good morning! It is currently {date_time_str}. What are your tasks for today?"

    print(good_morning)

    # inputting tasks for the day
    while True: 
        print(f"Task {count}")
        task_name = input("Enter the name of the task (or 'done' to finish): ")
        if task_name.lower() == 'done' or task_name.lower() == 'done ':
            break
        start_time = input("Enter the start time (HH:MM): ")
        end_time = input("Enter the end time (HH:MM): ")

        tasks.append({
            'name': task_name, 
            'start_time': start_time, 
            'end_time': end_time,
            'status': True
        })

        count += 1

    # stores tasks into a DataFrame object and converts to .csv file
    tasks = pd.DataFrame(tasks)
    tasks.to_csv('tasks.csv')

    run_instance = Run()
    run_instance.load_tasks()
    run_instance.earliest_time()

if __name__ == "__main__": 
    loading_animation()
    get_tasks()