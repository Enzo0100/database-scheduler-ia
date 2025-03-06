import schedule
import time
import subprocess


def run_script():
    print("Executando o script...")
    subprocess.run(["python", "logic/main.py"]) 

schedule.every().day.at("14:39").do(run_script)
print("Scheduler iniciado. Aguardando a execução...")

while True:
    schedule.run_pending()
    time.sleep(30)