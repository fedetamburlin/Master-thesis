# Master's thesis — Mechanical surrogate models

> **Interactive demo of the surrogate models:** https://pipe-analyzer.onrender.com/
> **Deployment code:** https://github.com/fedetamburlin/Pipe_Analyzer

Scripts and notebooks from my Master's thesis in Mathematical Engineering: a
surrogate model of the cross-section response of steel pipes, built from
high-fidelity Abaqus FEM simulations and trained with Gaussian Process
(Kriging) and Multi-Layer Perceptron regressors.

## Pipeline

00. Design of experiments.
01. Creation of the input file for the FEM solver Abaqus (`abaqus noGUI=FileName`).
02. Run the analysis (`abaqus python FileName`).
03. Data extraction from the output files.
04. Sort and clean extracted data.
05. Create Area Profiles and scalar parameters diameter reduction (DR), area reduction (AR). Save them in tables, create plots and a summary table.
06. Prediction 1D interpolating a curvature profile in a single scenario.
07. Metamodel Gaussian Process (Kriging) — Machine Learning approach.
08. Metamodel Multi-Layer Perceptron (MLP) — Neural Network approach.

The trained artifacts and the web app that serves them live in the
[deployment repository](https://github.com/fedetamburlin/Pipe_Analyzer).

## Data

- `Parameters_DoE.csv` — design of experiments.
- `AR_DR_results.csv` — area/diameter reduction dataset used by the surrogates.
- `Tesi_Tamburlin.pdf` — the thesis.

## License

The code in this repository is released under the MIT License (see [LICENSE](LICENSE)).
The thesis text and figures in `Tesi_Tamburlin.pdf` are licensed under
[CC BY-NC-ND 4.0](https://creativecommons.org/licenses/by-nc-nd/4.0/).
