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
        self.input = r"./cmip6_outputs"
        self.output = r"./cmip6_outputs/output"
        self.cmip6_nc_list = []
        self.cmip6_shp_list = []
        self.results_database = []

    def find_cmip6_netcdf(self):
        for cmip6 in pathlib.Path(self.input).glob('**/*.nc'):
            self.cmip6_nc_list.append(cmip6)

    def find_cmip6_grids(self):
        for cmip6_grid in pathlib.Path(self.input).glob('**/*.shp'):
            self.cmip6_shp_list.append(cmip6_grid)

    def extract_cmip6(self, cmip6_nc_path, cmip6_shp_path):
        self.results_database = []
        cmip6_nc = xr.open_dataset(cmip6_nc_path)
        affine = rio.open(cmip6_nc_path).transform
        shp_df = gpd.read_file(cmip6_shp_path)
        all_days = cmip6_nc['time'].values  # get the days of cmip6
        # loop into each day and calculate statistics
        for day in range(len(all_days)):
            variable = cmip6_nc.variable_id
            cmip6_da = cmip6_nc[variable][day, :, :]
            cmip6_da = cmip6_da.values
            cmip6_values = zonal_stats(shp_df.geometry, cmip6_da,
                                     affine=affine, stats=['majority'])
            current_date = all_days[day]
            date = np.full(shape=len(cmip6_values), fill_value=current_date)
            cmip6_values_pd = pd.DataFrame.from_records(cmip6_values)
            cmip6_values_pd["date"] = date
            self.results_database.append(cmip6_values_pd)

            # see progress in the console
            print(f"Total Processed Day: {day + 1}/{len(all_days)}")
        self.results_database = pd.concat(self.results_database)
        current_grid_name = '-'.join(os.path.split(current_cmip6_shp)[1].split('_')[1:-1])
        write_path = os.path.join(self.output, current_grid_name + '.csv')
        new_column_names = ['cmip6_value', 'date']
        self.results_database.set_axis(new_column_names, axis=1, inplace=True)
        self.results_database.to_csv(path_or_buf=write_path, index_label='id')


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
