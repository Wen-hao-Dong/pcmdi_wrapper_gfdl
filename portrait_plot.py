import glob
import os
import numpy as np
import requests
import copy
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import argparse
from pcmdi_metrics.graphics import read_mean_clim_json_files
from pcmdi_metrics.graphics import normalize_by_median
from pcmdi_metrics.graphics import portrait_plot

# Parse input arguments
parser = argparse.ArgumentParser(description="Generate portrait plot")
parser.add_argument('--outdir', type=str, required=True, help='Output directory for results')
parser.add_argument('--pmp_data_root', type=str, required=True, help='Path to PMP data root')
parser.add_argument('--convention', type=str, required=True, help='Convection of model simulation')
args = parser.parse_args()

outdir = args.outdir
pmp_data_root = args.pmp_data_root
convention = args.convention

# CMIP6 `amip` simulations
amip_json_files = glob.glob(
    f"{pmp_data_root}/pcmdi_metrics_results_archive/metrics_results/"
    + "mean_climate/cmip6/amip/v20210830/*.json"
)

# CMIP6 `historical` simulations
historical_json_files = glob.glob(
    f"{pmp_data_root}/pcmdi_metrics_results_archive/metrics_results/"
    + "mean_climate/cmip6/historical/v20210811/*.json"
)


class Metrics:
    """Mean climate metrics object class"""

    def __init__(self, files):
        """Initialize the mean climate metrics class

        This method initializes the mean climate metrics object given a
        single json file, a list of json files, or a directory containing
        a set of json files.

        Parameters
        ----------
        files : str, path-like or list
            Input json file(s) or directory containing json files

        Returns
        -------
        Metrics
            mean climte metrics object class
        """

        # if `files` input is a string, determine if it is a single file
        # or if it is a directory containing json files

        if isinstance(files, str):

            assert os.path.exists(files), "Specified path does not exist."

            if os.path.isfile(files):
                files = [files]
            elif os.path.isdir(files):
                files = glob.glob(f"{files}/*.json")

        else:

            assert isinstance(
                files, list
            ), "Input must either be a single file, directory, or list of files."

        # call `read_mean_clim_json_files` and save the results as
        # object attributes

        (
            self.df_dict,
            self.var_list,
            self.var_unit_list,
            self.regions,
            self.stats,
        ) = read_mean_clim_json_files(files)

    def copy(self):
        """method to deep copy a Metrics instance"""
        return copy.deepcopy(self)

    def merge(self, metrics_obj):
        """Method to merge Metrics instance with another instance

        This method merges an existing metrics instance with another instance
        by finding the superset of stats, seasons, and regions across the
        two instances

        Parameters
        ----------
        metrics_obj : Metrics
            Metrics object to merge with exisiting instance

        Returns
        -------
        Metrics
            merged Metrics instance
        """

        # ensure that second `metrics_obj` is a Metrics object
        assert isinstance(
            metrics_obj, Metrics
        ), "Metrics objects must be merged with other Metrics objects"

        # make a copy of the existing instance as the result
        result = self.copy()

        # loop over superset of `stats`
        stats = set(self.df_dict.keys()).union(metrics_obj.df_dict.keys())
        for stat in sorted(stats):

            # loop over superset of seasons
            seasons = set(self.df_dict[stat].keys()).union(
                metrics_obj.df_dict[stat].keys()
            )
            for season in seasons:

                # loop over superset of regions
                regions = set(self.df_dict[stat][season].keys()).union(
                    metrics_obj.df_dict[stat][season].keys()
                )
                for region in regions:

                    # consider both the current Metrics instance and
                    # candidate `metrics_obj` instance and determine if the
                    # [stat][season][region] nesting contains a pd.DataFrame.
                    # If a KeyError is thrown, it likely does not exist
                    # and initialize an empty pd.DataFrame. If some other
                    # exception occurs, raise it.

                    try:
                        _df1 = self.df_dict[stat][season][region]
                        assert isinstance(
                            _df1, pd.core.frame.DataFrame
                        ), "Unexpected object found"
                    except Exception as exception:
                        if isinstance(exception, KeyError):
                            _df1 = pd.DataFrame()
                        else:
                            raise exception

                    try:
                        _df2 = metrics_obj.df_dict[stat][season][region]
                        assert isinstance(
                            _df2, pd.core.frame.DataFrame
                        ), "Unexpected object found"
                    except Exception as exception:
                        if isinstance(exception, KeyError):
                            _df2 = pd.DataFrame()
                        else:
                            raise exception

                    # concatenate `merge_obj` to the end of the current
                    # instance. Fill `None` types as np.nan to avoid potential
                    # issues with future funcs, such as `normalize_by_median`

                    result.df_dict[stat][season][region] = pd.concat(
                        [_df1, _df2], ignore_index=True
                    ).fillna(value=np.nan)

        # determine the superset of the other attributes

        result.var_list = list(set(self.var_list + metrics_obj.var_list))
        result.var_unit_list = list(set(self.var_unit_list + metrics_obj.var_unit_list))
        result.regions = list(set(self.regions + metrics_obj.regions))
        result.stats = list(set(self.stats + metrics_obj.stats))

        return result

# List of libraries and corresponding tags
#libraries = [(Metrics(historical_json_files), 'HIST'), (Metrics(amip_json_files), 'AMIP')]

# Select library based on the value of convention
if convention == "AMIP":
    library = Metrics(amip_json_files)
elif convention == "HIST":
    library = Metrics(historical_json_files)
else:
    raise ValueError("The convention variable is not set correctly. It must be either 'AMIP' or 'HIST'.")

new_json_result_files = glob.glob(f"{outdir}results/*.json")
new_experiment = Metrics(new_json_result_files)

merged_results = library.merge(new_experiment)

df_dict = merged_results.df_dict
var_list = merged_results.var_list
var_unit_list = merged_results.var_unit_list
regions = merged_results.regions
stats = merged_results.stats

var_list.sort()

model_names = df_dict['rms_xyt']['ann']['global']['model'].tolist()
xaxis_labels = var_list
yaxis_labels = model_names

# Define seasons
djf, mam, jja, son = 'djf', 'mam', 'jja', 'son'
seasons = [djf, mam, jja, son]

# Define regions
stat = 'rms_xy'
regions = ['global', 'NHEX', 'TROPICS', 'SHEX']

# Loop through seasons and generate plots
for season in seasons:
    data1 = normalize_by_median(df_dict[stat][season]['global'][var_list].to_numpy())
    data2 = normalize_by_median(df_dict[stat][season]['NHEX'][var_list].to_numpy())
    data3 = normalize_by_median(df_dict[stat][season]['TROPICS'][var_list].to_numpy())
    data4 = normalize_by_median(df_dict[stat][season]['SHEX'][var_list].to_numpy())

    data_regions_nor = np.stack([data1, data2, data3, data4])

    fig, ax, cbar = portrait_plot(data_regions_nor,
                                  xaxis_labels=xaxis_labels,
                                  yaxis_labels=yaxis_labels,
                                  cbar_label='RMSE',
                                  box_as_square=True,
                                  vrange=(-0.5, 0.5),
                                  figsize=(15, 18),
                                  cmap='RdYlBu_r',
                                  cmap_bounds=[-0.5, -0.4, -0.3, -0.2, -0.1, 0, 0.1, 0.2, 0.3, 0.4, 0.5],
                                  cbar_kw={"extend": "both"},
                                  missing_color='grey',
                                  cbar_label_fontsize=16,
                                  cbar_tick_fontsize=15,
                                  legend_on=True,
                                  legend_labels=regions,
                                  legend_box_xy=(1.25, 1),
                                  legend_box_size=4,
                                  legend_lw=1,
                                  legend_fontsize=13,
                                  logo_off=True,
                                  logo_rect=[0.85, 0.15, 0.07, 0.07]
                                 )
    ax.set_xticklabels(xaxis_labels, rotation=45, va='bottom', ha="left")

    # Add title for each season
    ax.set_title(f"{season.upper()} climatology RMSE-{convention}", fontsize=30, pad=30)

    # Save figure as an image file for each season
    fig.savefig(f'mean_clim_portrait_plot_4regions_{season.upper()}_{convention}.png', facecolor='w', bbox_inches='tight')

    # Close the figure to release memory
    plt.close(fig)
    
# Loop through regions and generate plots
for region in regions:
    data1 = normalize_by_median(df_dict[stat]['djf'][region][var_list].to_numpy())
    data2 = normalize_by_median(df_dict[stat]['mam'][region][var_list].to_numpy())
    data3 = normalize_by_median(df_dict[stat]['jja'][region][var_list].to_numpy())
    data4 = normalize_by_median(df_dict[stat]['son'][region][var_list].to_numpy())

    data_seasons_nor = np.stack([data1, data2, data3, data4])

    fig, ax, cbar = portrait_plot(data_seasons_nor,
                                  xaxis_labels=xaxis_labels,
                                  yaxis_labels=yaxis_labels,
                                  cbar_label='RMSE',
                                  box_as_square=True,
                                  vrange=(-0.5, 0.5),
                                  figsize=(15, 18),
                                  cmap='RdYlBu_r',
                                  cmap_bounds=[-0.5, -0.4, -0.3, -0.2, -0.1, 0, 0.1, 0.2, 0.3, 0.4, 0.5],
                                  cbar_kw={"extend": "both"},
                                  missing_color='grey',
                                  cbar_label_fontsize=16,
                                  cbar_tick_fontsize=15,
                                  legend_on=True,
                                  legend_labels=seasons,
                                  legend_box_xy=(1.25, 1),
                                  legend_box_size=4,
                                  legend_lw=1,
                                  legend_fontsize=13,
                                  logo_off=True,
                                  logo_rect=[0.85, 0.15, 0.07, 0.07]
                                 )
    ax.set_xticklabels(xaxis_labels, rotation=45, va='bottom', ha="left")

    # Add title for each region
    ax.set_title(f"{region.upper()} climatology RMSE-{convention}", fontsize=30, pad=30)

    # Save figure as an image file for each region
    fig.savefig(f'{outdir}mean_clim_portrait_plot_4seasons_{region.upper()}_{convention}.png', facecolor='w', bbox_inches='tight')

    # Close the figure to release memory
    plt.close(fig)
