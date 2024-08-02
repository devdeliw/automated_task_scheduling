import time, random, shutil, os, sys, re
import pandas as pd
from datetime import datetime, timedelta
from google_tts import speak
from google_stt import run
from task_check import * 


def loading_animation(duration = random.randint(1, 4), interval = 0.5): 
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

def parse_task_string(task_string):

    time_pattern = re.compile(
        r'(\d{1,2}(:\d{2})?\s*[ap]\.?m\.?)\s*to\s*(\d{1,2}(:\d{2})?\s*[ap]\.?m\.?)',
        re.IGNORECASE
    )
    
    match = time_pattern.search(task_string)
    
    if not match:
        raise ValueError("Time pattern not found in the string")
    
    start_time_str, _, end_time_str, _ = match.groups()
    
    def convert_time(time_str):
        time_str = re.sub(r'[\.\-\s]', '', time_str.lower())
        return datetime.strptime(time_str, '%I:%M%p') if ':' in time_str else datetime.strptime(time_str, '%I%p')
    
    start_time = convert_time(start_time_str).strftime('%H:%M')
    end_time = convert_time(end_time_str).strftime('%H:%M')
    
    task_name = task_string.split('from')[0].strip()
    
    return task_name, start_time, end_time

def get_tasks(): 
    tasks = []
    count = 1 

    ordinals = {
        1: 'first', 2: 'second', 3: 'third', 4: 'fourth', 5: 'fifth',
        6: 'sixth', 7: 'seventh', 8: 'eighth', 9: 'ninth', 10: 'tenth'
    }

    # prints output to match terminal width
    terminal_size = shutil.get_terminal_size()
    width = terminal_size.columns 

    # good morning message
    date_time_str = format_datetime(datetime.now())
    good_morning =  f"Hi Deval, good morning! It is currently {date_time_str}"

    speak(good_morning)

    # inputting tasks for the day
    continue_loop = True
    while continue_loop: 
        if count == 1: 
            speak(f"What's your {ordinals.get(count, 'unknown')} task for today?")
        elif count == 2: 
            speak(f"Got it. What's your {ordinals.get(count, 'unknown')} task? ")
        elif count == 3: 
            speak(f"Alright. What's your {ordinals.get(count, 'unknown')} task? ")
        else: 
            speak(f"What's your {ordinals.get(count, 'unknown')} task")

        success = False
        while not success: 
            transcript = run(duration = 10)
            task_name_full = transcript[0][0]
            confidence = transcript[0][1]


            if ('for today' in task_name_full.lower() or 'done' in task_name_full.lower() or 
                'all' in task_name_full.lower() or 'that\'s it' in task_name_full.lower()):
                
                continue_loop = False
                if count > 2: 
                    speak(f"Great! I\'ll send you emails 30 minutes and 10 minutes prior to your {count - 1} tasks today. See you then!")
                else: 
                    speak(f"Great! I\'ll send you emails 30 minutes and 10 minutes prior to your {count - 1} task today. See you then!")
                break

            task_name, start_time, end_time = parse_task_string(task_name_full)

            speak(f"I heard {task_name_full} with a confidence of {confidence} percent. Is that correct?")

            correct = run(duration = 5)
            affirmative_pattern = re.compile(r'\b(yes|yeah|yep|yup|indeed)\b', re.IGNORECASE)

            if affirmative_pattern.search(correct[0][0].strip()):
                tasks.append({
                    'name': task_name, 
                    'start_time': start_time, 
                    'end_time': end_time,
                    'status': True
                })
                print('test 2')
                break
            else: 
                speak("Maybe try again?")

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