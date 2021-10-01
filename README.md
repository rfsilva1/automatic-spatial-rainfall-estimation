# Automatic Spatial Rainfall Estimation on Limited Coverage Areas
## Description
This repository contains the code, and the final datasets used for the paper Automatic Spatial Rainfall Estimation on Limited Coverage Areas, by Maria C. Fava, Roberto F. Silva, Gabriela C. Gesualdo, Marcos R. Benso, Eduardo M. Mendiondo, Antonio M. Saraiva, Alexandre C. B. Delbem, and Carlos R. Padovani. We proposed and implemented a framework that automatically calculates the rainfall interpolation using IDW and a cross-validation method to find its optimal hyperparameters. The framework can be implemented on any rainfall dataset, regardless of: (i) the amount of data available; (ii) the quality of the area coverage (station density); (iii) the number of weather stations; and (iv) the existence of missing values. This paper was accepted at the 2021 IEEE MetroAgriFor (2021 IEEE International Workshop on Metrology for Agriculture and Forestry) scientific event. Descriptions of the implementation and the dataset are contained in the paper. The PDF will be available in this repository as soon as the final version of the paper is accepted. The code is composed of saeveral Python scripts.

The dataset used was composed of data from 103 weather stations in a wide geographic location in Brazil with sub-areas containing multiple stations (considered fully coverage areas) and sub-areas containing one or few stations (considered limited coverage areas). The period encompassed by the data was from 2000 to 2015, with daily time, and the dataset contained around 580.000 observations. The Digital Elevation Model used can be download at Embrapa's website: https://www.cnpm.embrapa.br/projetos/relevobr/download/index.htm .

The code was developed by Maria C. Fava.

## Credits for the code:
The code was based on the following:
- Inverse Distance Weighting (IDW) Interpolation IDW for python and R: https://rafatieppo.github.io/post/2018_07_27_idw2pyr/

The authors would like to thank the authors of the code for providing it as an example for the use of the libraries and model implementation. 

The authors would also like to thank all the developers that were and are involved on the development of the following Python libraries: 
- Pandas: https://pandas.pydata.org/
- NumPy: https://numpy.org/
- IPython: https://ipython.org/

Reference of the paper and to cite this repository: 
- The reference will be inserted after the final version of the paper is accepted

## To Do (further research, out of the scope of this paper):
- optimize code for deployment in production
- evaluate the framework on different areas and applications
- evaluate the use of additional interpolation methods
- explore the use of unsupervised and supervised machine learning methods for improving the model's sMAPE
- deploy code on webapp for evaluating different areas and years
- automate data collection from the weather stations
- implement and evaluate additional metrics

## Credits for the dataset:
The authors would like to thank Embrapa Pantanal (Corumba-MS), a Unit of the Brazilian Agricultural Research Corporation for providing the rainfall data used in this research.

## Acknowledgements:
This work was carried out at the Center for Artificial Intelligence (C4AI-USP) with support from the following institutions: São Paulo Research Foundation (FAPESP) Grants \#2019/07665-4 and \#2014/50848-9, IBM Corporation, Coordenação de Aperfeiçoamento de Pessoal de Nível Superior – CAPES (finance code 001), CAPES Grant 16/2014, Conselho Nacional de Desenvolvimento Científico e Tecnológico (CNPq) Grant 465501/2014-1, National Institute of Science and Technology for Climate Change Phase 2 (INCT-II), the graduate program in Hydraulics and Sanitary Engineering (USP-EESC), and regular funding to post-graduate program in Hydraulics and Sanitation of USP.
