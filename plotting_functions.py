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


def create_sankey(df, total_col, impact_columns, title, save_path):
    """
    Create a Sankey diagram showing cumulative effects from metals -> technologies -> midpoint indicators.

    Parameters:
    - df: DataFrame with data
    - total_col: Column containing total impact (e.g., 'Total ecosystem quality' or 'Total human health')
    - impact_columns: List of midpoint impact indicators (e.g., EQ or HH categories)
    - title: Title of the Sankey diagram
    - save_path: Path to save the HTML file of the figure

    Outputs:
    - Saves the Sankey diagram as an interactive HTML file and PNG.
    """

    # Ensure directory exists
    os.makedirs(os.path.dirname(save_path), exist_ok=True)

    # Sum impacts over all years (2022-2050)
    df_cumulative = df.groupby(["Metal", "Technology"])[impact_columns + [total_col]].sum().reset_index()

    # Get unique categories
    all_metals = df_cumulative["Metal"].unique().tolist()
    all_technologies = df_cumulative["Technology"].unique().tolist()
    all_midpoints = impact_columns

    # Define node labels (Metals, Technologies, Midpoints)
    node_labels = all_metals + all_technologies + all_midpoints
    node_colors = (
            ["#d53e4f"] * len(all_metals) +  # Metals (red shades)
            ["#5ab4ac"] * len(all_technologies) +  # Technologies (blue-green shades)
            ["#3288bd"] * len(all_midpoints)  # Midpoint Indicators (blue shades)
    )

    # Create node dictionary for indexing
    node_dict = {name: i for i, name in enumerate(node_labels)}

    # Initialize link sources, targets, and values
    sources, targets, values = [], [], []

    # Metal -> Technology links
    for _, row in df_cumulative.iterrows():
        metal_idx = node_dict[row["Metal"]]
        tech_idx = node_dict[row["Technology"]]
        total_flow = row[total_col]  # Total impact flow from Metal to Technology
        sources.append(metal_idx)
        targets.append(tech_idx)
        values.append(total_flow)

    # Technology -> Midpoint Indicator links
    for tech in all_technologies:
        for midpoint in all_midpoints:
            tech_idx = node_dict[tech]
            midpoint_idx = node_dict[midpoint]
            total_flow = df_cumulative[df_cumulative["Technology"] == tech][midpoint].sum()
            sources.append(tech_idx)
            targets.append(midpoint_idx)
            values.append(total_flow)

    # Define node positions explicitly
    x_positions = (
            [0.1] * len(all_metals) +  # Metals on the left
            [0.5] * len(all_technologies) +  # Technologies in the middle
            [0.9] * len(all_midpoints)  # Midpoint indicators on the far right
    )

    # Create Sankey figure
    fig = go.Figure(go.Sankey(
        node=dict(
            pad=15,
            thickness=20,
            line=dict(color="black", width=1),
            label=node_labels,
            color=node_colors,
            x=x_positions,
        ),
        link=dict(
            source=sources,
            target=targets,
            value=values
        )
    ))

    fig.update_layout(
        title_text=title,
        font=dict(family="Arial", size=12, color="black"),
        font_size=12,
        font_color="black",  # Ensure text remains visible
        width=1200,
        height=700,
        paper_bgcolor="white",  # Set the entire image background to white
        plot_bgcolor="white"  # Set the plot area background to white
    )
    # Save as interactive HTML and PNG
    fig.write_html(f"{save_path}.html")
    # fig.write_image(f"{save_path}.pdf")  # High resolution PNG

    return fig