import subprocess

def run_commands():
  commands = [
    "python manage.py migrate",
    "python manage.py setup_permissions",
    "python manage.py setup_roles",
    "python manage.py collectstatic",
    "daphne -b 0.0.0.0 -p 8000 core.asgi:application"
  ]

  processes = []

  try:
    for command in commands:
      process = subprocess.Popen(command, shell=True)
      processes.append(process)
      process.communicate()
  except KeyboardInterrupt:
    print("Keyboard interruption detected. Exiting...")
    for process in processes:
      process.terminate()
    for process in processes:
      process.wait()

if __name__ == "__main__":
  run_commands()