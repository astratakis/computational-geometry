import geopandas as gpd
import matplotlib.pyplot as plt

# Custom libraries.
from dcel import *
from algorithms import *

# load a .shp file
gdf = gpd.read_file("testfiles/gshhg-shp-2.3.7/GSHHS_shp/f/GSHHS_f_L1.shp")

#gdf.plot()
#plt.show()

polygons = gdf['geometry']

print(gdf)

polygon = polygons[100]

all_points = [(polygon.exterior.coords[i][0], polygon.exterior.coords[i][1]) for i in range(len(polygon.exterior.coords))]
x, y = zip(*all_points)

figure = plt.figure()
plt.plot(x, y, '-')
plt.title('Polyline construction')

poly = Dcel()
poly.build_from_polygon(polygon)
plt.show()

triangulate_polygon(polygon=poly)

figure = poly.__plot__()
plt.show()
