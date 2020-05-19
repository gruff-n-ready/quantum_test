"""
Script for finding satellite imagery overlap with .geojson file
Test project

Should work like this:
>python sentinel2overlap.py -i kharkiv_region.geojson -o overlap.geojson
>Found tiles: 36UXA,36UXV,36UXU,36UYU,36UYV,37UCQ,37UDQ,37UDR,37UCR,36UYA,36UYB
"""
import argparse
import geopandas as gpd
import pandas as pd
import numpy as np

def read_filepaths():
    """Reads the filenames for input/output from console"""
    input_file = ''
    output_file = ''
    parser = argparse.ArgumentParser()                                                          # Initialize parser 
    parser.add_argument("input", help="dataset to compare")
    parser.add_argument("-o", "--output", default="overlap.geojson", help="output file name")   # Adding optional argument
    # Read arguments from command line
    args = parser.parse_args()
    if args.input:
        input_file=args.input                                                                   # Get input file name
    if args.output:
        output_file=args.output                                                                 # Get output file name, optional, defaults to "overlap.geojson"

    return (input_file, output_file)

def make_overlap_map(gdf):
    """Creates a poly with tile overlaps"""
    tile_overlaps_list=[]                                                                       # Create a list for Sentinel tile overlaps
    tile_indices_checked = []                                                                   # Create a list of tile indices for which intersections were already done
    for index, row in gdf.iterrows():
        tile_indices_checked.append(index)
        # print(type(sentinel.loc[:, 'geometry']))
        to_check = np.setdiff1d(gdf.index, tile_indices_checked)                                # Sentinel tile indices sans the checked tile indices
        if len(to_check)>0:
            gdf_temp=gdf.iloc[to_check]
            current_overlap = gdf_temp.loc[:, 'geometry'].intersection(row.geometry)                  
            tile_overlaps_list.append(current_overlap[~current_overlap.is_empty])               # Drop empty geometries cluttering the list
    overlaps = gpd.GeoSeries([pd.concat(tile_overlaps_list, ignore_index=True).unary_union], crs='EPSG:4326') # Make a GeoSeries with a polygon of all overlaps
    return overlaps

def drop_redundant(tiles, shape, overlap_map):
    """Returns a list of tile names that still qualify"""
    output = []
    if any(shape.within(overlap_map)):                                                           # Condition 3: Check if the input shape is completely within the overlap zone
        overlapping = tiles.loc[shape.within(tiles)]                                             #Returns first(least ID) tile that contains input shape
        output = overlapping.loc[:,'Name']                                                       #Save tile name into list
        return output
    else:
        for index in tiles.index:
            coverage = shape.intersection(tiles.at[index,'geometry'])
            coverage_cartesian=coverage.to_crs("EPSG:3857")                                       # Set a copy of overlap to Cartesian system
            if(coverage_cartesian.area[0]<= 1000.0):                                              # Get overlap area in m2, compare
                continue                                                                          # Condition 1 : Tile coverage must me more than 1000 m2
            if any(coverage.within(overlap_map)):                                                 # Drop tile if they only cover the overlap
                continue                                                                          # Condition 2 : Discard tiles that only cover within overlap
            else:
                output.append(tiles.at[index, 'Name'])                             
    return output

def print_tile_list(tile_list):
    """Prints out the list"""
    print("Found tiles: ")
    for entry in tile_list:
        print(entry, end=' ')

if __name__ == "__main__":
    # Filepaths
    input_fp, output_fp = read_filepaths()                                                    
    sentinel_fp = "sentinel2_tiles.geojson"

    # Begin work
    input_shape = gpd.read_file(input_fp)                                             # Read the input file
    sentinel = gpd.read_file(sentinel_fp, bbox=list(input_shape.bounds.values[0]) )   # Get only the tiles that overlap the bounding box  
    output_list = drop_redundant(sentinel, input_shape, make_overlap_map(sentinel))   # Discard the redundant tiles
    print_tile_list(output_list)

    # Select tiles in sentinel where 'Name' is in output_list, write the results into a .geojson file
    sentinel[sentinel['Name'].isin(output_list)].to_file(output_fp, driver='GeoJSON')                
