import os
import datetime
import pathlib
from datetime import datetime

import xarray as xr
import geopandas as gpd
from rasterstats import zonal_stats
import rasterio as rio
import numpy as np
import pandas as pd


class CMIP6Extraction(object):
    def __init__(self):
        self.input = r"/home/baris/Desktop/new/data/cmip6/models/tas_day_CNRM-ESM2-1_historical_r1i1p1f2_gr_1995_2004"
        self.output = r"/home/baris/Desktop/new/data/cmip6/output"
        self.cmip6_nc_list = []
        self.cmip6_shp_list = []
        self.results_database = []

    def find_cmip6_netcdf(self):
        for cmip6 in pathlib.Path(self.input).glob('**/tas_day_CNRM-ESM2-1_historical_r1i1p1f2_gr_1995_2004.nc'):
            self.cmip6_nc_list.append(cmip6)

    def find_cmip6_grids(self):
        for cmip6_grid in pathlib.Path(self.input).glob('**/*.shp'):
            self.cmip6_shp_list.append(cmip6_grid)

    def extract_cmip6(self, cmip6_nc_path, cmip6_shp_path):
        self.results_database = []
        cmip6_name = '-'.join(os.path.split(current_cmip6_shp)[1].split('_')[1:-1])

        cmip6_nc = xr.open_dataset(cmip6_nc_path)
        shp_df = gpd.read_file(cmip6_shp_path)
        # loop into each day and calculate statistics
        for i in range(len(shp_df)):
            lon = shp_df['geometry'][i].x
            lat = shp_df['geometry'][i].y
            dataset = cmip6_nc.sel(lat=lat, lon=lon,method='nearest')
            values = dataset.tas.to_numpy()
            date = dataset.time.to_numpy()
            id = shp_df['id'][i]
            self.results_database.append(pd.DataFrame({
                'cmip6_values': values,
                'date':date,
                'id':id
            }))
            print(f"Total grid processed: {i+1}/{len(shp_df)}")
        self.results_database = pd.concat(self.results_database)
        self.results_database.to_csv(os.path.join(self.output, cmip6_name+'.csv'))



if __name__ == '__main__':
    CMIP6ExtractionObject = CMIP6Extraction()
    CMIP6ExtractionObject.find_cmip6_netcdf()
    CMIP6ExtractionObject.find_cmip6_grids()
    for i in range(len(CMIP6ExtractionObject.cmip6_shp_list)):
        current_cmip6_nc = CMIP6ExtractionObject.cmip6_nc_list[i]
        current_cmip6_shp = CMIP6ExtractionObject.cmip6_shp_list[i]
        print(f"{current_cmip6_nc}")
        print(f"{current_cmip6_shp}")
        cmip6_name = '-'.join(os.path.split(current_cmip6_shp)[1].split('_')[1:-1])
        print(f"Data extraction for {cmip6_name} began at {datetime.now().strftime('%H:%M:%S')}")
        CMIP6ExtractionObject.extract_cmip6(current_cmip6_nc, current_cmip6_shp)
