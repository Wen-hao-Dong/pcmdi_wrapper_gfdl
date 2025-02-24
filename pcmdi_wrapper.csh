#!/bin/csh
module load conda
conda activate /home/mdteam/pcmdi_metrics/v2.2.2/env

################################################################
#Version0 written by Wenhao Dong(Wenhao.Dong@noaa.gov), Dec 2024  
################################################################

# Define input arguments with fixed values
set PPDIR = "/archive/oar.gfdl.am5/am5/am5f7c1r0/c96L65_am5f7c1r0_amip/gfdl.ncrc5-deploy-prod-openmp/pp/atmos_cmip/ts/monthly/1yr"
set DESCRIPTOR = "c96L65_am5f7c1r0_amip"
set CONVENTION = "AMIP"
set YR1 = 1980
set YR2 = 2014
set OUTDIR = "./"
set PMP_DATA_ROOT = "/home/mdteam/pcmdi_metrics"

# Step 1: Run generate_pmp_metrics.py to save data and generate param.py
python generate_pmp_metrics.py --ppdir "$PPDIR" --descriptor "$DESCRIPTOR" --yr1 "$YR1" --yr2 "$YR2" --outdir "$OUTDIR" --pmp_data_root "$PMP_DATA_ROOT"

# Step 2: Execute mean_climate_driver.py to process the data
mean_climate_driver.py --save_test_clims False -p param.py

# Step 3: Generate plots by running portrait_plot.py
python portrait_plot.py --pmp_data_root "$PMP_DATA_ROOT" --convention "$CONVENTION" --outdir "$OUTDIR"  

# Step 4: Generate html page by running html_generate.py  
python html_generate.py  --descriptor "$DESCRIPTOR" --convention "$CONVENTION" --outdir "$OUTDIR"  

# Indicate completion
echo "All steps completed successfully."

