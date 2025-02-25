# plca_metals 📦

Prospective Life Cycle Assessment (pLCA) of metals in the energy transition

This repository contains the code and data associated with the publication:
"Metals for the Energy Transition: A Heavy Environmental Burden to Life?"

## 📌 Features
- Regionalized prospective LCI generation for metals
- Custom metal scenarios developed by Marguerite Fauroux
- Coupling with IEA's Stated Policies and Net Zero Scenarios
- LCA calculations using [IMPACT World+ 2.1 version](https://www.impactworldplus.org/)

## 📦 Dependencies

This module relies on several packages for LCA calculations:
- [brightway2](https://docs.brightway.dev/en/legacy/index.html) – An open-source LCA framework 
- [premise](https://github.com/polca/premise) – A Python module to couple IAMs outputs with LCA
- [premise-community-scenario](https://github.com/premise-community-scenarios/metal-prospective-scenarios) - Custom metal scenarios developed by Marguerite Fauroux
- [regiopremise](https://github.com/matthieu-str/Regiopremise/tree/master) – A Python module to enhance premise-generated database with regionalization 
  - Relies on [Regioinvent](https://github.com/CIRAIG/Regioinvent)

## 📄 License

This repository is licensed under the BSD 3-Clause License. See the LICENSE file for details.

## 📬 Contact

For questions, feel free to open an issue or reach out via email to marin.pellan@polymtl.ca
