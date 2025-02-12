# import os
# import signal
# import subprocess
# from watchdog.observers import Observer
# from watchdog.events import FileSystemEventHandler

# class RestartDaphne(FileSystemEventHandler):
#     def __init__(self, process):
#         self.process = process

#     def on_any_event(self, event):
#         print("Change detected. Restarting Daphne...")
#         self.process.send_signal(signal.SIGTERM)
#         self.process = subprocess.Popen(["daphne", "-b", "0.0.0.0", "-p", "8000", "core.asgi:application"])

# def start_daphne():
#     process = subprocess.Popen(["daphne", "-b", "0.0.0.0", "-p", "8000", "core.asgi:application"])
#     event_handler = RestartDaphne(process)
#     observer = Observer()
#     observer.schedule(event_handler, path=".", recursive=True)
#     observer.start()

#     try:
#         process.wait()
#     except KeyboardInterrupt:
#         observer.stop()
#         observer.join()

# if __name__ == "__main__":
#     start_daphne()

import sys
import os
import django

if __name__ == '__main__':
    # insert here whatever commands you use to run daphne
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")

    sys.argv = ['daphne', 'core.asgi:application']
    from daphne.cli import CommandLineInterface
    django.setup()
    CommandLineInterface.entrypoint()
