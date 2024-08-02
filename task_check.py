from task_input import * 
import smtplib, plistlib, argparse, shutil
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

class Run: 

    def __init__(self): 

        self.TASKS_FILE = '/Users/devaldeliwala/calendar_AI/tasks.csv'
        self.plist_path_main = '/Users/devaldeliwala/Library/LaunchAgents/com.devdeliw.task_scheduler.plist'
        self.plist_path_30 = '/Users/devaldeliwala/Library/LaunchAgents/com.devdeliw.task_scheduler_30.plist'
        self.plist_path_10 ='/Users/devaldeliwala/Library/LaunchAgents/com.devdeliw.task_scheduler_10.plist'
        self.tasks = None

    def load_tasks(self): 
        tasks = pd.read_csv(self.TASKS_FILE)
        self.tasks = tasks
        return tasks 

    def update_plist(self, plist_path, new_schedule): 
        tasks = self.tasks

        if not os.path.exists(plist_path): 
            raise FileNotFoundError(f'{plist_path} not found.')

        with open(plist_path, 'rb') as f: 
            plist = plistlib.load(f)

        plist['StartCalendarInterval'] = new_schedule

        with open(plist_path, 'wb') as f: 
            plistlib.dump(plist, f)

        return

    def earliest_time(self):

        def adjust_time(time_dict, minutes_to_subtract):

            hour = int(time_dict['Hour'])
            minute = int(time_dict['Minute'])
            original_time = datetime(2020, 1, 1, hour, minute)
            new_time = original_time - timedelta(minutes=minutes_to_subtract)
            return {'Hour': new_time.hour, 'Minute': new_time.minute}

        tasks = self.tasks

        time_list = []
        for index, task in tasks.iterrows(): 
            time_list.append(task['start_time'])

        def to_minutes(time_str): 
            hour, minute = map(int, time_str.split(':'))
            return hour * 60 + minute

        earliest_time = min(time_list, key = to_minutes)
        hour, minute = earliest_time.split(':')
        schedule= {'Hour': hour, 'Minute': minute}

        self.update_plist(plist_path = self.plist_path_main, 
                          new_schedule = schedule)
        self.update_plist(plist_path = self.plist_path_30, 
                          new_schedule = adjust_time(schedule, 30))
        self.update_plist(plist_path = self.plist_path_10, 
                          new_schedule = adjust_time(schedule, 10))

        self.tell_iterm(f'launchctl unload {self.plist_path_main}')
        self.tell_iterm(f'launchctl load {self.plist_path_main}')
        self.tell_iterm(f'launchctl unload {self.plist_path_30}')
        self.tell_iterm(f'launchctl load {self.plist_path_30}')
        self.tell_iterm(f'launchctl unload {self.plist_path_10}')
        self.tell_iterm(f'launchctl load {self.plist_path_10}')
        self.tell_iterm(f'clear')

        return 

    def tell_iterm(self, script): 

        script = script.replace("\"", "\\\"")

        string = f"""
        tell application "iTerm"
            if (count of windows) is 0 then
                create window with default profile
                tell current session of current window
                    write text \"{script}\"
                end tell
            else
                tell current session of current window
                    write text \"{script}\"
                end tell
            end if
        end tell
        """
        os.system(f"osascript -e '{string}'")

        return

    def check_and_notify(self): 
        tasks = self.tasks

        current_time = datetime.now().strftime("%H:%M")
        current_datetime = datetime.strptime(current_time, "%H:%M")
        task_time = datetime.now().replace(hour = current_datetime.hour, 
                                           minute = current_datetime.minute, 
                                           second = 0, microsecond = 0
        )

        for index, task in tasks.iterrows(): 
            task_start= datetime.strptime(task['start_time'], "%H:%M")
            early_30min = (task_start - timedelta(minutes = 30)).strftime("%H:%M")
            early_10min = (task_start - timedelta(minutes = 10)).strftime("%H:%M")

            task_start = task['start_time']

            if current_time == task_start: 
                self.run_script(task)
                break
            elif current_time == early_30min: 
                self.run_reminder(task, '30')
                break
            elif current_time == early_10min: 
                self.run_reminder(task, '10')
                break

    def run_reminder(self, task, amount): 
        smtp_server = 'smtp.gmail.com'
        smtp_port = 587
        username = 'devaldeliwala04@gmail.com'
        password = 'vngh nqah ihyo zqoa'
        from_email = 'devaldeliwala04@gmail.com'
        to_email = 'devaldeliwala@berkeley.edu'
        subject = f"`{task['name']}` starts in 10 minutes!"
        body = f"Hi Deval, \'{task['name']}\' starts in {amount} minutes!"

        msg = MIMEMultipart()
        msg['From'] = from_email
        msg['To'] = to_email
        msg['Subject'] = subject

        msg.attach(MIMEText(body, 'plain'))

        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(username, password)
            server.send_message(msg)

    def run_script(self, task): 
        self.tell_iterm(f"/Users/devaldeliwala/miniconda3/bin/python /Users/devaldeliwala/calendar_AI/task_check.py --task \"{task['name']}\"")
        return 

    def format_duration(self, duration):
        total_seconds = int(duration.total_seconds())
        hours, remainder = divmod(total_seconds, 3600)
        minutes, _ = divmod(remainder, 60)

        if hours > 0 and minutes > 0:
            return f"{hours} hours and {minutes} minutes"
        elif hours > 0:
            return f"{hours} hours"
        elif minutes > 0:
            return f"{minutes} minutes"
        else:
            return "less than a minute"

    def notify_task(self, task): 
        start_time = datetime.strptime(task['start_time'], "%H:%M")
        end_time = datetime.strptime(task['end_time'], "%H:%M")
        duration = end_time - start_time

        speak(f"{task['name']} has started. You have {self.format_duration(duration)} remaining.")

        terminal_size = shutil.get_terminal_size()
        width = terminal_size.columns
        padding = (width - len(task['name'])) // 2

        print("\n")
        print('‾' * width)
        print(' ' * padding + task['name'])
        print('‾' * width)
        print("\n")

        while duration > timedelta(0): 
            print(f"Time Remaining: {duration}", end = '\r')
            duration -= timedelta(seconds = 1)
            time.sleep(1)

        if random.randint(1, 2) == 1: 
            speak(f"{task['name']} completed. Good Job.")
        else: 
            speak(f"{task['name']} completed. Excellent Job.")

        return

def main(): 
    parser = argparse.ArgumentParser()
    parser.add_argument('--task', help = 'name of task')
    args = parser.parse_args()

    run_instance = Run()

    if args.task: 
        tasks = run_instance.load_tasks()
        task = tasks[tasks['name'] == args.task]
        if not task.empty: 
            task_dict = task.iloc[0].to_dict()
            run_instance.notify_task(task_dict)
        else: 
            print(f"Task \"{args.task}\" not found.")
    else: 
        tasks = run_instance.load_tasks()
        run_instance.check_and_notify()


if __name__ == "__main__": 
    main()