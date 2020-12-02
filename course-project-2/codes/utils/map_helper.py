from __future__ import print_function
import io
import folium
from PIL import Image
import selenium

__all__ = ['save_fmap_plot', 'get_map_tiles', 'get_porto_coords', 'get_color_list',
          'get_xy_bounds', 'get_global_xy_bounds']

def save_fmap_plot(fmap, filename) -> None:
    """
    Saves Folium map to file.
    
    Parameters:
        fmap (object): Folium map object.
        filename (str): Name of file without file extension.
    """
    img_data = fmap._to_png(5)
    img = Image.open(io.BytesIO(img_data))
    img.save(filename+".png")
    
    
def get_map_tiles() -> list:
    """
    Returns list of Folium map tiles.
    """
    return ['OpenStreetMap','Stamen Terrain','Stamen Toner','Mapbox Bright','Mapbox Control Room']

def get_porto_coords(adjusted=True):
    """
    Returns tuple of Porto City coordinates.
    """
    porto_lat = 41.1496100
    porto_lon = -8.6109900
    if adjusted:
        porto_lat += 0.01
        porto_lon -= 0.02
    return (porto_lat, porto_lon)

def get_color_list() -> dict:
    """
    Returns a set of 10 color list with two modes:
        'bob': Black on black backgrounds are colours for black backgrounds.
        'bog': Black on grey backgrounds are colours for grey backgrounds.
    """
    color_dict = {
        'bob': ['crimson', 'blue', 'orange', 'green', 'magenta', 'pink', 'purple', 'cyan', 'orangered', 'olive'],
        'bog': ['crimson', 'blue', 'orange', 'green', 'orangered', 'deepskyblue', 'purple', 'cyan', 'magenta', 'teal'],
    }
    return color_dict

def get_xy_bounds(lcoord):
    """
    Returns min max bounds of single LineString coordinates.
    """
    x_min, x_max = 9999, -9999
    y_min, y_max = 9999, -9999 
    x_min = min(x_min, min([i[0] for i in lcoord]))
    x_max = max(x_max, max([i[0] for i in lcoord]))
    y_min = min(y_min, min([i[1] for i in lcoord]))
    y_max = max(y_max, max([i[1] for i in lcoord]))
    return [[x_min, y_min], [x_max, y_max]]
    
def get_global_xy_bounds(gdf, adjustx=0., adjusty=0.):
    """
    Returns min max bounds of single LineString coordinates in DataFrame.
    """
    x_min, x_max = 9999, -9999
    y_min, y_max = 9999, -9999 
    x_min = min(x_min, min([i[0] for lcoord in gdf for i in lcoord]))
    x_max = max(x_max, max([i[0] for lcoord in gdf for i in lcoord]))
    y_min = min(y_min, min([i[1] for lcoord in gdf for i in lcoord]))
    y_max = max(y_max, max([i[1] for lcoord in gdf for i in lcoord]))
    return [[x_min+adjustx, y_min+adjusty], [x_max-adjustx, y_max-adjusty]]