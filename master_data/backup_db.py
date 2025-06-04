import subprocess
import os
import sys

def backup_database(apps_and_dbs):
    os.makedirs('data_backup', exist_ok=True)
    python_cmd = os.environ.get("PYTHON_CMD", sys.executable)  # default to current Python

    for entry in apps_and_dbs:
        app_label = entry["app"]
        db_alias = entry["database"]
        filename = f"{app_label}.json"
        output_path = os.path.join('data_backup', filename)

        command = [
            python_cmd, "manage.py", "dumpdata", app_label,
            f"--database={db_alias}",
            f"--output={output_path}"
        ]

        try:
            subprocess.run(command, check=True)
            print(f"✔ Backup completed for '{app_label}' to '{output_path}'")
        except subprocess.CalledProcessError as e:
            print(f"❌ Error backing up '{app_label}': {e}")

if __name__ == '__main__':
    apps_to_backup = [
        {"app": "master", "database": "master"},
        {"app": "sales", "database": "sales"},
        {"app": "supplier", "database": "supplier"},
        {"app": "auth", "database": "default"},
    ]

    backup_database(apps_to_backup)