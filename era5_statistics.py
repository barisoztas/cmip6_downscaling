import os
import datetime
import pathlib

import xarray
from rasterstats import zonal_stats
import rasterio as rio
import fiona


class Era5Extraction(object):
    def __init__(self):
        # Define folder where grids are reside in
        self.start_time = datetime.datetime.now()
        self.input_folder_era5 = r"/home/hsaf/ponderful/ERA5/2m_temperature/daily_era5"
        self.output_folder_zonal_stats = r"/home/hsaf/ponderful/ERA5/ZonalStats"
        self.grid_folder = r"/home/hsaf/PycharmProjects/cmip6_downscaling/results/elevation_median/"
        self.era5_path = None
        self.era5_ds = None
        self.grid_list = []
        self.current_grid = None

    def find_era5(self):
        for era5 in pathlib.Path(self.input_folder_era5).glob('**/*daily*.nc'):
            self.era5_path = era5
        print("ERA5 is found!")

    def find_cmip6_grids(self):
        for grid_file in pathlib.Path(self.grid_folder).glob('**/*.shp'):
            self.grid_list.append(grid_file)
        print("Grids of CMIP6 is found!")

    def read_era5(self):
        self.era5_ds = xarray.load_dataset(self.era5_path)
        print("ERA5 is read!")

    def calculate_zonal_stats(self, grid_polygon):

        # loop into geometries of grids of CMIP6
        with fiona.open(grid_polygon) as src:

            # get the days of era5
            all_days = self.era5_ds['time'].values

            # loop into each day and calculate statistics
            for day in all_days:
                affine = rio.open(self.era5_path).transform
                era5_ds_day = self.era5_ds.sel(time=day).values

                era5_stats = zonal_stats(src, era5_ds_day, affine=affine,
                                         stats=['min', 'max', 'median', 'mean'])
                print(era5_stats)

    def report_output(self):
        pass


if __name__ == '__main__':
    ERA5ExtractionObject = Era5Extraction()
    print('Hello World!')
    ERA5ExtractionObject.find_era5()
    ERA5ExtractionObject.read_era5()
    ERA5ExtractionObject.find_cmip6_grids()
    for current_cmip6_grid in ERA5ExtractionObject.grid_list:
        grid_name = '-'.join((os.path.split(current_cmip6_grid)[1]).split('_')[1:-1])
        print(f"Processing {grid_name}!!: Here is the results:")
        ERA5ExtractionObject.calculate_zonal_stats(current_cmip6_grid)
