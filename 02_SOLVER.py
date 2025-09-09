import os
import subprocess
import time

# IMPOSTAZIONI UTENTE
# Definisci il numero massimo di analisi da eseguire in parallelo.
MAX_PARALLEL_JOBS = 2    # sarebbe 4 ma problemi con 16Gb RAM
# -------------------------

# Definisci le cartelle
input_folder = "input_files"
output_folder = "output_files"

# Crea la cartella di output principale se non esiste
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

# Raccogli la lista di tutti i job da eseguire
jobs_to_run = []
for file_name in os.listdir(input_folder):
    if file_name.endswith(".inp"):
        jobs_to_run.append(os.path.splitext(file_name)[0])

# Lista per tenere traccia dei processi Popen attivi
running_processes = []
job_index = 0

print "Avvio di {} analisi con un massimo di {} processi paralleli.".format(len(jobs_to_run), MAX_PARALLEL_JOBS)

while job_index < len(jobs_to_run):
    # Controlla se ci sono slot liberi nel pool di processi
    if len(running_processes) < MAX_PARALLEL_JOBS:
        job_name = jobs_to_run[job_index]
        
        # Percorso del file .inp
        input_path = os.path.join(input_folder, job_name + ".inp")
        
        # Crea una directory di output dedicata per questo job
        job_output_folder = os.path.join(output_folder, job_name)
        if not os.path.exists(job_output_folder):
            os.makedirs(job_output_folder)
            
        # Print
        print "Avvio del job: {}".format(job_name)
        absolute_input_path = os.path.abspath(input_path)        
        command = "abaqus job={} input={}".format(job_name, absolute_input_path)
        
        # Avvia il processo Abaqus
        process = subprocess.Popen(command, shell=True, cwd=job_output_folder)
        running_processes.append(process)        
        job_index += 1 # Passa al prossimo job della lista

    # Se il pool e' pieno, attendi che almeno un processo finisca
    else:
        # Controlla lo stato dei processi in esecuzione
        for p in running_processes[:]: # Itera su una copia della lista
            if p.poll() is not None: # Se .poll() non e' None, il processo e' terminato
                running_processes.remove(p)
        
        time.sleep(15) # Attendi 15 secondi prima di ricontrollare

# Attendi il completamento di tutti i processi rimasti alla fine
print "Tutti i job sono stati avviati. In attesa del completamento degli ultimi processi..."
for p in running_processes:
    p.wait()
print "Tutte le analisi sono state completate. I risultati si trovano in '{}'.".format(output_folder)