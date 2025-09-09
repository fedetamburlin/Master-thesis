## This files are the pipeline of the building of the surrogate model:
00. Design of experiments.
01. Creation of the input file for the FEM solver Abaqus (abaqus noGUI=FileName).
02. Run the analysis (abaqus python FileName).
03. Data extraction from the output files.
04. Sort and clean extracted data.
05. Create Area Profiles and scalar parameter diameter reduction (DR), area reduction (AR). Save it in tables, create plots and a summary table.
06. Prediction 1D interpolating a curvature profile in a single scenario
07. Metamodel Gaussian Process (Kriging) - Machine Learning approach
08. Metamodel Multi-Layer Perceptron (MLP) - Neural Network approach
