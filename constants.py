# Midpoints for ecosystem quality
EQ = [
'Climate change, ecosystem quality, long term',
'Climate change, ecosystem quality, short term',
'Fisheries impact',
'Freshwater acidification',
'Freshwater ecotoxicity, long term',
'Freshwater ecotoxicity, short term',
'Freshwater eutrophication',
'Ionizing radiations, ecosystem quality',
'Land occupation, biodiversity',
'Land transformation, biodiversity',
'Marine acidification, long term',
'Marine acidification, short term',
'Marine ecotoxicity, long term',
'Marine ecotoxicity, short term',
'Marine eutrophication',
'Photochemical ozone formation, ecosystem quality',
'Terrestrial acidification',
'Terrestrial ecotoxicity, long term',
'Terrestrial ecotoxicity, short term',
'Thermally polluted water',
'Water availability, freshwater ecosystem',
'Water availability, terrestrial ecosystem'
]


## Aggregation for EQ
agg_mapping_eq = {'Freshwater ecotoxicity, long term': 'Freshwater ecotoxicity',
 'Freshwater ecotoxicity, short term': 'Freshwater ecotoxicity',
 'Terrestrial acidification': 'Terrestrial acidification',
 'Climate change, ecosystem quality, long term': 'Climate change',
 'Climate change, ecosystem quality, short term': 'Climate change',
 'Freshwater acidification': 'Freshwater acidification',
 'Terrestrial ecotoxicity, long term': 'Other ecotoxicities',
 'Marine ecotoxicity, long term': 'Other ecotoxicities',
 'Terrestrial ecotoxicity, short term': 'Other ecotoxicities',
 'Marine ecotoxicity, short term': 'Other ecotoxicities',
 'Land occupation, biodiversity': 'LULUC',
 'Land transformation, biodiversity': 'LULUC',
 'Water availability, freshwater ecosystem': 'Water',
 'Thermally polluted water': 'Water',
 'Water availability, terrestrial ecosystem': 'Water',
 'Marine eutrophication': 'Eutrophication',
 'Freshwater eutrophication': 'Eutrophication',
 'Marine acidification, long term': 'Marine acidification',
 'Marine acidification, short term': 'Marine acidification',
 'Photochemical ozone formation, ecosystem quality': 'Smog',
 'Fisheries impact': 'Fisheries impact',
 'Ionizing radiations, ecosystem quality': 'Ionizing radiations'}


# Midpoints for human health
HH = [
'Climate change, human health, long term',
'Climate change, human health, short term',
'Human toxicity cancer, long term',
'Human toxicity cancer, short term',
'Human toxicity non-cancer, long term',
'Human toxicity non-cancer, short term',
'Ionizing radiations, human health',
'Ozone layer depletion',
'Particulate matter formation',
'Photochemical ozone formation, human health',
'Water availability, human health'
]


## Aggregation for HH
agg_mapping_hh = {'Climate change, human health, long term': 'Climate change',
 'Climate change, human health, short term': 'Climate change',
 'Human toxicity cancer, long term': 'Human toxicity, cancer',
 'Human toxicity cancer, short term': 'Human toxicity, cancer',
 'Human toxicity non-cancer, long term': 'Human toxicity, non-cancer',
 'Human toxicity non-cancer, short term': 'Human toxicity, non-cancer',
 'Ionizing radiations, human health': 'Ionizing radiations',
 'Ozone layer depletion': 'Ozone layer depletion',
 'Particulate matter formation': 'Particulate matter',
 'Photochemical ozone formation, human health': 'Smog',
 'Water availability, human health': 'Water availability'}


# Define custom colors for metals
custom_metal_colors = {
    "Copper": "#a50026",
    "Aluminium": "#d73027",
    "Nickel": "#f46d43",
    "Silicon": "#fee090",
    "Graphite": "#e0f3f8",
    "Iridium": "#4575b4",
    "PGMs": "#313695",
    "Vanadium": "#4575b4",
    "Other": "#A9A9A9", # Generic color for agg categories
}

custom_metal_roe_colors = {
    "Copper": "#a50026",
    "Aluminium": "#d73027",
    "Nickel": "#f46d43",
    "Chromium": "#fdae61",
    "Zinc": "#fee090",
    "Lead": "#e0f3f8",
    "Magnesium": "#abd9e9",
    "Silicon": "#74add1",
    "Iridium": "#4575b4",
    "PGMs": "#313695",
    "Other": "#A9A9A9"
}


# Define custom colors for technologies
custom_tech_colors = {
    "Electricity networks": "#8c510a",
    "Solar PV": "#d8b365",
    "Electric vehicles": "#f6e8c3",
    "Wind": "#f5f5f5",
    "Low emissions power generation": "#c7eae5",
    "Hydrogen technologies": "#5ab4ac",
    "Grid battery storage": "#01665e",
}


metal_map = {
    "Dysprosium":  "REE",
    "Lanthanum": "REE",
    "Neodymium":   "REE",
    "Praseodymium": "REE",
    "Terbium":     "REE",
    "Yttrium":    "REE",
    "Iridium":     "PGMs"
}