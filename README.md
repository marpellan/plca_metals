# plca_metals 📦

Prospective Life Cycle Assessment (pLCA) of metals in the energy transition

This repository contains the code and data associated with the publication:
"Metals for the Energy Transition: A Heavy Environmental Burden to Life?"

## 📌 Features
- Use of IEA's Stated Policies and Net Zero Scenarios for an estimate of the future demand for 35 metals
- Regionalized prospective LCI database generation 
- Custom metal scenarios developed by Marguerite Fauroux. 
They include the evolution of secondary production in the supply of aluminum, copper, cobalt, nickel and lithium. 
The evolution of the electricity mix and the efficiency of aluminum smelters in China were also modeled.
- Use of IEA's Stated Policies and Net Zero Scenarios for an estimate of the future demand for 35 metals
- LCA calculations using [IMPACT World+ 2.1 version](https://www.impactworldplus.org/)


## 📦 Dependencies

This module relies on several packages for LCA calculations:
- [brightway2](https://docs.brightway.dev/en/legacy/index.html) – An open-source LCA framework 
- [premise](https://github.com/polca/premise) – A Python module to couple IAMs outputs with LCA
- [premise-community-scenario](https://github.com/premise-community-scenarios/metal-prospective-scenarios) - Custom metal scenarios developed by Marguerite Fauroux
- [regiopremise](https://github.com/matthieu-str/Regiopremise/tree/master) – A Python module to enhance premise-generated database with regionalization 
  - Relies on [Regioinvent](https://github.com/CIRAIG/Regioinvent)

Additionally, the [pyam](https://pyam-iamc.readthedocs.io/en/stable/) package is used to fetch SSP and IAM data,
and transform the IEA data into the IAM-format.

## 📄 License

This repository is licensed under the BSD 3-Clause License. See the LICENSE file for details.

## 📬 Contact

For questions, feel free to open an issue or reach out via email to marin.pellan@polymtl.ca
