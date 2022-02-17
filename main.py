import pandas as pd
import geopandas as gpd
from shapely.geometry import Point


class cmip6_stations_selection(object):

    def __init__(self):
        self.grid_folder = r"/home/baris/PycharmProjects/cmip6_downscaling/results/elevation_wgs84/"
        self.cmip6_grid_file = r"/home/baris/PycharmProjects/cmip6_downscaling/results/elevation_wgs84/" \
                               r"elevation_grid_access_cm_2_rotated.shp"

        self.station_csv = r"/home/baris/PycharmProjects/cmip6_downscaling/tr_stations/stations.csv"
        self.output_folder = r"/home/baris/PycharmProjects/cmip6_downscaling/output/"
        self.cmip6_grid = None
        self.tr_stations_pandas = None
        self.tr_stations = None
        self.tr_stations_geopandas = None

    def read_grid(self):
        self.cmip6_grid = gpd.read_file(self.cmip6_grid_file)
        return self.cmip6_grid

    def read_stations(self):
        self.tr_stations_pandas = pd.read_csv(self.station_csv)
        geometry_stations = [Point(xy) for xy in zip(self.tr_stations_pandas.longitude,
                                                     self.tr_stations_pandas.latitude)]
        self.tr_stations_geopandas = gpd.GeoDataFrame(self.tr_stations_pandas, geometry=geometry_stations,
                                                      crs="EPSG:4326")

    def find_representative_stations(self, cmip6_grid):
        for index, row in cmip6_grid.iterrows():
            polygon_geometry = row["geometry"]
            df = pd.DataFrame({'wkt': [polygon_geometry]})
            polygon_df = gpd.GeoDataFrame(df,
                                          crs='epsg:4326',
                                          geometry=[polygon_geometry])
            pts_in_poly = gpd.sjoin(self.tr_stations_geopandas, polygon_df, how='inner', predicate='within')
            grid_elevation = row.elevation_
            station_elevation_list = pts_in_poly.elevation

            if len(station_elevation_list) == 0:
                print("There is no station in the grid!")
                print("---------------------------------------------------------------")
            else:
                print(f"Mean grid elevation is: {grid_elevation}")
                print(f"Elevations of stations are {station_elevation_list.tolist()}")
                print("---------------------------------------------------------------")


if __name__ == "__main__":
    cmip6_stations_selection_object = cmip6_stations_selection()
    current_cmip6_grid = cmip6_stations_selection_object.read_grid()
    cmip6_stations_selection_object.read_stations()
    cmip6_stations_selection_object.find_representative_stations(current_cmip6_grid)
