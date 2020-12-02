# AI6128 Urban Computing

Project Title: Trajectory and Road Network Data Analysis

Members:

+ Ong Jia Hui (Karyl)
+ Zhu Zhi Cheng (Jackson)
+ Tan Meng Xuan

## Tasks:

+ Task 1: Data Preparation
  + Download a road network of the Porto City, Portugal and download some trajectory data of taxies in the city from a Kaggle competition.
+ Task 2: GPS Point Visualization
  + Visualize the raw GPS points of the first 10 trips in the trajectory data dataset on a map with the road network of Porto (together with different colors or separately).
+ Task 3: Map Matching
  + Perform the map matching task to map the trajectory data to the road network using an existing open-source tool. Each trajectory will be mapped to a sequence of road segments and we call a sequence of road segments a route.
+ Task 4: Route Visualization
  + Visualize the routes that are mapped from the trajectories of the first 10 trips on the road network (together with different colors or separately).
+ Task 5: Route Analysis
  + Perform some analysis on the mapped routes. This includes (1) to return 5 road segments that are traversed the most often as indicated by the trajectory data; (2) to return 5 road segments, whose average travelling time as indicated by the trajectory data are the largest (those road segments that are traversed by no trajectories can be ignored); and (3) and visualize the road segments returned in (1) and (2) on the road network separately.
+ Task 6 (bonus and optional): Case studies
  + If possible, identify those cases where the map matching algorithm do not work well, think of some solutions for the identified cases and implement the new ideas into the open source tools and perform the map matching task on the trajectory data again and compare the mapped routes before and after the changes are made.

## How to Setup Environment

1. Install [Anaconda](https://docs.anaconda.com/anaconda/install/) environment.

2. Run the following command to install the necessary libraries using the provided YAML file in env folder:

   ```
   conda env create --file env\ox.yml		
   ```

3. Start up jupyter-lab to run the IPython notebooks!

Note that for Task 3 codes, please follow installation guide from [FMM](https://fmm-wiki.github.io/docs/installation/).

## References

+ [Fast Map Matching](https://github.com/cyang-kth/fmm): Map Matching Algorithm by Can Yang and Gyozo Gidofalvi
+ [Folium](https://github.com/python-visualization/folium): Used to plot plots on maps.
+ [OSMNX](https://github.com/gboeing/osmnx): Visualization tool
