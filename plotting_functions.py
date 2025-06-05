import pandas as pd
import numpy as np
import os
import math
# Matplotlib
import matplotlib.pyplot as plt
import matplotlib.cm as cm
from matplotlib import rcParams
from matplotlib.lines import Line2D
import seaborn as sns
import plotly.graph_objects as go


### SET GLOBAL MATPLOTLIB PARAMS
rcParams['pdf.fonttype'] = 42  # to Ensure TrueType fonts are embedded
rcParams['ps.fonttype'] = 42
rcParams['font.family'] = 'arial'
rcParams['font.size'] = 10
rcParams['axes.labelsize'] = 10
rcParams['legend.fontsize'] = 9
rcParams['xtick.labelsize'] = 9
rcParams['ytick.labelsize'] = 9
rcParams['axes.titlesize'] = 12

# TO AVOID CONFLICTS
sns.reset_orig()


### FUNCTIONS
def plot_metal_demand_scenarios(df_nze, df_sps, save_path, custom_colors_dict=None):
    """
    Plot 2x2 stacked area charts of metal demand by Technology and Metal
    for NZE and SPS scenarios, with threshold-based grouping for Metal.

    Layout:
    Top row = SPS, Bottom row = NZE
    Left column = Technology, Right column = Metal
    """
    # --- Matplotlib style ---
    rcParams['pdf.fonttype'] = 42
    rcParams['ps.fonttype'] = 42
    rcParams['font.family'] = 'arial'
    rcParams['font.size'] = 10
    rcParams['axes.labelsize'] = 10
    rcParams['legend.fontsize'] = 9
    rcParams['xtick.labelsize'] = 9
    rcParams['ytick.labelsize'] = 9
    rcParams['axes.titlesize'] = 12
    rcParams['text.usetex'] = False
    sns.reset_orig()

    # --- Prepare data ---
    df_nze = df_nze.copy()
    df_sps = df_sps.copy()
    df_nze['Scenario'] = 'NZE'
    df_sps['Scenario'] = 'SPS'
    df_all = pd.concat([df_nze, df_sps], ignore_index=True)

    year_cols = [col for col in df_all.columns if col.isdigit()]
    df_long = df_all.melt(id_vars=['Metal', 'Technology', 'Scenario'],
                          value_vars=year_cols, var_name='Year', value_name='Demand')
    df_long['Year'] = df_long['Year'].astype(int)

    fig, axs = plt.subplots(2, 2, figsize=(10, 6), sharex=True)
    plt.subplots_adjust(hspace=0.3, wspace=0.2)

    handles_dict = {'Technology': [], 'Metal': []}
    labels_dict = {'Technology': [], 'Metal': []}

    # Rows: SPS (0), NZE (1); Cols: Technology (0), Metal (1)
    for row_i, scenario in enumerate(['SPS', 'NZE']):
        df_scenario = df_long[df_long['Scenario'] == scenario]
        for col_j, group_by in enumerate(['Technology', 'Metal']):
            ax = axs[row_i, col_j]
            df_grouped = df_scenario.groupby(['Year', group_by])['Demand'].sum().reset_index()

            # Threshold logic for metals
            if group_by == 'Metal':
                total_contrib = df_grouped.groupby(group_by)['Demand'].sum()
                threshold = 0.01
                significant = total_contrib[total_contrib / total_contrib.sum() >= threshold].index
                df_grouped[group_by] = df_grouped[group_by].apply(lambda x: x if x in significant else 'Others')

            df_pivot = df_grouped.pivot_table(index='Year', columns=group_by, values='Demand', aggfunc='sum').fillna(0)
            sorted_cols = df_pivot.loc[df_pivot.index.min()].sort_values(ascending=False).index
            df_pivot = df_pivot[sorted_cols]

            categories = df_pivot.columns.tolist()
            if custom_colors_dict and group_by in custom_colors_dict:
                color_dict = {cat: custom_colors_dict[group_by].get(cat, 'gray') for cat in categories}
                colors = [color_dict[cat] for cat in categories]
            else:
                cmap = cm.get_cmap('tab20', len(categories))
                colors = [cmap(k) for k in range(len(categories))]

            ax.stackplot(df_pivot.index, df_pivot.T, labels=categories, colors=colors, alpha=0.8)
            ax.set_title(f"{scenario} - {group_by}", fontsize=10)
            if row_i == 1:
                ax.set_xlabel("")
            if col_j == 0:
                ax.set_ylabel("kg")

            handles, labels = ax.get_legend_handles_labels()
            handles_dict[group_by] = handles
            labels_dict[group_by] = labels

    # Shared legends
    fig.legend(handles_dict['Technology'], labels_dict['Technology'],
               loc="lower left", bbox_to_anchor=(0.15, -0.28), fontsize=9)
    fig.legend(handles_dict['Metal'], labels_dict['Metal'],
               loc="lower right", bbox_to_anchor=(0.85, -0.28), fontsize=9)

    fig.savefig(f"{save_path}.pdf", dpi=600, bbox_inches="tight")
    fig.savefig(f"{save_path}.png", dpi=600, bbox_inches="tight")
    plt.close()


def plot_demand_vs_specific_impacts(lca_df, demand_df, save_path=None, show=False, ncols=4):
    """
    Generate a multi-panel plot of indexed LCA impacts and metal demand (base 2023 = 100).
    """
    # ---- Preprocess LCA ----
    lca_grouped = lca_df.groupby(["Year", "Metal"])[
        ["Total human health", "Total ecosystem quality"]].sum().reset_index()
    lca_melted = lca_grouped.melt(id_vars=["Year", "Metal"],
                                  value_vars=["Total human health", "Total ecosystem quality"],
                                  var_name="Variable", value_name="Value")

    # ---- Preprocess Demand ----
    demand_melted = demand_df.melt(id_vars=["Year", "Metal"],
                                   value_vars=["Energy transition (kt)", "Rest of the economy (kt)"],
                                   var_name="Variable", value_name="Value")

    # ---- Merge and Normalize ----
    combined_df = pd.concat([lca_melted, demand_melted], ignore_index=True)
    base_2023 = combined_df[combined_df["Year"] == 2023].set_index(["Metal", "Variable"])["Value"]
    combined_df["Base_2023"] = combined_df.set_index(["Metal", "Variable"]).index.map(base_2023)
    combined_df["Value_base100"] = combined_df["Value"] / combined_df["Base_2023"] * 100

    # ---- Plot settings ----
    rcParams['pdf.fonttype'] = 42  # to Ensure TrueType fonts are embedded
    rcParams['ps.fonttype'] = 42
    rcParams['font.family'] = 'arial'
    rcParams['font.size'] = 10
    rcParams['axes.labelsize'] = 10
    rcParams['legend.fontsize'] = 9
    rcParams['xtick.labelsize'] = 9
    rcParams['ytick.labelsize'] = 9
    rcParams['axes.titlesize'] = 12
    sns.reset_orig()

    colors = {
        "Total human health": "#a6dba0",  # Blue
        "Total ecosystem quality": "#008837",  # Orange
        "Energy transition (kt)": "#c2a5cf",  # Green
        "Rest of the economy (kt)": "#7b3294"  # Red
    }

    metals = combined_df['Metal'].unique()
    n = len(metals)
    nrows = math.ceil(n / ncols)
    fig, axes = plt.subplots(nrows, ncols, figsize=(ncols * 4, nrows * 3), squeeze=False)

    # ---- Plot each metal ----
    for idx, metal in enumerate(metals):
        r, c = divmod(idx, ncols)
        ax = axes[r][c]
        sub = combined_df[combined_df['Metal'] == metal]
        for var, color in colors.items():
            sub_var = sub[sub["Variable"] == var]
            linestyle = '--' if "kt" in var else '-'  # Dashed for demand, solid for LCA
            ax.plot(sub_var['Year'], sub_var['Value_base100'], marker='o', linestyle=linestyle, label=var, color=color)
        ax.set_title(metal)
        ax.set_xlabel('')
        ax.set_ylabel('Index (2023 = 100)')

    # ---- Shared legend in empty panel ----
    handles = [Line2D([0], [0], color=color, marker='o', label=label) for label, color in colors.items()]
    # Hide unused axes and place legend if any empty subplot
    # ---- Shared legend in empty panel if one exists ----
    handles = [Line2D([0], [0], color=color, marker='o', label=label) for label, color in colors.items()]

    # Indices of unused subplots (e.g., when n < nrows * ncols)
    for idx in range(n, nrows * ncols):
        r, c = divmod(idx, ncols)
        axes[r][c].axis('off')
        if idx == n:  # Only in the first unused subplot
            legend = axes[r][c].legend(
                handles=handles,
                loc='lower right',
                frameon=True,
                edgecolor='black',
                facecolor='white',
                fontsize=12,
                markerscale=1.5,
                handlelength=2.0,
                borderpad=1.0
            )
            legend.get_frame().set_linewidth(1.0)

    plt.tight_layout()

    if save_path:
        fig.savefig(f"{save_path}.pdf", format='pdf', dpi=600)
        # Optionally add PNG
        # fig.savefig(f"{save_path}.png", format='png', dpi=300)

    if show:
        plt.show()
    plt.close()


def plot_metal_lca_impacts(df, value_cols, group_by_options, titles, y_labels, custom_colors_dict, save_path):
    """
    Create a 2x2 grid of stacked area plots: rows = EQ/HH, cols = Technology/Metal.
    Separate legends are added below for each group_by.
    """

    rcParams['pdf.fonttype'] = 42
    rcParams['ps.fonttype'] = 42
    rcParams['font.family'] = 'arial'
    rcParams['font.size'] = 10
    rcParams['axes.labelsize'] = 10
    rcParams['legend.fontsize'] = 9
    rcParams['xtick.labelsize'] = 9
    rcParams['ytick.labelsize'] = 9
    rcParams['axes.titlesize'] = 12
    rcParams['text.usetex'] = False

    fig, axs = plt.subplots(2, 2, figsize=(10, 6), sharex=True)
    plt.subplots_adjust(hspace=0.3, wspace=0.2)

    all_handles = {"Technology": [], "Metal": []}
    all_labels = {"Technology": [], "Metal": []}

    for i, value_col in enumerate(value_cols):  # 0 = EQ, 1 = HH
        for j, group_by in enumerate(group_by_options):  # 0 = Technology, 1 = Metal
            ax = axs[i, j]
            df_grouped = df.groupby(["Year", group_by])[value_col].sum().reset_index()

            # Optional thresholding
            if group_by == "Metal":
                total_contributions = df_grouped.groupby(group_by)[value_col].sum()
                threshold = 0.01
                significant = total_contributions[total_contributions / total_contributions.sum() >= threshold].index
                df_grouped[group_by] = df_grouped[group_by].apply(lambda x: x if x in significant else "Others")

            df_pivot = df_grouped.pivot_table(index="Year", columns=group_by, values=value_col, aggfunc="sum")
            sorted_categories = df_pivot.loc[df_pivot.index.min()].sort_values(ascending=False).index
            df_pivot = df_pivot[sorted_categories]

            unique_categories = df_pivot.columns
            custom_colors = custom_colors_dict.get(group_by, {})
            if custom_colors:
                color_dict = {cat: custom_colors.get(cat, "gray") for cat in unique_categories}
            else:
                cmap = cm.get_cmap("tab20", len(unique_categories))
                color_dict = {cat: cmap(k) for k, cat in enumerate(unique_categories)}

            colors = [color_dict.get(cat, "gray") for cat in df_pivot.columns]
            ax.stackplot(df_pivot.index, df_pivot.T, labels=df_pivot.columns, colors=colors, alpha=0.8)
            ax.set_title(titles[i][j], fontsize=10)
            ax.set_ylabel(y_labels[i])
            ax.tick_params(labelsize=8)
            ax.tick_params(labelbottom=True)

            # Capture legend elements
            handles, labels = ax.get_legend_handles_labels()
            all_handles[group_by] = handles
            all_labels[group_by] = labels

    # Shared legends below the plots
    tech_legend = fig.legend(
        all_handles["Technology"], all_labels["Technology"],
        loc="lower left", bbox_to_anchor=(0.2, -0.25), ncol=1, fontsize=10, title_fontsize=9
    )
    metal_legend = fig.legend(
        all_handles["Metal"], all_labels["Metal"],
        loc="lower right", bbox_to_anchor=(0.8, -0.25), ncol=1, fontsize=10, title_fontsize=9
    )

    # Save
    fig.savefig(f"{save_path}.pdf", format="pdf", dpi=600, bbox_inches="tight")
    fig.savefig(f"{save_path}.png", format="png", dpi=600, bbox_inches="tight")
    plt.show()


def plot_midpoint_contribution(df, impact_columns, total_col, title, y_label="Percentage contribution (%)",
                               mapping_dict=None, threshold=0.01, save_path="plots/stacked_bar"):
    """
    Generate a stacked bar plot showing the contribution of different midpoint indicators to the total impact.
    Contributors below a threshold are grouped into "Others".

    Parameters:
    - df: DataFrame with data
    - impact_columns: List of original midpoint impact indicators
    - total_col: Column containing the total impact for normalization
    - title: Plot title
    - y_label: Label for Y-axis
    - mapping_dict: Dictionary mapping original categories to aggregated ones
    - threshold: Minimum percentage contribution to remain separate
    - save_path: Base filename for saving plots

    Outputs:
    - Saves PDF and PNG versions of the figure
    """

    from constants import mp_color_dict

    # Font and style setup
    rcParams['pdf.fonttype'] = 42
    rcParams['ps.fonttype'] = 42
    rcParams['font.family'] = 'arial'
    rcParams['font.size'] = 10
    rcParams['axes.labelsize'] = 10
    rcParams['legend.fontsize'] = 9
    rcParams['xtick.labelsize'] = 9
    rcParams['ytick.labelsize'] = 9
    rcParams['axes.titlesize'] = 12

    os.makedirs(os.path.dirname(save_path), exist_ok=True)

    # Step 1: Aggregate impact columns if a mapping is provided
    if mapping_dict:
        agg_df = pd.DataFrame(index=df.index)
        for original, aggregated in mapping_dict.items():
            if original in df.columns:
                if aggregated not in agg_df.columns:
                    agg_df[aggregated] = df[original]
                else:
                    agg_df[aggregated] += df[original]
        df = pd.concat([df.drop(columns=[col for col in impact_columns if col in df.columns]), agg_df], axis=1)
        impact_columns = sorted(set(mapping_dict.values()))

    # Step 2: Aggregate by year
    df_grouped = df.groupby("Year")[impact_columns + [total_col]].sum()

    # Step 3: Normalize to percentage
    df_percent = df_grouped[impact_columns].div(df_grouped[total_col], axis=0) * 100

    # Step 4: Apply threshold and group small ones into "Others"
    total_contributions = df_percent.mean()
    significant_categories = total_contributions[total_contributions >= threshold * 100].index.tolist()
    df_percent["Others"] = df_percent.drop(columns=significant_categories).sum(axis=1)
    df_percent = df_percent[significant_categories + ["Others"]]

    # Step 5: Sort categories by first year
    first_year = df_percent.index.min()
    sorted_categories = df_percent.loc[first_year].sort_values(ascending=False).index
    df_percent = df_percent[sorted_categories]

    # Step 6: Fixed color dictionary
    mp_color_dict = mp_color_dict
    color_dict = {cat: mp_color_dict.get(cat, "#BBBBBB") for cat in df_percent.columns}

    # Step 7: Plot
    fig, ax = plt.subplots(figsize=(7.2, 5))
    colors = [color_dict[col] for col in df_percent.columns]
    df_percent.plot(kind="bar", stacked=True, color=colors, ax=ax, width=0.8)

    ax.set_ylabel(y_label, fontsize=10)
    ax.set_xlabel("")
    ax.set_xticklabels(df_percent.index, rotation=360)

    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.15), ncol=3, fontsize=8, frameon=False)

    plt.tight_layout()
    plt.savefig(f"{save_path}.pdf", format="pdf", dpi=600)
    plt.savefig(f"{save_path}.png", format="png", dpi=600)
    plt.show()


def plot_cumulative_midpoint_contribution(df, impact_columns, total_col, title,
                                          y_label="Percentage contribution (%)",
                                          mapping_dict=None, threshold=0.01,
                                          save_path="plots/cumulative_midpoint"):
    """
    Generate a cumulative bar plot of midpoint contributions with error bars (min/max over time).
    Contributors below a threshold are grouped into "Others".

    Parameters:
    - df: DataFrame with midpoint and total values
    - impact_columns: Original midpoint columns (pre-aggregation)
    - total_col: Name of the column with total impact values
    - title: Plot title
    - y_label: Y-axis label
    - mapping_dict: Dictionary to aggregate original midpoint columns into fewer categories
    - threshold: Minimum contribution to appear individually
    - save_path: Path prefix for saving plots (without extension)

    Outputs:
    - Saves PDF and PNG plots
    """

    from constants import mp_color_dict

    # Font settings
    rcParams['pdf.fonttype'] = 42
    rcParams['ps.fonttype'] = 42
    rcParams['font.family'] = 'arial'
    rcParams['font.size'] = 10
    rcParams['axes.labelsize'] = 10
    rcParams['legend.fontsize'] = 9
    rcParams['xtick.labelsize'] = 9
    rcParams['ytick.labelsize'] = 9
    rcParams['axes.titlesize'] = 12

    os.makedirs(os.path.dirname(save_path), exist_ok=True)

    # Step 1: Aggregate midpoint categories if mapping provided
    if mapping_dict:
        agg_df = pd.DataFrame(index=df.index)
        for orig, agg in mapping_dict.items():
            if orig in df.columns:
                if agg not in agg_df.columns:
                    agg_df[agg] = df[orig]
                else:
                    agg_df[agg] += df[orig]
        df = pd.concat([df.drop(columns=[col for col in impact_columns if col in df.columns]), agg_df], axis=1)
        impact_columns = sorted(set(mapping_dict.values()))

    # Step 2: Group by year
    df_grouped = df.groupby("Year")[impact_columns + [total_col]].sum()

    # Step 3: Normalize by total
    df_percent = df_grouped[impact_columns].div(df_grouped[total_col], axis=0) * 100

    # Step 4: Compute stats
    mean_contributions = df_percent.mean()
    min_contributions = df_percent.min()
    max_contributions = df_percent.max()

    # Step 5: Group small categories into "Others"
    significant_categories = mean_contributions[mean_contributions >= threshold * 100].index.tolist()
    df_percent["Others"] = df_percent.drop(columns=significant_categories).sum(axis=1)
    mean_contributions["Others"] = df_percent["Others"].mean()
    min_contributions["Others"] = df_percent["Others"].min()
    max_contributions["Others"] = df_percent["Others"].max()

    mean_contributions = mean_contributions[significant_categories + ["Others"]]
    min_contributions = min_contributions[significant_categories + ["Others"]]
    max_contributions = max_contributions[significant_categories + ["Others"]]

    # Step 6: Sort
    sorted_categories = mean_contributions.sort_values(ascending=False).index
    mean_contributions = mean_contributions[sorted_categories]
    min_contributions = min_contributions[sorted_categories]
    max_contributions = max_contributions[sorted_categories]

    # Step 7: Fixed color mapping
    mp_color_dict = mp_color_dict
    color_dict = {cat: mp_color_dict.get(cat, "#BBBBBB") for cat in sorted_categories}

    # Step 8: Plot
    fig, ax = plt.subplots(figsize=(9, 5))
    x_positions = np.arange(len(sorted_categories))
    colors = [color_dict[col] for col in sorted_categories]

    # Bars
    bars = ax.bar(x_positions, mean_contributions, color=colors, alpha=0.8)

    # Error bars
    ax.errorbar(
        x_positions, mean_contributions,
        yerr=[mean_contributions - min_contributions, max_contributions - mean_contributions],
        fmt='none', ecolor='black', capsize=4, elinewidth=1
    )

    # Labels
    ax.set_ylabel(y_label, fontsize=10)
    ax.set_xticks(x_positions)
    ax.set_xticklabels(sorted_categories, rotation=45, ha="right", fontsize=8)

    plt.tight_layout()
    plt.savefig(f"{save_path}.pdf", format="pdf", dpi=600)
    plt.savefig(f"{save_path}.png", format="png", dpi=600)
    plt.show()


def create_sankey(
    df,
    total_col,
    impact_columns,
    #title,
    save_path,
    agg_mapping=None,
    metal_mapping=None
):
    """
    Sankey: Metals → Technologies → (aggregated) Midpoints,
    with optional aggregation of both metals and midpoint indicators.

    Parameters
    ----------
    df : pd.DataFrame
        must contain columns ["Metal","Technology", *impact_columns, total_col]
    total_col : str
        e.g. 'Total ecosystem quality' or 'Total human health'
    impact_columns : list[str]
        your detailed midpoint columns (EQ or HH)
    title : str
    save_path : str
        path WITHOUT extension; .html (and optionally .png) will be added
    agg_mapping : dict | None
        maps each detailed midpoint → its aggregated label
    metal_mapping : dict | None
        maps each raw metal name → its aggregated metal group
        e.g. {"Dysprosium":"REE", "Neodymium":"REE", "Terbium":"REE",
               "Iridium":"PGM",   "Platinum":"PGM"}
    """
    os.makedirs(os.path.dirname(save_path), exist_ok=True)

    rcParams['pdf.fonttype'] = 42
    rcParams['ps.fonttype'] = 42
    rcParams['font.family'] = 'arial'
    rcParams['font.size'] = 10
    rcParams['axes.labelsize'] = 10
    rcParams['legend.fontsize'] = 9
    rcParams['xtick.labelsize'] = 9
    rcParams['ytick.labelsize'] = 9
    rcParams['axes.titlesize'] = 12
    rcParams['text.usetex'] = False

    # 0) apply metal aggregation if requested
    df_proc = df.copy()
    if metal_mapping:
        df_proc["Metal"] = df_proc["Metal"].map(metal_mapping).fillna(df_proc["Metal"])

    # 1) sum over years (or whatever time dim you have)
    df_cum = (
        df_proc
        .groupby(["Metal", "Technology"])[impact_columns + [total_col]]
        .sum()
        .reset_index()
    )

    # 2) pick off your metals (alphabetical!) and techs
    all_metals = sorted(df_cum["Metal"].unique().tolist())
    all_techs  = df_cum["Technology"].unique().tolist()

    # 3) build your (aggregated) midpoint list
    if agg_mapping:
        midpoints = []
        for m in impact_columns:
            agg = agg_mapping.get(m)
            if agg and agg not in midpoints:
                midpoints.append(agg)
        all_midpoints = midpoints
    else:
        all_midpoints = impact_columns

    # 4) assemble nodes
    node_labels = all_metals + all_techs + all_midpoints
    node_colors = (
        ["#d53e4f"] * len(all_metals) +
        ["#5ab4ac"] * len(all_techs)  +
        ["#3288bd"] * len(all_midpoints)
    )
    node_dict = {label: idx for idx, label in enumerate(node_labels)}

    # 5) build metal→tech links
    sources = []
    targets = []
    values  = []
    for _, row in df_cum.iterrows():
        sources.append(node_dict[row["Metal"]])
        targets.append(node_dict[row["Technology"]])
        values.append(row[total_col])

    # 6) build tech→midpoint links (summing all detailed columns into each agg‐bucket)
    for tech in all_techs:
        block = df_cum[df_cum["Technology"] == tech]
        for mid in all_midpoints:
            if agg_mapping:
                cols = [m for m in impact_columns if agg_mapping.get(m) == mid]
                flow = block[cols].sum().sum()
            else:
                flow = block[mid].sum()
            sources.append(node_dict[tech])
            targets.append(node_dict[mid])
            values.append(flow)

    # 7) x positions (fixed columns)
    x_pos = (
        [0.1] * len(all_metals) +
        [0.5] * len(all_techs)  +
        [0.9] * len(all_midpoints)
    )

    # 8) draw
    fig = go.Figure(go.Sankey(
        arrangement="snap",  # or "fixed"
        node=dict(
            pad=15, thickness=20, line=dict(color="black", width=1),
            label=node_labels, color=node_colors, x=x_pos,
        ),
        link=dict(source=sources, target=targets, value=values)
    ))
    fig.update_layout(
        #title_text=title,
        font_family="Arial", font_color='black', font_size=16,
        width=1200, height=800,
        paper_bgcolor="white", plot_bgcolor="white"
    )

    # 9) save outputs
    fig.write_html(f"{save_path}.html")
    fig.write_image(f"{save_path}.pdf", format="pdf", width=1200, height=800, scale=2)

    return fig


def plot_lineplot_logscale(df, save_path=None, show=False):

    rcParams['pdf.fonttype'] = 42
    rcParams['ps.fonttype'] = 42
    rcParams['font.family'] = 'Arial'
    rcParams['font.size'] = 10
    rcParams['axes.labelsize'] = 10
    rcParams['legend.fontsize'] = 9
    rcParams['xtick.labelsize'] = 9
    rcParams['ytick.labelsize'] = 9
    rcParams['axes.titlesize'] = 12

    df["Year"] = pd.to_numeric(df["Year"], errors="coerce")
    pivot_df = df.pivot_table(
        index=["Year", "Sector", "Impact category"],
        columns="Scenario",
        values="Impact value"
    ).reset_index()
    pivot_df.columns.name = None
    scenario_1, scenario_2 = pivot_df.columns[3:]

    scenario_map = {
        "Net Zero Emissions by 2050 Scenario": "NZE",
        "Stated Policies Scenario": "STEPS"
    }

    impact_categories = ["Human Health damage", "Ecosystem Quality damage"]
    ylabels = {"Human Health damage": "DALY", "Ecosystem Quality damage": "PDF·m²·yr"}
    fill_colors = {
        "Total energy system": "#99d8c9",
        "Energy transition": "#ffadad"
    }
    custom_labels = {
        "Total energy system": "Cumulative avoided impact",
        "Energy transition": "Cumulative additional impact"
    }

    sns.set_style("white")
    fig, axes = plt.subplots(1, 2, figsize=(12, 5), sharex=True)
    fig.subplots_adjust(hspace=0.3, wspace=0.25)

    for idx, impact_category in enumerate(impact_categories):
        ax = axes[idx]
        sub_df = pivot_df[pivot_df["Impact category"] == impact_category]

        for sector_idx, (sector, linestyle, linewidth, alpha) in enumerate(
            zip(["Total energy system", "Energy transition"], ["-", "--"], [2, 1.5], [1, 0.8])
        ):
            sub = sub_df[sub_df["Sector"] == sector].dropna(subset=[scenario_1, scenario_2]).sort_values("Year")
            years = sub["Year"].values
            val_1 = sub[scenario_1].values
            val_2 = sub[scenario_2].values

            ax.plot(years, val_1, marker='o', markersize=4, linestyle=linestyle, linewidth=linewidth,
                    alpha=alpha, color="#adc698", label=f"{scenario_map[scenario_1]} - {sector}")
            ax.plot(years, val_2, marker='s', markersize=4, linestyle=linestyle, linewidth=linewidth,
                    alpha=alpha, color="#c05746", label=f"{scenario_map[scenario_2]} - {sector}")

            # Fill area (not added to legend)
            ax.fill_between(
                years, val_1, val_2,
                interpolate=True,
                color=fill_colors[sector],
                alpha=0.3
            )

            # Δ annotation in matching color
            diff_area = np.trapz(val_1 - val_2, x=years)
            x_center = 0.50
            y_offset = 0.5 if sector == "Total energy system" else 0.3
            unit = ylabels[impact_category]
            ax.annotate(
                f"{custom_labels[sector]}\nΔ = {diff_area:.1e} {unit}",
                xy=(x_center, y_offset),
                xycoords='axes fraction',
                fontsize=10,
                fontweight='bold',
                ha='right',
                va='center',
                color=fill_colors[sector],
                bbox=dict(facecolor="white", edgecolor="none", boxstyle="round,pad=0.2", alpha=0.7)
            )

        ax.set_yscale('log')
        ax.set_title(impact_category)
        ax.set_ylabel(ylabels[impact_category])
        ax.set_xlabel("")
        ax.set_xticks(years)
        ax.set_xticklabels([int(y) for y in years])
        ax.spines[['top', 'right']].set_visible(False)
        ax.grid(axis='y', linestyle="--", linewidth=0.5, alpha=0.4)

    # Remove "Gap:" lines from legend
    handles, labels = axes[0].get_legend_handles_labels()
    clean_handles_labels = [(h, l) for h, l in zip(handles, labels) if not l.startswith("Gap:")]
    clean_handles, clean_labels = zip(*clean_handles_labels)
    fig.legend(clean_handles, clean_labels, loc='lower center', bbox_to_anchor=(0.5, -0.08), ncol=2, fontsize=10)

    plt.tight_layout(rect=[0, 0.05, 1, 1])

    if save_path:
        import os
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        plt.savefig(f"{save_path}.pdf", format="pdf", dpi=600, transparent=True, bbox_inches='tight')
        plt.savefig(f"{save_path}.png", format="png", dpi=600, bbox_inches='tight')

    if show:
        plt.show()
    else:
        plt.close()


def plot_all_metals_subplots(
        df,
        ncols=4,
        energy_color='#31a354',
        rest_color='#de2d26',
        save_path=None,
        show=False
):
    """
    Multi-panel line plot with shared legend placed in the empty bottom-right subplot.
    """

    rcParams['pdf.fonttype'] = 42
    rcParams['ps.fonttype'] = 42
    rcParams['font.family'] = 'arial'
    rcParams['font.size'] = 10
    rcParams['axes.labelsize'] = 10
    rcParams['legend.fontsize'] = 9
    rcParams['xtick.labelsize'] = 9
    rcParams['ytick.labelsize'] = 9
    rcParams['axes.titlesize'] = 12
    rcParams['text.usetex'] = False

    metals = df['Metal'].unique()
    n = len(metals)
    nrows = math.ceil(n / ncols)
    fig, axes = plt.subplots(nrows, ncols, figsize=(ncols * 4, nrows * 3), squeeze=False)

    # Plot each metal
    for idx, metal in enumerate(metals):
        r, c = divmod(idx, ncols)
        ax = axes[r][c]
        sub = df[df['Metal'] == metal]
        ax.plot(sub['Year'], sub['Energy transition (kt)'], marker='o',
                color=energy_color)
        ax.plot(sub['Year'], sub['Rest of the economy (kt)'], marker='s',
                color=rest_color)
        ax.set_title(metal)
        ax.set_xlabel('Year')
        ax.set_ylabel('Demand (kt)')

    # Prepare legend handles
    handles = [
        Line2D([0], [0], color=energy_color, marker='o', label='Energy transition'),
        Line2D([0], [0], color=rest_color, marker='s', label='Rest of economy')
    ]

    # Hide unused subplots and place legend in the first empty spot
    for idx in range(n, nrows * ncols):
        r, c = divmod(idx, ncols)
        axes[r][c].axis('off')
        # place legend in that first empty subplot
        # axes[r][c].legend(handles=handles, loc='lower right', frameon=False)

        # after — framed and larger
        legend = axes[r][c].legend(
            handles=handles,
            loc='lower right',
            frameon=True,  # turn the box on
            edgecolor='black',  # box border color
            facecolor='white',  # box fill
            fontsize=12,  # larger text
            markerscale=1.5,  # bigger markers
            handlelength=2.0,  # longer line samples
            borderpad=1.0  # space between box and content
        )
        legend.get_frame().set_linewidth(1.0)  # thicker frame line
        break  # only use the first empty spot

    plt.tight_layout()

    # Save both PDF and PNG at high resolution
    if save_path:
        fig.savefig(f"{save_path}.pdf", format='pdf', dpi=600)
        fig.savefig(f"{save_path}.png", format='png', dpi=600)

    if show:
        plt.show()

    plt.close()


def plot_all_metals_subplots_damage(df_nze, df_ssp2, impact_type, save_path=None, ncols=4):
    """
    Multi-panel plot comparing NZE vs SSP2 for each metal, with NZE aggregated over all technologies.
    Fixes: enlarged legend and avoids drawing an empty grid cell.
    """
    # Aggregate NZE over all technologies

    rcParams['pdf.fonttype'] = 42
    rcParams['ps.fonttype'] = 42
    rcParams['font.family'] = 'arial'
    rcParams['font.size'] = 10
    rcParams['axes.labelsize'] = 10
    rcParams['legend.fontsize'] = 9
    rcParams['xtick.labelsize'] = 9
    rcParams['ytick.labelsize'] = 9
    rcParams['axes.titlesize'] = 12
    rcParams['text.usetex'] = False

    df_nze_agg = df_nze.groupby(["Year", "Metal"])[impact_type].sum().reset_index()
    df_ssp2_agg = df_ssp2.groupby(["Year", "Metal"])[impact_type].sum().reset_index()

    df_nze_agg["Scenario"] = "Energy transition"
    df_ssp2_agg["Scenario"] = "Rest of economy"

    df_all = pd.concat([df_nze_agg, df_ssp2_agg], ignore_index=True)

    # Only keep metals present in both scenarios
    metal_counts = df_all.groupby(["Metal", "Scenario"]).size().unstack().dropna()
    common_metals = metal_counts.index.tolist()
    df_all = df_all[df_all["Metal"].isin(common_metals)]

    # Global figure setup
    metals = sorted(df_all["Metal"].unique())
    n = len(metals)
    nrows = math.ceil(n / ncols)
    fig, axes = plt.subplots(nrows, ncols, figsize=(ncols * 4, nrows * 2.8), squeeze=False)

    # Plot per metal
    for idx, metal in enumerate(metals):
        r, c = divmod(idx, ncols)
        ax = axes[r][c]
        sub = df_all[df_all["Metal"] == metal]
        for scenario, marker, color in zip(["Energy transition", "Rest of economy"],
                                           ['o', 's'],
                                           ['#31a354', '#de2d26']):
            scenario_data = sub[sub["Scenario"] == scenario]
            ax.plot(scenario_data["Year"], scenario_data[impact_type],
                    label=scenario, marker=marker, color=color, linewidth=1.5)
        ax.set_title(metal)
        ax.set_xlabel('')
        ax.set_ylabel(impact_type if idx % ncols == 0 else "")

    # Remove all unused subplots
    for idx in range(n, nrows * ncols):
        r, c = divmod(idx, ncols)
        fig.delaxes(axes[r][c])

    # Create big legend outside the grid
    fig.legend(
        handles=[
            Line2D([0], [0], color='#31a354', marker='o', label='Energy transition'),
            Line2D([0], [0], color='#de2d26', marker='s', label='Rest of the economy')
        ],
        loc="lower center", ncol=2, frameon=True, edgecolor='black',
        facecolor='white', fontsize=12, markerscale=1.8,
        handlelength=2.5, borderpad=1.2
    )

    plt.tight_layout(rect=[0, 0.05, 1, 1])  # leave space at bottom for legend

    # Save
    if save_path:
        fig.savefig(f"{save_path}.pdf", format='pdf', dpi=600)
        fig.savefig(f"{save_path}.png", format='png', dpi=600)

    plt.show()


def plot_stacked_overlay_subplot(df_nze, df_ssp2,
                              group_by="Metal",
                              value_cols=["Total ecosystem quality", "Total human health"],
                              titles=["EQ damage by metal", "HH damage by metal"],
                              y_labels=["PDF·m²·yr", "DALY"],
                              color_palette="tab20",
                              custom_colors=None,
                              nze_color="#000000",
                              threshold=0.01,
                              save_path=None):

    rcParams['pdf.fonttype'] = 42
    rcParams['ps.fonttype'] = 42
    rcParams['font.family'] = 'arial'
    rcParams['font.size'] = 10
    rcParams['axes.labelsize'] = 10
    rcParams['legend.fontsize'] = 9
    rcParams['xtick.labelsize'] = 9
    rcParams['ytick.labelsize'] = 9
    rcParams['axes.titlesize'] = 12
    rcParams['text.usetex'] = False

    fig, axes = plt.subplots(2, 1, figsize=(8, 7), sharex=True)
    plt.subplots_adjust(hspace=0.3)

    all_handles = []
    all_labels = []

    for idx, (value_col, title, y_label) in enumerate(zip(value_cols, titles, y_labels)):
        ax = axes[idx]

        df_nze_ = df_nze.copy()
        df_ssp2_ = df_ssp2.copy()
        df_nze_["Scenario"] = "Energy transition"
        df_ssp2_["Scenario"] = "Rest of economy"
        df_all = pd.concat([df_nze_, df_ssp2_])

        total_contributions = df_all.groupby(group_by)[value_col].sum()
        significant = total_contributions[total_contributions / total_contributions.sum() >= threshold].index
        df_all[group_by] = df_all[group_by].apply(lambda x: x if x in significant else "Others")

        df_nze_ = df_all[df_all["Scenario"] == "Energy transition"]
        df_ssp2_ = df_all[df_all["Scenario"] == "Rest of economy"]

        df_ssp2_pivot = df_ssp2_.groupby(["Year", group_by])[value_col].sum().reset_index() \
            .pivot(index="Year", columns=group_by, values=value_col).fillna(0)
        ssp2_sorted_cols = df_ssp2_pivot.sum().sort_values(ascending=False).index
        df_ssp2_pivot = df_ssp2_pivot[ssp2_sorted_cols]

        df_nze_total = df_nze_.groupby("Year")[value_col].sum().reset_index()

        metals = df_ssp2_pivot.columns
        if custom_colors:
            color_dict = {m: custom_colors.get(m, "gray") for m in metals}
        else:
            cmap = cm.get_cmap(color_palette, len(metals))
            color_dict = {m: cmap(i) for i, m in enumerate(metals)}

        x_years = df_nze_total["Year"].to_numpy(dtype=np.float64)
        ssp2_bottom = np.zeros(len(df_ssp2_pivot))

        for metal in ssp2_sorted_cols:
            y = df_ssp2_pivot[metal].to_numpy(dtype=np.float64)
            patch = ax.fill_between(df_ssp2_pivot.index, ssp2_bottom, ssp2_bottom + y,
                                    color=color_dict[metal], alpha=0.8, label=metal)
            ssp2_bottom += y

        y1_bottom = ssp2_bottom
        y2_top = y1_bottom + df_nze_total[value_col].to_numpy(dtype=np.float64)
        ax.fill_between(x_years, y1_bottom, y2_top, color=nze_color, alpha=0.8, label="Energy transition")
        ax.plot(x_years, y1_bottom, color='black', linewidth=1.0)

        ax.set_title(title, fontsize=11)
        ax.set_ylabel(y_label)
        ax.tick_params(labelsize=8)
        ax.tick_params(labelbottom=True)
        ax.spines[['top', 'right']].set_visible(False)
        #ax.grid(axis='y', linestyle='--', linewidth=0.5, alpha=0.3)

        # Collect legend entries once
        handles, labels = ax.get_legend_handles_labels()
        all_handles.extend(handles)
        all_labels.extend(labels)

    # Deduplicate legend items
    unique_labels = dict(zip(all_labels, all_handles))  # Keeps last occurrence
    fig.legend(unique_labels.values(), unique_labels.keys(),
               loc='lower center', bbox_to_anchor=(0.5, -0.08),
               ncol=3, fontsize=10)

    axes[-1].set_xlabel("")

    if save_path:
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        fig.savefig(f"{save_path}.pdf", format="pdf", dpi=600, bbox_inches='tight')
        fig.savefig(f"{save_path}.png", format="png", dpi=600, bbox_inches='tight')

    plt.tight_layout(rect=[0, 0.05, 1, 1])
    plt.show()