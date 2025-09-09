# -*- coding: utf-8 -*-
from odbAccess import *
import os
import csv

input_folder = "output_files"
output_folder = "extracted_data"
instance_name = 'PIPE-1'  # Nome dell'istanza nel modello

# Creazione della cartella di output se non esiste
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

# Itera ricorsivamente su tutte le cartelle e i file in input_folder
for root, dirs, files in os.walk(input_folder):
    for file_name in files:
        if file_name.endswith(".odb"):
            # 'root' e' la cartella che contiene il file (es. "output_files/run_0001")
            # 'file_name' e' il nome del file (es. "run_0001.odb")
            input_path = os.path.join(root, file_name)
            
            # I CSV verranno salvati tutti in 'extracted_data'
            output_name = file_name.replace(".odb", "_results.csv")
            output_path = os.path.join(output_folder, output_name)

            # Apertura del file ODB
            odb = openOdb(path=input_path)
            
            # Identifica quale step processare, con fallback su Step-1 per robustezza
            step_da_processare = None
            if 'Step-2' in odb.steps and len(odb.steps['Step-2'].frames) > 0:
                step_da_processare = odb.steps['Step-2']
            elif 'Step-1' in odb.steps and len(odb.steps['Step-1'].frames) > 0:
                print "ATTENZIONE: Step-2 non trovato o vuoto. Estraggo dati da Step-1 per il file " + file_name
                step_da_processare = odb.steps['Step-1']
            
            if step_da_processare:
                frame = step_da_processare.frames[-1]  # Seleziona l'ultimo frame
                displacements = frame.fieldOutputs['U']
                node_set = odb.rootAssembly.instances[instance_name].nodes  

                # Estrazione dei dati dei nodi
                node_data = []
                for disp in displacements.values:
                    node = node_set[disp.nodeLabel - 1]
                    node_data.append((
                        disp.nodeLabel,
                        float(node.coordinates[0]),  # X
                        float(node.coordinates[1]),  # Y
                        float(node.coordinates[2]),  # Z
                        float(disp.data[0]),  # Ux
                        float(disp.data[1]),  # Uy
                        float(disp.data[2])   # Uz
                    ))

                # Ordinamento dei nodi rispetto alla coordinata Z
                node_data.sort(key=lambda n: n[3])

                # Scrittura dei dati ordinati nel file CSV
                with open(output_path, 'wb') as file:
                    writer = csv.writer(file)
                    writer.writerow(["Nodo", "X", "Y", "Z", "Ux", "Uy", "Uz"])
                    for row in node_data:
                        writer.writerow(row)

                print "Dati estratti e ordinati per " + file_name + " e salvati in " + output_path

            else:
                print "ERRORE: Nessun frame valido trovato in Step-2 o Step-1 per il file " + file_name

            # Chiusura del file ODB
            odb.close()

print "Estrazione dati completata!"