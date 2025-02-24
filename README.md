# pcmdi_wrapper_gfdl
This repository contains a wrapper for generating PCMDI portrait plots using GFDL model output.

## Overview
This wrapper script automates the execution of the PCMDI Metrics Package (PMP) by first activating the pre-installed Conda environment and then defining essential settings before running the analysis workflow. Ensure you have access to the pre-installed Conda environment located at: /home/mdteam/pcmdi_metrics/v2.2.2/env. The wrapper is written by Wenhao Dong (Wenhao.Dong@noaa.gov) to support AM5 model development.

## Configuration Settings

Before running the script, a few key variables must be defined:

**PPDIR**, Directory containing the monthly output data to be analyzed. (e.g. /archive/oar.gfdl.am5/am5/am5f7c1r0/c96L65_am5f7c1r0_amip/gfdl.ncrc5-deploy-prod-openmp/pp/atmos_cmip/ts/monthly/1yr)

**DESCRIPTOR**, User-defined name for the simulation. (e.g. c96L65_am5f7c1r0_amip)

**CONVENTION**, Specifies the comparison dataset, which can be "HIST" or "AMIP": "HIST" → Compares with CMIP6 historical simulations.  "AMIP" → Compares with CMIP6 AMIP-type simulations.

**YR1**, User-defined starting year of the analysis period (e.g., 1980)

**YR2**, User-defined ending year of the analysis period (e.g., 2014)

**OUTDIR**, Directory where the results (processed climatological data and plots) will be saved.

**PMP_DATA_ROOT**, Root directory containing pre-calculated CMIP6 datasets. Default "/home/mdteam/pcmdi_metrics"

## Workflow: Running the PCMDI Metrics Package

The process consists of four steps:

#Step 1: Run generate_pmp_metrics.py to save data and generate param.py

    python generate_pmp_metrics.py --ppdir "$PPDIR" --descriptor "$DESCRIPTOR" --yr1 "$YR1" --yr2 "$YR2" --outdir "$OUTDIR" --pmp_data_root "$PMP_DATA_ROOT"

#Step 2: Execute mean_climate_driver.py to process the data

    mean_climate_driver.py --save_test_clims False -p param.py

#Step 3: Generate plots by running portrait_plot.py

    python portrait_plot.py --pmp_data_root "$PMP_DATA_ROOT" --convention "$CONVENTION" --outdir "$OUTDIR"

#Step 4: Generate html page by running html_generate.py

    python html_generate.py --descriptor "$DESCRIPTOR" --convention "$CONVENTION" --outdir "$OUTDIR"


## Additional Notes
- Ensure that all required dependencies are installed before running the scripts.
- Modify the configuration parameters as needed for different datasets and experiments.
- For troubleshooting or further customizations, refer to the official [PCMDI Metrics](https://pcmdi.github.io/pcmdi_metrics/) documentation.

## Acknowledgment
I would like to express my gratitude to John Krasting (John.Krasting@noaa.gov) for guiding me in using the PCMDI package and providing the two original notebooks. I also appreciate the support from the AM5DT leads team and thank Huan Guo (Huan.Guo@noaa.gov) for assistance with testing.
