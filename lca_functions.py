from brightway2 import *
import bw2data as bd
import pandas as pd
import numpy as np
import os


def setup_activities_dict(df, scenario_prefix):
    """
    Create a dictionary mapping (scenario, year, metal, technology) to Brightway activities.
    """
    activities_dict = {}

    for index, row in df.iterrows():
        metal = row["Metal"]
        market = row["Market"]
        product = row["Reference Product"]
        location = row["Location"]

        for year in years:
            database_name = f"{scenario_prefix}_{year} regionalized"  # Select the appropriate database
            activity_name = (scenario_prefix, year, metal, row["Technology"])
            search_criteria = market

            try:
                activities = Database(database_name).search(search_criteria, limit=1000)
                filtered_activities = [
                    i for i in activities if i["name"] == search_criteria
                                             and i["location"] == location
                                             and i["reference product"] == product
                ]

                if filtered_activities:
                    activities_dict[activity_name] = filtered_activities[0]
                else:
                    activities_dict[activity_name] = None
            except:
                activities_dict[activity_name] = None

    return activities_dict


def calculate_lca(df, activities_dict, scenario_prefix, lcia_methods):
    """
    Perform LCA calculations for different scenarios, years, metals, and technologies.
    Returns a DataFrame with results disaggregated.
    """
    results = []

    for index, row in df.iterrows():
        metal = row["Metal"]
        technology = row["Technology"]

        for year in years:
            quantity = row[str(year)]  # Get the metal quantity for the year
            activity_name = (scenario_prefix, year, metal, technology)
            activity = activities_dict.get(activity_name, None)

            if activity:
                impact_results = {}

                for method in lcia_methods:
                    try:
                        lca = LCA({activity: quantity}, method)
                        lca.lci()
                        lca.lcia()
                        impact_results[method[2]] = lca.score
                    except:
                        impact_results[method[2]] = np.nan  # Assign NaN if calculation fails

                results.append({
                    "Scenario": scenario_prefix,
                    "Year": year,
                    "Metal": metal,
                    "Technology": technology,
                    **impact_results
                })

    return pd.DataFrame(results)


def calculate_lca_optimized(df, activities_dict, scenario_prefix, lcia_methods):
    """
    Optimized LCA calculations for different scenarios, years, metals, and technologies.
    """
    results = []

    for index, row in df.iterrows():
        metal = row["Metal"]
        technology = row["Technology"]

        for year in years:
            quantity = row[str(year)]  # Get the metal quantity for the year
            activity_name = (scenario_prefix, year, metal, technology)
            activity = activities_dict.get(activity_name, None)

            if activity:
                impact_results = {}

                try:
                    # Initialize LCA object once per activity
                    lca = LCA({activity: quantity}, lcia_methods[0])  # Use first method as reference
                    lca.lci()

                    for method in lcia_methods:
                        lca.switch_method(method)  # Switch to a new impact method without recalculating LCI
                        lca.lcia()
                        impact_results[method[2]] = lca.score

                except:
                    for method in lcia_methods:
                        impact_results[method[2]] = np.nan  # Assign NaN if calculation fails

                results.append({
                    "Scenario": scenario_prefix,
                    "Year": year,
                    "Metal": metal,
                    "Technology": technology,
                    **impact_results
                })

    return pd.DataFrame(results)