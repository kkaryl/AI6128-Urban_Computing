from __future__ import print_function
import os
import geopandas as gpd
import pandas as pd
import json
from shapely.geometry import Point, LineString
import shapely.wkt

from pyproj import CRS
crs = CRS("EPSG:4326")

__all__ = ['get_train1000_df', 'get_lineString_gdf', 'get_coords', 'get_lineString_coords',
          'get_mm_results_df', 'get_geom_gdf']

def get_train1000_df(file_path, dedup=False):
    """
    Returns a dataframe containing "POLYLINE" column from train-1000.csv file.
    
    Parameters:
        data_dir (str): Directory containing train-1000.csv.
        dedup (bool): Removes inorder duplicated points from trajectories if set to True.
    """
    train1000 = pd.read_csv(file_path,
                            sep = ",", usecols=['POLYLINE'],
                            converters={'POLYLINE': lambda x: json.loads(x)})
    if dedup:
        # Remove inorder duplicated points from trajectories
        cleaned_list = []
        dedup_ctr = 0
        for k in train1000["POLYLINE"]:
            dedup_ks = [k[i] for i in range(len(k)) if i == 0 or k[i] != k[i-1]]
            if len(dedup) != len(k):
                dedup_ctr += 1
            cleaned_list.append(dedup_ks)

        print(f"Removed duplicated points from {dedup_ctr} trajectories.")        
        train1000["POLYLINE"] = cleaned_list
        
    return train1000

def get_lineString_gdf(train_df, verbose=True):
    """
    Returns geopandas dataframe containing LineString geometry trajectories.
    
    Parameters:
        train_df (Dataframe): Dataframe of train-1000 csv.
        verbose (bool): Set to True to print out conversion statistics.
    """
    linestr_obj = []
    for idx, coords in enumerate(train_df['POLYLINE']):
        if len(coords) > 0:
            points = []
            for coord in coords:
                points.append(Point(coord))
                
            if len(points) > 1:
                linestr_obj.append(LineString(points))
            elif verbose:
                print(f"Insufficient points to form LineString. Coords only have {len(points)} point.")
        else:
            if verbose:
                print(f"Missing coordinates at row {idx}!")
                print(train_df['POLYLINE'][idx])
                
    if verbose:
        print(f"Total number of LineString: {len(linestr_obj)}")
        
    ls_gdf = gpd.GeoDataFrame([{'geometry': ls} for ls in linestr_obj], crs=crs)
    return ls_gdf

def get_coords(geom):
    return list((y, x) for x, y in geom.coords)

def get_lineString_coords(ls_gdf):
    """
    Converts LineString GeoDataFrame back to Array List x,y coordinates.
    """
    lcoords = ls_gdf.apply(lambda row: get_coords(row.geometry), axis=1)
    return lcoords


def get_mm_results_df(filepath):
    """
    Returns a dataframe containing "mgeom" column from match_result.csv file.
    
    Parameters:
        data_dir (str): Directory containing match_result.csv.
    """
    mm_results = pd.read_csv(filepath, sep = ",", usecols=['mgeom'])        
    return mm_results


def get_geom_gdf(mm_results, verbose=True):
    """
    Returns geopandas dataframe containing LineString geometry trajectories.
    
    Parameters:
        mm_results (Dataframe): Dataframe of match_result csv.
        verbose (bool): Set to True to print out conversion statistics.
    """
    linestr_obj = []
    for idx, ls in enumerate(mm_results['mgeom']):
        try:
            line = shapely.wkt.loads(ls)
            if len(line.coords) == 1 and verbose:
                print(f"Only 1 point at row {idx+1}")
            linestr_obj.append(line)
        except:
            if verbose:
                print(f"Missing coordinates at row {idx+1}! Row data: {ls}")
                
    if verbose:
        print(f"Total number of LineString: {len(linestr_obj)}")
        
    geom_gdf = gpd.GeoDataFrame([{'geometry': ls} for ls in linestr_obj], crs=crs)
    return geom_gdf