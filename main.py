import geopandas as gpd
import matplotlib.pyplot as plt

# Data strucrure libraries.
from collections import deque

# Custom libraries.
from dcel import *
from algorithms import *

# load a .shp file
gdf = gpd.read_file("testfiles/gshhg-shp-2.3.7/GSHHS_shp/h/GSHHS_h_L1.shp")

#gdf.plot()
#plt.show()

polygons = gdf['geometry']

print(gdf)

polygon = polygons[100]

x_values = [polygon.exterior.coords[i][0] for i in range(len(polygon.exterior.coords))]
y_values = [polygon.exterior.coords[i][1] for i in range(len(polygon.exterior.coords))]

n = len(x_values)

recon = plt.figure()
plt.scatter(x_values, y_values, s=1)
plt.title('Sample Points')
plt.show()

all_points = [(polygon.exterior.coords[i][0], polygon.exterior.coords[i][1]) for i in range(len(polygon.exterior.coords))]
x, y = zip(*all_points)

figure = plt.figure()
plt.plot(x, y, '-')
plt.title('Polyline construction')
plt.show()

poly = DCEL(all_points[::-1])

monotonize_simple_polygon(poly)

poly.__plot__()