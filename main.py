from datetime import datetime
import pathlib
import os
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point


class cmip6_stations_selection(object):
    def __init__(self):
        # Define folder where grids are reside in
        self.start_time = datetime.now()
        self.grid_folder = r"/home/baris/PycharmProjects/cmip6_downscaling/results/elevation_median/"
        self.station_csv = r"/home/baris/PycharmProjects/cmip6_downscaling/tr_stations/stations.csv"
        self.output_folder = r"/home/baris/PycharmProjects/cmip6_downscaling/output/"
        self.tr_stations_pandas = None
        self.tr_stations_geopandas = None
        self.grid_list = []
        self.current_grid = None

    def calculate_time(self):
        end_time = datetime.now()
        total_time = self.start_time-end_time
        print(f"Total time: {total_time} minutes")

    def find_cmip6_grids(self):
        for grid_file in pathlib.Path(self.grid_folder).glob('**/*.shp'):
            self.grid_list.append(grid_file)

    def read_grid(self, grid):
        self.current_grid = gpd.read_file(grid)
        return self.current_grid

    def read_stations(self):
        self.tr_stations_pandas = pd.read_csv(self.station_csv)
        geometry_stations = [Point(xy) for xy in zip(self.tr_stations_pandas.longitude,
                                                     self.tr_stations_pandas.latitude)]
        self.tr_stations_geopandas = gpd.GeoDataFrame(self.tr_stations_pandas, geometry=geometry_stations,
                                                      crs="EPSG:4326")

    def find_representative_stations(self, cmip6_grid, current_grid):
        station_list = []
        for index, row in cmip6_grid.iterrows():
            polygon_geometry = row["geometry"]
            df = pd.DataFrame({'wkt': [polygon_geometry]})
            polygon_df = gpd.GeoDataFrame(df,
                                          crs='epsg:4326',
                                          geometry=[polygon_geometry])
            pts_in_poly = gpd.sjoin(self.tr_stations_geopandas, polygon_df, how='inner', predicate='within')
            grid_elevation = row.elevation_

            # choosing the oldest station if there is more than one closest elevation
            sorted_stations = pts_in_poly.iloc[(pts_in_poly['elevation'] - grid_elevation).abs().argsort()]
            best_elevation = sorted_stations[:1].elevation.to_numpy()
            elevation_mask = sorted_stations['elevation'].values == best_elevation
            best_stations = sorted_stations[elevation_mask]
            best_stations['establish'] = pd.to_datetime(best_stations['establish'], format='%Y-%m-%d')
            best_stations = best_stations.sort_values(by="establish")

            # save best representative stations to dataframe
            station_list.append(best_stations)

#           if len(station_elevation_list) == 0:
#               print("There is no station in the grid!")
#               print("---------------------------------------------------------------")
#           else:
#               print(f"Mean grid elevation is: {grid_elevation}")
#               print(f"Elevations of stations are {station_elevation_list.tolist()}")
#               print("---------------------------------------------------------------")
        output_path = os.path.join(self.output_folder, current_grid + '_stations.csv')
        station_list = pd.concat(station_list)
        station_list.to_csv(output_path)


if __name__ == "__main__":
    cmip6_stations_selection_object = cmip6_stations_selection()
    cmip6_stations_selection_object.find_cmip6_grids()
    for current_cmip6_grid in cmip6_stations_selection_object.grid_list:
        grid_name = '-'.join((os.path.split(current_cmip6_grid)[1]).split('_')[1:-1])
        print(f"Processing {grid_name}!!: Here is the results:")
        current_cmip6_grid = cmip6_stations_selection_object.read_grid(current_cmip6_grid)
        cmip6_stations_selection_object.read_stations()
        cmip6_stations_selection_object.find_representative_stations(current_cmip6_grid, grid_name)
        cmip6_stations_selection_object.calculate_time()
        
