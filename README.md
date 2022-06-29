# Documentation

## Required Software

- ### Postgresql
- ### Postgis (extension for postgres to handle geographical data)
- ### Pgrouting (routing algorithms extension)
- ### osm2pgrouting (administers data from OpenStreetMap to postgres)
- ### osmium-tool (cleans data by removing uneccessary tags)

## Problem Description

I will be creating a mobile application where given 4 long/lat coordinates, it creates a path going through all drivable roads within the rectangle created by the coordinates. The path I am looking to generate does not actually need to be an Euler path (backtracking and overlapping are allowed); it must simply cover all reachable roads. The application would then choose a starting point within the edge of the square, and guide a driver through the generated path with directions (like Google/Apple maps).

This problem is known as the Chinese Postman problem, and there are several variations. In my case it is the Mixed (bidirectional edges and directional arcs) Open (does not need to end at source vertex) Rural (aka selecting, this means not ALL edges need to be traversed, since I will only want to traverse edges that have single family residences, but this optimization is not necessary initially) ChPP. The solution also doesn't have to be optimal which is known as the incremental ChPP. Computationally, the undirected and directed cases are polynomial, whereas the mixed is NP-hard! Referenced paper: http://www.harold.thimbleby.net/cv/files/cpp.pdf

No implementations of the mixed chinese postman instilled confidence in me. For instance, pgrouting has an expiremental Chinese Postman Tour function that has limited documentation and has not been edited since 2018. I want to create my own because I will need specific functionality for my program such as implementing a Rural version of the algorithm that only prioritizes streets with SFHs and older houses constructed before a certain date (we want older SFHs i.e. before 1990). I need an intimate understanding of the algorithm for debugging purposes.

CPT Chinese Postman Tour
An algorithm within the pgrouting extension can solve this problem for me. My work will be: <br>

- Acquiring road data
- Cleaning the data
- Generating a path
- Creating an app (or using an app) to give directions of the path to a mobile user (QGIS?)

## Acquiring Data -- OpenStreetMaps

osmfilter used to remove unecessary tags with the following command:
_osmfilter export.osm --verbose --keep-tags="all highway= name= service= oneway=" --drop-author -o=filtered_export.osm_

## QGIS

To load OSM data go to vector tab, then QuickOSM

# Procedure

CURRENT SEQ OF OPERATIONS -- NEEDS TO BE AUTOMATED/OPTIMIZED

## Retrieving/Loading Data

- Download OSM data from QGIS using button in middle left tab _"Select OSM data by rectangle selection"_
- Filter the data to get just the roads using osmfilter with following command: **osmfilter qgis_export.osm --keep="highway=motorway =trunk =primary =secondary =tertiary =tertiary_link =living_street =residential =unclassified highway=\*link service=alley" --drop="motor_vehicle=no" --drop-author --drop-version -o=qgis_streets.osm**
- Load the data into Postgres with necessary formatting for pgrouting using osm2pgrouting: **osm2pgrouting --f qgis_streets.osm --conf /opt/homebrew/Cellar/osm2pgrouting/2.3.8_2/share/osm2pgrouting/mapconfig.xml --dbname postgres --username colet --clean**
- Change the oneway column such that strings "UNKNOWN" or "NO" become null with:
  > UPDATE ways  
  > SET oneway=
  > CASE  
  > WHEN ways.oneway='UNKNOWN' OR ways.oneway='NO' THEN NULL
  > ELSE oneway END;

## Diagnosing Route Errors with pgr_analyze functions

### pgr_analyzeGraph

- To use this function, you need to first change the column name from "gid" to "id". Do this with the following SQL: ALTER TABLE ways RENAME COLUMN gid TO id;
- pgr_analyzeGraph('ways', 0.0001) first param table name, second is percision for calculations (I think)
- Sample output:

  > NOTICE: PROCESSING:
  > NOTICE: pgr_analyzeGraph('ways',1e-05,'the_geom','id','source','target','true')
  > NOTICE: Performing checks, please wait ...
  > NOTICE: Analyzing for dead ends. Please wait...
  > NOTICE: Analyzing for gaps. Please wait...
  > NOTICE: Analyzing for isolated edges. Please wait...
  > NOTICE: Analyzing for ring geometries. Please wait...
  > NOTICE: Analyzing for intersections. Please wait...
  > NOTICE: ANALYSIS RESULTS FOR SELECTED EDGES:
  > NOTICE: Isolated segments: 0
  > NOTICE: Dead ends: 24
  > NOTICE: Potential gaps found near dead ends: 0
  > NOTICE: Intersections detected: 1
  > NOTICE: Ring geometries: 0

- Isolated segments will let you know if there are any ways that aren't connected to the graph (for instance onetime there was a dangling road that didn't connect to anything)
- Dead ends would be one ways where you can't backtrack and would then be stuck at the end of the road. These are identified by cnt=1 in ways_vertices_pgr ( SELECT \* FROM ways_vertices_pgr WHERE cnt = 1; )
- Potential gaps are identified with chk=1 in ways_vertices_pgr

### pgr_analyzeOneway

- Query

  > SELECT pgr_analyzeOneway('ways',
  > ARRAY['', 'B', 'YES'],
  > ARRAY['', 'B', 'FT'],
  > ARRAY['', 'B', 'FT'],
  > ARRAY['', 'B', 'YES']);

- Result

  > NOTICE: PROCESSING:
  > NOTICE: pgr_analyzeOneway('ways','{"",B,TF}','{"",B,FT}','{"",B,FT}','{"",B,TF}','oneway','source','target',t)
  > NOTICE: Analyzing graph for one way street errors.
  > NOTICE: Analysis 25% complete ...
  > NOTICE: Analysis 50% complete ...
  > NOTICE: Analysis 75% complete ...
  > NOTICE: Analysis 100% complete ...
  > NOTICE: Found 33 potential problems in directionality

- Use SELECT \* FROM ways_vertices_pgr WHERE ein=0 OR eout=0; to find problem nodes
- Execute the following to get the edges using these nodes:
  > SELECT gid FROM ways a, ways_vertices_pgr b WHERE a.source=b.id AND (ein=0 OR eout=0)
  > UNION  
  > SELECT gid FROM ways a, ways_vertices_pgr b WHERE a.target=b.id AND (ein=0 OR eout=0);
