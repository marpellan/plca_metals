import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt
import matplotlib.cm as cm
from matplotlib import rcParams
import plotly.graph_objects as go

### SET GLOBAL MATPLOTLIB PARAMS
rcParams['pdf.fonttype'] = 42  # to snsure TrueType fonts are embedded
rcParams['ps.fonttype'] = 42
rcParams['font.family'] = 'arial'
rcParams['font.size'] = 10
rcParams['axes.labelsize'] = 10
rcParams['legend.fontsize'] = 9
rcParams['xtick.labelsize'] = 9
rcParams['ytick.labelsize'] = 9
rcParams['axes.titlesize'] = 12


### FUNCTIONS
def plot_stacked_area(df, group_by, value_col, title, y_label, color_palette="tab20", custom_colors=None,
                      threshold=0.01, save_path="plots/stacked_area"):
    """
    Generate a stacked area plot with optional custom colors and conditional aggregation.

    Parameters:
    - df: DataFrame with data
    - group_by: Column to group by ('Metal' or 'Technology')
    - value_col: Column containing impact values
    - title: Plot title
    - y_label: Label for Y-axis (e.g., "Impact (unit)")
    - color_palette: Colormap name for automatic coloring (default: "tab20")
    - custom_colors: Dict with manual colors (e.g., {"Solar PV": "#1f77b4"})
    - threshold: Threshold for grouping small categories into "Other" (applies only to Metals, not Technologies)
    - save_path: Base filename for saving plots (without extension)

    Outputs:
    - Saves PDF and PNG versions of the figure
    """

    # Ensure directory exists
    os.makedirs(os.path.dirname(save_path), exist_ok=True)

    # Aggregate data
    df_grouped = df.groupby(["Year", group_by])[value_col].sum().reset_index()

    # Apply threshold only for Metals, keep all Technologies
    if group_by == "Metal":
        total_contributions = df_grouped.groupby(group_by)[value_col].sum()
        significant_categories = total_contributions[total_contributions / total_contributions.sum() >= threshold].index
        df_grouped[group_by] = df_grouped[group_by].apply(lambda x: x if x in significant_categories else "Other")

    # Pivot for stacked area plot
    df_pivot = df_grouped.pivot_table(index="Year", columns=group_by, values=value_col, aggfunc="sum")

    # Sort categories based on first year's contribution (largest to smallest)
    first_year = df_pivot.index.min()
    sorted_categories = df_pivot.loc[first_year].sort_values(ascending=False).index
    df_pivot = df_pivot[sorted_categories]

    # Assign colors (Fix: Apply to both Metals & Technologies)
    unique_categories = df_pivot.columns
    if custom_colors:
        # Apply user-defined colors for both Metals & Technologies
        color_dict = {cat: custom_colors.get(cat, "gray") for cat in unique_categories}
    else:
        # Otherwise, use colormap
        cmap = cm.get_cmap(color_palette, len(unique_categories))
        color_dict = {cat: cmap(i) for i, cat in enumerate(unique_categories)}

    # Generate plot
    fig, ax = plt.subplots(figsize=(7.2, 4.5))
    colors = [color_dict.get(col, "gray") for col in df_pivot.columns]
    ax.stackplot(df_pivot.index, df_pivot.T, labels=df_pivot.columns, colors=colors, alpha=0.8)

    # Formatting
    ax.set_title(title)
    ax.set_ylabel(y_label)

    # Sort legend in the same order as the stacked areas
    handles, labels = ax.get_legend_handles_labels()
    legend_order = [labels.index(cat) for cat in sorted_categories if cat in labels]
    sorted_handles = [handles[i] for i in legend_order]
    sorted_labels = [labels[i] for i in legend_order]

    ax.legend(sorted_handles, sorted_labels, loc="upper left", bbox_to_anchor=(1, 1))
    plt.tight_layout()

    # Save figures
    plt.savefig(f"{save_path}.pdf", format="pdf", dpi=600)
    plt.savefig(f"{save_path}.png", format="png", dpi=600)
    plt.show()


def generate_full_color_dict(impact_categories, custom_colors, colormap="tab20"):
    """
    Ensures all impact categories receive a distinct color.

    - Uses predefined colors for important categories.
    - Assigns unique colors to remaining categories from a colormap.

    Parameters:
    - impact_categories: List of all impact categories
    - custom_colors: Dictionary of manually defined colors for key categories
    - colormap: Matplotlib colormap to use for additional categories

    Returns:
    - A complete color dictionary for all impact categories
    """

    # Get a colormap with enough distinct colors
    cmap = cm.get_cmap(colormap, len(impact_categories))

    # Start with predefined colors
    full_color_dict = custom_colors.copy()

    # Assign unique colors to missing categories
    for i, cat in enumerate(impact_categories):
        if cat not in full_color_dict:
            full_color_dict[cat] = cmap(i)  # Assign a unique color

    return full_color_dict


def plot_stacked_bar(df, impact_columns, total_col, title, y_label="Percentage contribution (%)",
                     color_palette="tab20", custom_colors=None, threshold=0.03, save_path="plots/stacked_bar"):
    """
    Generate a stacked bar plot showing the contribution of different midpoint indicators to the total impact.
    Contributors below a threshold (default: 5%) are grouped into "Other".

    Parameters:
    - df: DataFrame with data
    - impact_columns: List of midpoint impact indicators (e.g., EQ or HH categories)
    - total_col: Column containing the total impact for normalization (e.g., 'Total ecosystem quality' or 'Total human health')
    - title: Plot title
    - y_label: Label for Y-axis (default: "Percentage contribution (%)")
    - color_palette: Colormap name for automatic coloring (default: "tab20") if no custom colors are provided
    - custom_colors: Dictionary with predefined colors for certain categories
    - threshold: Minimum percentage contribution to remain separate; others are grouped into "Other"
    - save_path: Base filename for saving plots (without extension)

    Outputs:
    - Saves PDF and PNG versions of the figure
    """

    # Ensure directory exists
    os.makedirs(os.path.dirname(save_path), exist_ok=True)

    # Aggregate data by year
    df_grouped = df.groupby("Year")[impact_columns + [total_col]].sum()

    # Convert to percentage of total impact
    df_percent = df_grouped[impact_columns].div(df_grouped[total_col], axis=0) * 100

    # Identify small contributors to group into "Other"
    total_contributions = df_percent.mean()  # Average over time for consistency
    significant_categories = total_contributions[total_contributions >= (threshold * 100)].index.tolist()

    # Group small contributors into "Other"
    df_percent["Other"] = df_percent.drop(columns=significant_categories).sum(axis=1)
    df_percent = df_percent[significant_categories + ["Other"]]

    # Sort categories based on first year's contribution (largest to smallest)
    first_year = df_percent.index.min()
    sorted_categories = df_percent.loc[first_year].sort_values(ascending=False).index
    df_percent = df_percent[sorted_categories]

    # Assign colors: use custom colors if provided, else use a colormap
    if custom_colors:
        color_dict = {cat: custom_colors.get(cat, "gray") for cat in sorted_categories}
    else:
        color_dict = generate_full_color_dict(sorted_categories, {}, color_palette)

    # Ensure "Other" has a distinct neutral color
    color_dict["Other"] = "#2b2d42"  # Dark Gray for clarity

    # Generate plot
    fig, ax = plt.subplots(figsize=(7.2, 5))
    colors = [color_dict[col] for col in df_percent.columns]
    df_percent.plot(kind="bar", stacked=True, color=colors, ax=ax, width=0.8)

    # Formatting
    ax.set_title(title, fontsize=12)
    ax.set_ylabel(y_label, fontsize=10)
    ax.set_xlabel("")
    ax.set_xticklabels(df_percent.index, rotation=360)

    # Legend formatting: Reduce size, place below if necessary
    # ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.1), ncol=3, fontsize=6, frameon=False)
    ax.legend(loc="center left", bbox_to_anchor=(1, 0.5), fontsize=8, frameon=False)

    plt.tight_layout()

    # Save figures
    plt.savefig(f"{save_path}.pdf", format="pdf", dpi=600)
    plt.savefig(f"{save_path}.png", format="png", dpi=600)
    plt.show()


def plot_cumulative_midpoint_contribution(df, impact_columns, total_col, title, y_label="Percentage contribution (%)",
                                          color_palette="tab20", custom_colors=None, threshold=0.03,
                                          save_path="plots/cumulative_midpoint"):
    """
    Generate a bar plot showing the cumulative contribution of different midpoint indicators to the total impact from 2022-2050.
    Bars represent the mean contribution, with a line showing min-max variation. Contributors below a threshold (default: 5%)
    are grouped into "Other".

    Parameters:
    - df: DataFrame with data
    - impact_columns: List of midpoint impact indicators (e.g., EQ or HH categories)
    - total_col: Column containing the total impact for normalization (e.g., 'Total ecosystem quality' or 'Total human health')
    - title: Plot title
    - y_label: Label for Y-axis (default: "Percentage contribution (%)")
    - color_palette: Colormap name for automatic coloring (default: "tab20") if no custom colors are provided
    - custom_colors: Dictionary with predefined colors for certain categories
    - threshold: Minimum percentage contribution to remain separate; others are grouped into "Other"
    - save_path: Base filename for saving plots (without extension)

    Outputs:
    - Saves PDF and PNG versions of the figure
    """

    # Ensure directory exists
    os.makedirs(os.path.dirname(save_path), exist_ok=True)

    # Aggregate data over all years (2022-2050)
    df_grouped = df.groupby("Year")[impact_columns + [total_col]].sum()

    # Convert to percentage of total impact
    df_percent = df_grouped[impact_columns].div(df_grouped[total_col], axis=0) * 100

    # Compute mean, min, and max contributions over time
    mean_contributions = df_percent.mean()
    min_contributions = df_percent.min()
    max_contributions = df_percent.max()

    # Identify small contributors to group into "Other"
    significant_categories = mean_contributions[mean_contributions >= (threshold * 100)].index.tolist()

    # Group small contributors into "Other"
    df_percent["Other"] = df_percent.drop(columns=significant_categories).sum(axis=1)
    mean_contributions["Other"] = df_percent["Other"].mean()
    min_contributions["Other"] = df_percent["Other"].min()
    max_contributions["Other"] = df_percent["Other"].max()

    # Keep only significant contributors + "Other"
    mean_contributions = mean_contributions[significant_categories + ["Other"]]
    min_contributions = min_contributions[significant_categories + ["Other"]]
    max_contributions = max_contributions[significant_categories + ["Other"]]

    # Sort categories by mean contribution
    sorted_categories = mean_contributions.sort_values(ascending=False).index
    mean_contributions = mean_contributions[sorted_categories]
    min_contributions = min_contributions[sorted_categories]
    max_contributions = max_contributions[sorted_categories]

    # Assign colors: use custom colors if provided, else use a colormap
    if custom_colors:
        color_dict = {cat: custom_colors.get(cat, "gray") for cat in sorted_categories}
    else:
        cmap = cm.get_cmap(color_palette, len(sorted_categories))
        color_dict = {cat: cmap(i) for i, cat in enumerate(sorted_categories)}

    # Ensure "Other" has a distinct neutral color
    color_dict["Other"] = "#A9A9A9"  # Dark Gray for clarity

    # Generate plot
    fig, ax = plt.subplots(figsize=(9, 5))
    x_positions = np.arange(len(sorted_categories))
    colors = [color_dict[col] for col in sorted_categories]

    # Plot bars (mean values)
    bars = ax.bar(x_positions, mean_contributions, color=colors, alpha=0.8)

    # Add min-max variation as a line
    ax.errorbar(x_positions, mean_contributions,
                yerr=[mean_contributions - min_contributions, max_contributions - mean_contributions],
                fmt='none', ecolor='black', capsize=4, elinewidth=1)

    # Formatting
    ax.set_title(title, fontsize=12)
    ax.set_ylabel(y_label, fontsize=10)
    ax.set_xticks(x_positions)
    ax.set_xticklabels(sorted_categories, rotation=90, ha="right", fontsize=8)

    # Save figures
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
            label=node_labels, color=node_colors, x=x_pos
        ),
        link=dict(source=sources, target=targets, value=values)
    ))
    fig.update_layout(
        #title_text=title,
        font_family="Arial", font_size=12,
        width=1200, height=700,
        paper_bgcolor="white", plot_bgcolor="white"
    )

    # 9) save outputs
    fig.write_html(f"{save_path}.html")
    # fig.write_image(f"{save_path}.png", scale=2)

    return fig


def plot_lineplot_burden_comparison(df, save_path=None, show=True):
    import matplotlib.pyplot as plt
    import seaborn as sns
    import pandas as pd
    import os

    # Matplotlib formatting for Joule-quality figures
    from matplotlib import rcParams
    rcParams['pdf.fonttype'] = 42
    rcParams['ps.fonttype'] = 42
    rcParams['font.family'] = 'Arial'
    rcParams['font.size'] = 10
    rcParams['axes.labelsize'] = 10
    rcParams['legend.fontsize'] = 9
    rcParams['xtick.labelsize'] = 9
    rcParams['ytick.labelsize'] = 9
    rcParams['axes.titlesize'] = 12

    # Pivot and clean
    df["Year"] = pd.to_numeric(df["Year"], errors="coerce")
    pivot_df = df.pivot_table(
        index=["Year", "Sector", "Impact category"],
        columns="Scenario",
        values="Impact value"
    ).reset_index()
    pivot_df.columns.name = None
    scenario_1, scenario_2 = pivot_df.columns[3:]

    scenario_map = {
        "Net Zero Emissions by 2050 Scenario": "NZS",
        "Stated Policies Scenario": "STEPS"
    }

    pivot_df[scenario_1] = pd.to_numeric(pivot_df[scenario_1], errors="coerce")
    pivot_df[scenario_2] = pd.to_numeric(pivot_df[scenario_2], errors="coerce")

    hh_df = pivot_df[pivot_df["Impact category"] == "Climate change (HH)"]
    eq_df = pivot_df[pivot_df["Impact category"] == "Climate change (EQ)"]

    sns.set_style("white")
    fig, axes = plt.subplots(2, 2, figsize=(10, 6), sharex=True)
    fig.subplots_adjust(hspace=0.35, wspace=0.25)

    panels = [
        (hh_df, "Energy transition", axes[0, 0], "Human Health (HH)", "DALY"),
        (hh_df, "Total energy system", axes[0, 1], "Human Health (HH)", ""),
        (eq_df, "Energy transition", axes[1, 0], "Ecosystem Quality (EQ)", "PDF·m²·yr"),
        (eq_df, "Total energy system", axes[1, 1], "Ecosystem Quality (EQ)", "")
    ]

    handles_created = False
    all_handles, all_labels = [], []

    for df_part, sector, ax, title, ylabel in panels:
        sub = df_part[df_part["Sector"] == sector].dropna(subset=[scenario_1, scenario_2]).sort_values("Year")
        years = sub["Year"].values
        val_1 = sub[scenario_1].values
        val_2 = sub[scenario_2].values

        line1, = ax.plot(years, val_1, marker='o', color="#1f77b4", label=scenario_map.get(scenario_1, scenario_1))
        line2, = ax.plot(years, val_2, marker='s', color="#2ca02c", label=scenario_map.get(scenario_2, scenario_2))
        ax.fill_between(years, val_1, val_2, color="#b2df8a", alpha=0.5)

        ax.set_title(f"{title} – {sector}")
        ax.set_ylabel(ylabel)
        ax.set_xlabel("")
        ax.set_xticks(years)
        ax.set_xticklabels([int(y) for y in years])
        ax.ticklabel_format(axis="y", style="sci", scilimits=(0, 0))
        ax.spines[['top', 'right']].set_visible(False)

        # Only collect legend handles once
        if not handles_created:
            all_handles.extend([line1, line2])
            all_labels.extend([scenario_map.get(scenario_1), scenario_map.get(scenario_2)])
            patch = plt.Line2D([0], [0], color="#b2df8a", lw=6, alpha=0.5)
            all_handles.append(patch)
            all_labels.append("Difference")
            handles_created = True

    plt.tight_layout(rect=[0, 0.05, 1, 1])  # Room for legend

    # One shared legend below
    fig.legend(all_handles, all_labels,
               loc='lower center',
               bbox_to_anchor=(0.5, -0.01),
               ncol=3,
               frameon=False)

    if save_path:
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        plt.savefig(f"{save_path}.pdf", format="pdf", dpi=600, transparent=True)
        plt.savefig(f"{save_path}.png", format="png", dpi=600)

    if show:
        plt.show()
    else:
        plt.close()


def plot_lineplot_burden_comparison_combined(df, save_path=None, show=True):
    import matplotlib.pyplot as plt
    import seaborn as sns
    import pandas as pd
    import os

    from matplotlib import rcParams
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
        "Net Zero Emissions by 2050 Scenario": "NZS",
        "Stated Policies Scenario": "STEPS"
    }

    pivot_df[scenario_1] = pd.to_numeric(pivot_df[scenario_1], errors="coerce")
    pivot_df[scenario_2] = pd.to_numeric(pivot_df[scenario_2], errors="coerce")

    impact_categories = ["Climate change (HH)", "Climate change (EQ)"]
    ylabels = {"Climate change (HH)": "DALY", "Climate change (EQ)": "PDF·m²·yr"}

    sns.set_style("white")
    fig, axes = plt.subplots(1, 2, figsize=(12, 5), sharex=True)
    fig.subplots_adjust(hspace=0.35, wspace=0.25)

    for idx, impact_category in enumerate(impact_categories):
        ax = axes[idx]
        sub_df = pivot_df[pivot_df["Impact category"] == impact_category]

        for sector, linestyle, marker in zip(["Total energy system", "Energy transition"], ["-", "--"], ['o', None]):
            sub = sub_df[sub_df["Sector"] == sector].dropna(subset=[scenario_1, scenario_2]).sort_values("Year")
            years = sub["Year"].values
            val_1 = sub[scenario_1].values
            val_2 = sub[scenario_2].values

            ax.plot(years, val_1, marker=marker, linestyle=linestyle, color="#1f77b4",
                    label=f"{scenario_map[scenario_1]} - {sector}")
            ax.plot(years, val_2, marker=marker, linestyle=linestyle, color="#2ca02c",
                    label=f"{scenario_map[scenario_2]} - {sector}")
            ax.fill_between(years, val_1, val_2, color="#b2df8a", alpha=0.3)

        ax.set_title(impact_category)
        ax.set_ylabel(ylabels[impact_category])
        ax.set_xlabel("Year")
        ax.set_xticks(years)
        ax.set_xticklabels([int(y) for y in years])
        ax.ticklabel_format(axis="y", style="sci", scilimits=(0, 0))
        ax.spines[['top', 'right']].set_visible(False)

    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(handles, labels, loc='lower center', bbox_to_anchor=(0.5, -0.02), ncol=2, frameon=False)

    plt.tight_layout(rect=[0, 0.05, 1, 1])

    if save_path:
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        plt.savefig(f"{save_path}.pdf", format="pdf", dpi=600, transparent=True)
        plt.savefig(f"{save_path}.png", format="png", dpi=600)

    if show:
        plt.show()
    else:
        plt.close()


def plot_lineplot_logscale(df, save_path=None, show=True):
    import matplotlib.pyplot as plt
    import seaborn as sns
    import pandas as pd
    import os

    from matplotlib import rcParams
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
        "Net Zero Emissions by 2050 Scenario": "NZS",
        "Stated Policies Scenario": "STEPS"
    }

    pivot_df[scenario_1] = pd.to_numeric(pivot_df[scenario_1], errors="coerce")
    pivot_df[scenario_2] = pd.to_numeric(pivot_df[scenario_2], errors="coerce")

    impact_categories = ["Climate change (HH)", "Climate change (EQ)"]
    ylabels = {"Climate change (HH)": "DALY", "Climate change (EQ)": "PDF·m²·yr"}

    sns.set_style("white")
    fig, axes = plt.subplots(1, 2, figsize=(12, 5), sharex=True)
    fig.subplots_adjust(hspace=0.3, wspace=0.25)

    for idx, impact_category in enumerate(impact_categories):
        ax = axes[idx]
        sub_df = pivot_df[pivot_df["Impact category"] == impact_category]

        for sector, linestyle, linewidth, alpha in zip(["Total energy system", "Energy transition"], ["-", "--"], [2, 1.5], [1, 0.8]):
            sub = sub_df[sub_df["Sector"] == sector].dropna(subset=[scenario_1, scenario_2]).sort_values("Year")
            years = sub["Year"].values
            val_1 = sub[scenario_1].values
            val_2 = sub[scenario_2].values

            ax.plot(years, val_1, marker='o', markersize=4, linestyle=linestyle, linewidth=linewidth, alpha=alpha,
                    color="#1f77b4", label=f"{scenario_map[scenario_1]} - {sector}")
            ax.plot(years, val_2, marker='s', markersize=4, linestyle=linestyle, linewidth=linewidth, alpha=alpha,
                    color="#2ca02c", label=f"{scenario_map[scenario_2]} - {sector}")

        ax.set_yscale('log')
        ax.set_title(impact_category)
        ax.set_ylabel(ylabels[impact_category])
        ax.set_xlabel("")
        ax.set_xticks(years)
        ax.set_xticklabels([int(y) for y in years])
        ax.spines[['top', 'right']].set_visible(False)
        ax.grid(axis='y', linestyle="--", linewidth=0.5, alpha=0.4)  # Only y-grid

    # Fix legend positioning for export
    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(handles, labels,
           loc='center left',
           bbox_to_anchor=(0.85, 0.5),
           frameon=False)


    # Make sure there is enough room at bottom
    plt.tight_layout(rect=[0, 0, 0.85, 1])

    if save_path:
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        plt.savefig(f"{save_path}.pdf", format="pdf", dpi=600, transparent=True, bbox_inches='tight')
        plt.savefig(f"{save_path}.png", format="png", dpi=600, bbox_inches='tight')

    if show:
        plt.show()
    else:
        plt.close()


def plot_percentage_transition(df, save_path=None, show=True):
    import matplotlib.pyplot as plt
    import seaborn as sns
    import pandas as pd
    import numpy as np
    import os
    from scipy.interpolate import make_interp_spline

    from matplotlib import rcParams
    rcParams['pdf.fonttype'] = 42
    rcParams['ps.fonttype'] = 42
    rcParams['font.family'] = 'Arial'
    rcParams['font.size'] = 10

    df["Year"] = pd.to_numeric(df["Year"], errors="coerce")
    pivot_df = df.pivot(index=["Year", "Impact category", "Scenario"], columns="Sector", values="Impact value").reset_index()
    pivot_df['Percentage'] = 100 * pivot_df['Energy transition'] / pivot_df['Total energy system']

    impact_categories = pivot_df["Impact category"].unique()
    scenarios = pivot_df["Scenario"].unique()

    sns.set_style("white")
    fig, axes = plt.subplots(1, len(impact_categories), figsize=(12, 5))

    for idx, impact_category in enumerate(impact_categories):
        ax = axes[idx]
        for scenario, color in zip(scenarios, ["#1f77b4", "#2ca02c"]):
            sub = pivot_df[(pivot_df["Impact category"] == impact_category) & (pivot_df["Scenario"] == scenario)]
            sub = sub[np.isfinite(sub["Percentage"])]
            years = sub["Year"].values
            percentages = sub["Percentage"].values

            if len(years) >= 4:
                spline = make_interp_spline(years, percentages, k=3)
                interpolated_years = np.linspace(years.min(), years.max(), 200)
                interpolated_percentages = spline(interpolated_years)
                ax.plot(interpolated_years, interpolated_percentages, color=color, label=scenario)
            else:
                interpolated_years = np.linspace(years.min(), years.max(), 200)
                interpolated_percentages = np.interp(interpolated_years, years, percentages)
                ax.plot(interpolated_years, interpolated_percentages, color=color, label=scenario)

            ax.scatter(years, percentages, color=color, edgecolor='black')

        ax.set_title(f"{impact_category}")
        ax.set_ylabel("Percentage (%)")
        ax.set_xlabel("")
        ax.spines[['top', 'right']].set_visible(False)

    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(handles, labels,
               loc='center left',
               bbox_to_anchor=(0.85, 0.5),
               frameon=False)

    plt.tight_layout(rect=[0, 0, 0.85, 1])

    if save_path:
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        plt.savefig(f"{save_path}.pdf", format="pdf", dpi=600, transparent=True, bbox_inches='tight')
        plt.savefig(f"{save_path}.png", format="png", dpi=600, bbox_inches='tight')

    if show:
        plt.show()
    else:
        plt.close()