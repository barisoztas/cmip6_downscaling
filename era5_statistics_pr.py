import os
import datetime
import pathlib

import geopandas as gpd
import pandas as pd
import xarray as xr
from rasterstats import zonal_stats
import rasterio as rio
import numpy as np


class Era5Extraction(object):
    def __init__(self):
        # Define folder where grids are reside in
        self.start_time = datetime.datetime.now()
        self.PARAMETER = 'tp'
        self.input_folder_era5 = r"/home/hsaf/ponderful/ERA5/total_precipitation/daily_precipitation"
        self.output_folder_zonal_stats = r"./results/ZonalStats"
        self.grid_folder = r"./results/elevation_median/pr/"
        self.era5_path = None
        self.era5_ds = None
        self.grid_list = []
        self.current_grid = None
        self.results_database = []

    def find_era5(self):
        for era5 in pathlib.Path(self.input_folder_era5).glob('**/total_precipitation_daily_1979_2014.nc'):
            self.era5_path = era5
        print("ERA5 is found!")

    def find_cmip6_grids(self):
        for grid_file in pathlib.Path(self.grid_folder).glob('**/*.shp'):
            self.grid_list.append(grid_file)
        print("Grids of CMIP6 is found!")

    def read_era5(self):
        self.era5_ds = xr.load_dataset(self.era5_path, engine='scipy')
        self.era5_ds = self.era5_ds[self.PARAMETER]
        self.era5_da = self.era5_ds[:,:,:]
        print("ERA5 is read!")

    def calculate_zonal_stats(self, grid_polygon):
        self.results_database = []

        affine = rio.open(self.era5_path).transform
        shp_df = gpd.read_file(grid_polygon)
        # loop into geometries of grids of CMIP6
            # get the days of era5
        all_days = self.era5_ds['time'].values
        # loop into each day and calculate statistics
        for day in range(len(all_days)):
            era5_da = self.era5_ds[day,:,:]
            era5_da = era5_da.values
            era5_stats = zonal_stats(shp_df.geometry, era5_da,
                                         affine=affine, stats=['min', 'max', 'median', 'mean', 'count', 'sum'])
            current_date = all_days[day]
            date = np.full(shape=len(era5_stats),fill_value=current_date)
            era5_stats_pd = pd.DataFrame.from_records(era5_stats)
            era5_stats_pd["date"] = date
            self.results_database.append(era5_stats_pd)

            # see progress in the console
            print(f"Total Processed Day: {day+1}/{len(all_days)}")
        self.results_database = pd.concat(self.results_database)
        current_grid_name = '-'.join((os.path.split(current_cmip6_grid)[1]).split('_')[1:-1])
        write_path = os.path.join(self.output_folder_zonal_stats, current_grid_name+'.csv')
        new_column_names = ['min_era5', 'max_era5','mean_era5', 'count_era5', 'sum_era5', 'median_era5', 'date']
        self.results_database.set_axis(new_column_names, axis=1, inplace=True)
        new_column_names_sorted = ['date', 'count_era5', 'min_era5', 'max_era5', 'median_era5', 'mean_era5']
        self.results_database = self.results_database.reindex(columns = new_column_names_sorted)
        self.results_database.to_csv(path_or_buf=write_path, index_label='id')

if __name__ == '__main__':
    ERA5ExtractionObject = Era5Extraction()
    ERA5ExtractionObject.find_era5()
    ERA5ExtractionObject.read_era5()
    ERA5ExtractionObject.find_cmip6_grids()
    for current_cmip6_grid in ERA5ExtractionObject.grid_list:
        grid_name = '-'.join((os.path.split(current_cmip6_grid)[1]).split('_')[1:-1])
        print(f"Processing {grid_name}!!: Here is the results:")
        ERA5ExtractionObject.calculate_zonal_stats(current_cmip6_grid)
