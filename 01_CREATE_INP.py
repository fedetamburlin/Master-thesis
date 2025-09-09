# -*- coding: mbcs -*-
from abaqus import *
from abaqusConstants import *
import __main__
import numpy as np
import csv
import os

# DEFAULT VALUES
DIAM_def = 1066.9
L_def = 6100.0
E_def = 210000.0
NI_def = 0.3
SY1_def = 400.0
EP1_def = 0.0
SY2_def = 500.0
EP2_def = 0.08
THK_def = 30
COMPR_def = 5e6
PRESS_def = 1.0
CURV_def = 0.1

CURVILINEAR_STEP_def = 50 # mm, mesh lungo z
OVAL_def = 0
NP_def = 1  # default processors

#----------------------------------------------------------------------------
# MAIN

def main():
    csv_file = "Parameters_DoE.csv"

    # Leggere CSV senza Pandas
    with open(csv_file) as file:
        reader = csv.reader(file)
        next(reader)  # Salta l'intestazione

        for i, row in enumerate(reader, start=1):
            THK = float(row[1])  # Wall Thickness
            DIAM_p = float(row[0])     # Diam in pollici
            COMPR = float(row[2])       # Compression Force
            PRESS = float(row[3])     # External Pressure
            #LEN = float(row[4])     # Pipe lenght
            E = float(row[4])     # Young Modulus
            #NI = float(row[5])     # Poisson Modulus
            SY1 = float(row[5])     # SY1
            SY2 = float(row[6])     # SY2
            EP2 = float(row[7])     # EP2
            OVAL = float(row[8])     # Ovalisation
            CURV = float(row[9])     # Curvature
            
            DIAM = pollici_a_mm(DIAM_p)  # D_out convertito in mm            

            # Creazione file inp
            part_module(DIAM, OVAL)
            material_module(E, NI_def, SY1, EP1_def, SY2, EP2)
            section_module(THK)
            assembly_module()
            steps_module()
            constraints_module()
            amplitudes_module()
            loads_module(COMPR, PRESS)
            BC_module(CURV)                
            partitions_module()
            mesh_module()
            job_module(i)

    print("Files inp creati correttamente")

# PART-----------------------------------------------------------------------------------

def part_module(DIAM=DIAM_def, OVAL=OVAL_def, L=L_def):
    import section
    import regionToolset
    import displayGroupMdbToolset as dgm
    import part
    import material
    import assembly
    import step
    import interaction
    import load
    import mesh
    import optimization
    import job
    import sketch
    import visualization
    import xyPlot
    import displayGroupOdbToolset as dgo
    import connectorBehavior
    
    s = mdb.models['Model-1'].ConstrainedSketch(name='__profile__', 
        sheetSize=2000.0)
    g, v, d, c = s.geometry, s.vertices, s.dimensions, s.constraints
    s.setPrimaryObject(option=STANDALONE)
    
     # Calcolo dei semiassi in funzione dell'ovalizzazione
    a = (DIAM / 2.0) * (1 + OVAL / 2.0)  # Semiasse maggiore (su asse X)
    b = (DIAM / 2.0) * (1 - OVAL / 2.0)  # Semiasse minore (su asse Y)

    # Creazione dell'ellisse
    s.EllipseByCenterPerimeter(center=(0.0, 0.0), axisPoint1=(a, 0.0),
                                axisPoint2=(0.0, b))
    
    p = mdb.models['Model-1'].Part(name='Pipe', dimensionality=THREE_D, 
        type=DEFORMABLE_BODY)
    p = mdb.models['Model-1'].parts['Pipe']
    
    # Extrusion
    p.BaseShellExtrude(sketch=s, depth=L)
    s.unsetPrimaryObject()
    del mdb.models['Model-1'].sketches['__profile__']

# PARTITIONS------------------------------------------------------------------------

def partitions_module():
    import section
    import regionToolset
    import displayGroupMdbToolset as dgm
    import part
    import mesh
    import sketch
    import visualization
    import xyPlot
    import displayGroupOdbToolset as dgo
    import connectorBehavior

    # Recupera la parte
    model = mdb.models['Model-1']
    p = model.parts['Pipe']

    # Creo i piani di riferimento e salvo gli ID
    datum_plane_YZ = p.DatumPlaneByPrincipalPlane(principalPlane=YZPLANE, offset=0.0)
    datum_plane_XZ = p.DatumPlaneByPrincipalPlane(principalPlane=XZPLANE, offset=0.0)

    # Recuperare ID effettivo dei datum planes
    datum_id_YZ = datum_plane_YZ.id
    datum_id_XZ = datum_plane_XZ.id

    # Recupera le facce della parte
    f = p.faces

    # Verifica che il datum plane esista prima di applicarlo
    if datum_id_YZ in p.datums:
        pickedFaces1 = f.getSequenceFromMask(mask=('[#1 ]', ), )
        p.PartitionFaceByDatumPlane(datumPlane=p.datums[datum_id_YZ], faces=pickedFaces1)
    else:
        print("Errore: Il Datum Plane YZ con ID {} non esiste.".format(datum_id_YZ))

    if datum_id_XZ in p.datums:
        pickedFaces2 = f.getSequenceFromMask(mask=('[#3 ]', ), )
        p.PartitionFaceByDatumPlane(datumPlane=p.datums[datum_id_XZ], faces=pickedFaces2)
    else:
        print("Errore: Il Datum Plane XZ con ID {} non esiste.".format(datum_id_XZ))

    print("Partizionamento completato correttamente.")


# MATERIAL ------------------------------------------------------------------------------

def material_module(E=E_def, NI=NI_def, SY1=SY1_def, EP1=EP1_def, SY2=SY2_def, EP2=EP2_def):
    import material
    import assembly
    import step
    import interaction
    import visualization
    import xyPlot
    import displayGroupOdbToolset as dgo
    import connectorBehavior

    # Material 1 (Steel)
    mdb.models['Model-1'].Material(name='Steel')
    mdb.models['Model-1'].materials['Steel'].Elastic(table=((E, NI), ))
    mdb.models['Model-1'].materials['Steel'].Plastic(table=((SY1, EP1),(SY2,EP2)))

# SECTION-------------------------------------------------------------------------------

def section_module(THK=THK_def):
    import section
    import regionToolset
    import displayGroupMdbToolset as dgm
    import part
    import material
    import assembly
    import step
    import interaction
    import load
    import mesh
    import optimization
    import job
    import sketch
    import visualization
    import xyPlot
    import displayGroupOdbToolset as dgo
    import connectorBehavior

    # Section 1
    mdb.models['Model-1'].HomogeneousShellSection(name='Section-1', 
        preIntegrate=OFF, material='Steel', thicknessType=UNIFORM, 
        thickness=THK, thicknessField='', idealization=NO_IDEALIZATION, 
        poissonDefinition=DEFAULT, thicknessModulus=None, temperature=GRADIENT, 
        useDensity=OFF, integrationRule=SIMPSON, numIntPts=5)

    # Apply section - Create pipe_set
    p = mdb.models['Model-1'].parts['Pipe']
    f = p.faces
    faces = f.getSequenceFromMask(mask=('[#1 ]', ), )
    region = p.Set(faces=faces, name='pipe_set')
    p.SectionAssignment(region=region, sectionName='Section-1', offset=0.0, 
        offsetType=BOTTOM_SURFACE, offsetField='', 
        thicknessAssignment=FROM_SECTION)

# ASSEMBLY--------------------------------------------------------------------------------

def assembly_module(L=L_def):
    import assembly
    import step
    import interaction
    import load
    import mesh
    import optimization
    import job
    import sketch
    import visualization
    import xyPlot
    import displayGroupOdbToolset as dgo
    import connectorBehavior
    
    a = mdb.models['Model-1'].rootAssembly
    p = mdb.models['Model-1'].parts['Pipe']
    
    # Create a reference system
    a.DatumCsysByDefault(CARTESIAN)
    
    # Create an instance
    a.Instance(name='Pipe-1', part=p, dependent=ON)

    # Create fix_set
    e1 = a.instances['Pipe-1'].edges
    edges1 = e1.getSequenceFromMask(mask=('[#1 ]', ), )
    a.Set(edges=edges1, name='fix_set')
    a = mdb.models['Model-1'].rootAssembly
    
    # Create load_set
    e1 = a.instances['Pipe-1'].edges
    edges1 = e1.getSequenceFromMask(mask=('[#2 ]', ), )
    a.Set(edges=edges1, name='load_set')
    a = mdb.models['Model-1'].rootAssembly
    e1 = a.instances['Pipe-1'].edges   
          
    # Create RP2 and RP2_set       
    if 'RP2_set' not in a.sets.keys():
        r2 = a.ReferencePoint(point=(0.0, 0.0, 0.0))
        refPoints2 = a.referencePoints[r2.id]
        a.Set(referencePoints=(refPoints2,), name='RP2_set')  
    
    # Create ext_surf
    s1 = a.instances['Pipe-1'].faces
    side1Faces1 = s1.getSequenceFromMask(mask=('[#1 ]', ), )
    a.Surface(side1Faces=side1Faces1, name='ext_surf')

# STEPS ---------------------------------------------------------------------------------

def steps_module():
    import step
    import interaction
    import load
    import mesh
    import optimization
    import job
    import sketch
    import visualization
    import xyPlot
    import displayGroupOdbToolset as dgo
    import connectorBehavior    

    # Creazione del modello
    m = mdb.models['Model-1']
    
    # STEP 1
    m.StaticStep(adaptiveDampingRatio=0.05, continueDampingFactors=False,
                 name='Step-1', previous='Initial', maxNumInc=200,
                 initialInc=0.1, maxInc=0.1, nlgeom=ON, stabilizationMagnitude=0.001, 
                 stabilizationMethod=DISSIPATED_ENERGY_FRACTION) 

    # STEP 2
    m.StaticStep(name='Step-2', previous='Step-1', 
        description='ausiliary step to relax loads and BCs')

    # Field output
    m.FieldOutputRequest(name='F-Output-1', createStepName='Step-1', variables=('S', 'E', 'U'))
    m.FieldOutputRequest(name='F-Output-2', createStepName='Step-2', variables=('S', 'E', 'U'))


# CONSTRAINTS ----------------------------------------------------------------------------

def constraints_module():
    import section
    import regionToolset
    import displayGroupMdbToolset as dgm
    import part
    import material
    import assembly
    import step
    import interaction
    import sketch
    import visualization
    import xyPlot
    import displayGroupOdbToolset as dgo
    import connectorBehavior
    a = mdb.models['Model-1'].rootAssembly
    
    # Coupling end point    
    region1=a.sets['RP2_set']    
    region2=a.sets['load_set']
    mdb.models['Model-1'].Coupling(name='load_constr', controlPoint=region1, 
        surface=region2, influenceRadius=WHOLE_SURFACE, couplingType=KINEMATIC, 
        localCsys=None, u1=ON, u2=ON, u3=ON, ur1=ON, ur2=ON, ur3=ON)

# AMPLITUDES ------------------------------------------------------------------------

def amplitudes_module():
    import section
    import regionToolset
    import displayGroupMdbToolset as dgm
    import part
    import material
    import assembly
    import step
    import interaction
    import load
    import mesh
    import optimization
    import job
    import sketch
    import visualization
    import xyPlot
    import displayGroupOdbToolset as dgo
    import connectorBehavior
    
    # Compression amplitude
    mdb.models['Model-1'].TabularAmplitude(name='compr_ampl', timeSpan=STEP, 
        smooth=SOLVER_DEFAULT, data=((0.0, 0.0), (0.5, 1.0), (1.0, 1.0)))

    # Curvature amplitude
    mdb.models['Model-1'].TabularAmplitude(name='curvature_ampl', timeSpan=STEP, 
        smooth=SOLVER_DEFAULT, data=((0.0, 0.0), (0.5, 0.0), (1.0, 1.0)))

# LOADS--------------------------------------------------------------------------------

def loads_module(COMPR=COMPR_def, PRESS=PRESS_def):
    import section
    import regionToolset
    import displayGroupMdbToolset as dgm
    import part
    import material
    import assembly
    import step
    import interaction
    import load
    import mesh
    import optimization
    import job
    import sketch
    import visualization
    import xyPlot
    import displayGroupOdbToolset as dgo
    import connectorBehavior

    a = mdb.models['Model-1'].rootAssembly
    
    # External pressure    
    region = a.surfaces['ext_surf']
    mdb.models['Model-1'].Pressure(name='ext_pressure', createStepName='Step-1', 
        region=region, distributionType=UNIFORM, field='', magnitude=PRESS, 
        amplitude=UNSET)

    # Compression load
    region = a.sets['RP2_set']
    mdb.models['Model-1'].ConcentratedForce(name='compression_load', 
        createStepName='Step-1', region=region, cf3=COMPR, 
        amplitude='compr_ampl', distributionType=UNIFORM, field='', 
        localCsys=None)

    # DEACTIVATE LOADS ON STEP-2
    mdb.models['Model-1'].loads['compression_load'].deactivate('Step-2')
    mdb.models['Model-1'].loads['ext_pressure'].deactivate('Step-2')

# BOUNDARY CONDITIONS ----------------------------------------------------------------

def BC_module(CURV=CURV_def):
    import section
    import regionToolset
    import displayGroupMdbToolset as dgm
    import part
    import material
    import assembly
    import step
    import interaction
    import load
    import mesh
    import optimization
    import job
    import sketch
    import visualization
    import xyPlot
    import displayGroupOdbToolset as dgo
    import connectorBehavior
    a = mdb.models['Model-1'].rootAssembly
        
    # Curvature
    a = mdb.models['Model-1'].rootAssembly
    region = a.sets['RP2_set']
    mdb.models['Model-1'].DisplacementBC(name='curvature_BC', 
        createStepName='Step-1', region=region, u1=UNSET, u2=UNSET, u3=UNSET, 
        ur1=CURV, ur2=UNSET, ur3=UNSET, amplitude='curvature_ampl', fixed=OFF, 
        distributionType=UNIFORM, fieldName='', localCsys=None)

    # BC_fix
    mdb.models['Model-1'].DisplacementBC(name='fix_BC', createStepName='Initial',
        region=a.sets['fix_set'], u1=UNSET, u2=UNSET, u3=0.0, ur1=0.0, ur2=0.0, ur3=UNSET,
        amplitude=UNSET, fixed=OFF, distributionType=UNIFORM, fieldName='',
        localCsys=None)

    # BC_load
    mdb.models['Model-1'].DisplacementBC(name='load_BC', createStepName='Initial',
        region=a.sets['RP2_set'], u1=0.0, u2=0.0, u3=UNSET, ur1=UNSET, ur2=UNSET, ur3=0.0,
        amplitude=UNSET, fixed=OFF, distributionType=UNIFORM, fieldName='',
        localCsys=None)
    #----------------------------
    
    # Deactivate curvature at step-2
    mdb.models['Model-1'].boundaryConditions['curvature_BC'].deactivate('Step-2')
    
# MESH -----------------------------------------------------------------------------

def mesh_module(CURVILINEAR_STEP=CURVILINEAR_STEP_def):
    import section
    import regionToolset
    import displayGroupMdbToolset as dgm
    import part
    import material
    import assembly
    import step
    import interaction
    import load
    import mesh
    import optimization
    import job
    import sketch
    import visualization
    import xyPlot
    import displayGroupOdbToolset as dgo
    import connectorBehavior
    
    # Ottieni il modello e la parte
    p = mdb.models['Model-1'].parts['Pipe']
    
    # Seleziona gli edges lungo l'ascissa curvilinea (asse Z)
    edges_z = [edge for edge in p.edges if abs(edge.pointOn[0][2]) >= 0]  # Seleziona tutti gli edge lungo Z
    
    # Imposta il seed variabile lungo la pipeline
    for edge in edges_z:
        p.seedEdgeBySize(edges=[edge], size=CURVILINEAR_STEP, deviationFactor=0.1, minSizeFactor=0.1)
    
    # Genera la mesh
    p.generateMesh()    

# JOB ---------------------------------------------------------------------------

def job_module(run_id, NP=NP_def):
    import section
    import optimization
    import job
    import sketch
    import visualization
    import xyPlot
    import displayGroupOdbToolset as dgo
    import connectorBehavior
    
    # Create Job

    # Costruisci un nome più corto
    #job_name = "job_wt{}_D{}_C{}_c{}_P{}".format(thick_str, diam_str, compr_str, curv_str, press_str)
    job_name = "run_{:04}".format(run_id)
    
    mdb.Job(name=job_name, model='Model-1', description='', type=ANALYSIS, 
        atTime=None, waitMinutes=0, waitHours=0, queue=None, memory=90, 
        memoryUnits=PERCENTAGE, getMemoryFromAnalysis=True, 
        explicitPrecision=SINGLE, nodalOutputPrecision=SINGLE, echoPrint=OFF, 
        modelPrint=OFF, contactPrint=OFF, historyPrint=OFF, userSubroutine='', 
        scratch='', resultsFormat=ODB, multiprocessingMode=DEFAULT, numCpus=NP, 
        numDomains=NP, numGPUs=0)
        
    # Crea una sottocartella se non esiste
    subfolder = 'input_files'    
    if not os.path.exists(subfolder):
        os.makedirs(subfolder)

    # Write input
    mdb.jobs[job_name].writeInput()
    input_path = os.path.join(subfolder, job_name + ".inp")

    # Sposta il file .inp nella nuova sottocartella
    os.rename(job_name + ".inp", input_path)

# -------------------------------------------------------------------------
# Funzione conversione

def pollici_a_mm(pollici):
    return pollici * 25.4

#----------------------------------------------------------------------------
# CHIAMATA FINALE DEL MAIN

if __name__ == "__main__":
    main()

#---------------------------------------------------------------------------



