import os
import glob
import subprocess
import xarray as xr
import cftime
import datetime
import numpy as np
import pandas as pd
import argparse

# Parse input arguments
parser = argparse.ArgumentParser(description="Process climate data and generate PMP parameter file.")
parser.add_argument('--ppdir', type=str, required=True, help='Path to post-processed data directory')
parser.add_argument('--descriptor', type=str, required=True, help='Descriptor for the experiment')
parser.add_argument('--yr1', type=int, required=True, help='Start year for the analysis')
parser.add_argument('--yr2', type=int, required=True, help='End year for the analysis')
parser.add_argument('--outdir', type=str, required=True, help='Output directory for results')
parser.add_argument('--pmp_data_root', type=str, required=True, help='Path to PMP data root')
args = parser.parse_args()

# Step 1: Define directories and parameters
ppdir = args.ppdir
descriptor = args.descriptor
yr1 = args.yr1
yr2 = args.yr2
outdir = args.outdir
pmp_data_root = args.pmp_data_root

# Define GFDL to CMOR variable mapping
varmap = {
    "hur": None,
    "hurs": None,
    "hus": None,
    "huss": None,
    "pr": "pr",
    "prw": "prw",
    "psl": "psl",
    "rlds": "rlds",
    "rltcre": None,
    "rlus": "rlus",
    "rlut": "rlut",
    "rlutcs": "rlutcs",
    "rsds": "rsds",
    "rsdscs": "rsdscs",
    "rsdt": "rsdt",
    "rstcre": None,
    "rsus": "rsus",
    "rsut": "rsut",
    "rsutcs": "rsutcs",
    "sfcWind": "sfcWind",
    "ta": "ta",
    "tas": "tas",
    "tauu": "tauu",
    "tauv": "tauv",
    "ua": "ua",
    "va": "va",
    "zg": "zg",
}

varmap = {k: v for k, v in varmap.items() if v is not None}

tcoord = "time"

# Step 3: Aggregate the files into a single xarray DataSet
# construct a list of relevant files that match the variable names defined above
files = [glob.glob(f"{ppdir}/*.{var}.nc") for var in varmap.values()]
files = sorted([file for sublist in files for file in sublist])

def is_in_range(filepath,yr1,yr2):
    
    yr1 = -99999 if yr1 is None else yr1
    yr2 = 99999 if yr2 is None else yr2
    
    filename = os.path.split(filepath)[-1]
    years = filename.split(".")[1].split("-")
    years = [int(x[0:4]) for x in years]
    if (years[1] < int(yr1)) or (years[0] > int(yr2)):
        result = False
    else:
        result = True
    return result
    
files = [x for x in files if is_in_range(x,yr1,yr2)]

# load all variables into an xarray dataset and subset in time
dset_in = xr.open_mfdataset(files, use_cftime=True, compat="override", coords="all")

# subset in time
_yr1 = f"{yr1}-01-01" if yr1 is not None else None
_yr2 = f"{yr2}-12-31" if yr2 is not None else None

dset_in = dset_in.sel({tcoord: slice(_yr1, _yr2)})

# find median year and save time axis
median_year = str(int(dset_in[tcoord].dt.year.median())).zfill(4)
tax = dset_in[tcoord].sel({tcoord:slice(f"{median_year}-01-01", f"{median_year}-12-31")})
print(median_year)
print('----------------------')
print(tax)
print('----------------------')

# determine time range of the data and generate a string
timerange = (
    dset_in[tcoord].values[0].strftime("%Y%m")
    + "-"
    + dset_in[tcoord].values[-1].strftime("%Y%m")
)
print(timerange)

# cross reference full GFDL variable mapping against
# the contents of the actual dataset
varmap = {k: v for k, v in varmap.items() if v in dset_in.keys()}

# rename variables with their CMOR names
dset_in = dset_in.rename({v:k for k,v in varmap.items()})

# create annual cycle climatologies
dset = dset_in.groupby(f"{tcoord}.month").mean(tcoord)

# rename the time coordinate back to its original value
dset = dset.rename({"month":tcoord})

# reassign the median year time axis that we saved earlier
dset = dset.assign_coords({tcoord:tax})

# output directory for the climatology files
climdir = f"{outdir}/clims"
_ = os.makedirs(climdir, exist_ok=True)


# today's datestamp string to use as version number
datestamp = datetime.datetime.now().strftime("%Y%m%d")

# list of GFDL-specific post-processing varaibles that are not used by PMP
gfdl_exclusion_list = ["average_DT", "average_T1", "average_T2", "lat_bnds", "lon_bnds"]

# retain relevant variables for processing
varlist = sorted([x for x in dset.keys() if x not in gfdl_exclusion_list])
for var in varlist:
    
    # construct output filename
    ncfile = f"{climdir}/gfdl.experiment.{descriptor}.r1i1p1.mon.{var}.{timerange}.AC.v{datestamp}.nc"
    print(ncfile)
    
    # establish a new xarray.DataSet for the variable and horizontal bounds
    _dset = xr.Dataset(
        {var: dset[var], "lat_bnds": dset["lat_bnds"], "lon_bnds": dset["lon_bnds"]}
    )
    
    # rename the bounds dimension
    _dset = _dset.rename({"bnds": "bound"})

    # cleanup the latitude and longitude attributes
    _dset["lat"].attrs["units"] = "degrees_north"
    _dset["lat"].attrs["standard_name"] = "latitude"
    _dset["lat"].attrs["realtopology"] = "linear"

    _dset["lon"].attrs["units"] = "degrees_east"
    _dset["lon"].attrs["standard_name"] = "longitude"
    _dset["lon"].attrs["realtopology"] = "circular"
    _dset["lon"].attrs["modulo"] = 360.0

    # copy original variable attributes to the climatology
    _dset[var].attrs = dset_in[var].attrs

    # remove time bounds attribute (xarray will handle adding the correct bounds, if needed)
    del _dset["time"].attrs["bounds"]

    # set variable's _FillValue and remove all other _FillValues
    for _var in _dset.variables:
        fillvalue = -999.0 if _var == var else None
        _dset[_var].encoding = {"_FillValue": fillvalue}

    # save to NetCDF file
    _dset.to_netcdf(ncfile)

vars_4d = {
    "ta": ["_850", "_200"],
    "ua": ["_850", "_200"],
    "va": ["_850", "_200"],
    "zg": ["_500"],
}

modified_4d_varnames = []
for var in vars_4d.keys():
    if var in varlist:
        varlist.remove(var)
        for level in vars_4d[var]:
            modified_4d_varnames.append(var+level)

varlist = sorted(varlist + modified_4d_varnames)

# construct a dictionary of PMP parameters
parameters = {
    "case_id": "metrics",
    "test_data_set": [descriptor],
    "vars": varlist,
    "reference_data_set": ["all"],
    "target_grid": "2.5x2.5",
    "regrid_tool": "regrid2",
    "regrid_method": "linear",
    "regrid_tool_ocn": "esmf",
    "regrid_method_ocn": "linear",
    "filename_template": f"gfdl.experiment.%(model_version).r1i1p1.mon.%(variable).{timerange}.AC.v{datestamp}.nc",
    "sftlf_filename_template": "sftlf_%(model_version).nc",
    "generate_sftlf": True,
    "regions": {"rsus": ["Global"]},
    "test_data_path": climdir,
    "reference_data_path": f"{pmp_data_root}/obs_clim/v20210804/",
    "metrics_output_path": f"{outdir}/results/",
}

# save the parameters to a .py file (would be cleaner to somehow invoke PMP directly)
with open("param.py", "w") as f:
    for k, v in parameters.items():
        if isinstance(v, str):
            f.write(f"{k} = '{v}'\n")
        else:
            f.write(f"{k} = {v}\n")

f.close()
