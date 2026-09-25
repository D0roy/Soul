import os
import signal
import subprocess
import sys
import time


HOST = "0.0.0.0"
PORT = "8000"
CELERY_APP = "soul"


COMMANDS = [
    [
        sys.executable,
        "-m",
        "celery",
        "-A",
        CELERY_APP,
        "worker",
        "--loglevel=info",
        "--pool=solo",
    ],
    [
        sys.executable,
        "-m",
        "celery",
        "-A",
        CELERY_APP,
        "beat",
        "--loglevel=info",
    ],
    [
        sys.executable,
        "manage.py",
        "runserver",
        f"{HOST}:{PORT}",
    ],
]


def main():
    processes = []

    try:
        for command in COMMANDS:
            process = subprocess.Popen(
                command,
                cwd=os.path.dirname(
                    os.path.abspath(__file__)
                ),
            )

            processes.append(process)

            time.sleep(1)


        print(
            "Запущены:"
        )

        print(
            f"Django: http://{HOST}:{PORT}"
        )

        print(
            "Celery worker"
        )

        print(
            "Celery beat"
        )

        print(
            "Для остановки нажмите Ctrl+C."
        )


        while True:
            for process in processes:
                return_code = process.poll()

                if return_code is not None:
                    raise RuntimeError(
                        "Один из процессов завершился "
                        f"с кодом {return_code}."
                    )

            time.sleep(1)


    except KeyboardInterrupt:
        print(
            "\nОстановка процессов..."
        )


    finally:
        for process in processes:
            if process.poll() is None:
                process.terminate()


        for process in processes:
            try:
                process.wait(
                    timeout=5
                )
            except subprocess.TimeoutExpired:
                process.kill()


        print(
            "Все процессы остановлены."
        )


if __name__ == "__main__":
    main()