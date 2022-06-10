
# Documentation

## Required Software

* ### Postgresql 
* ### Postgis
* ### Pgrouting 
* ### osm2pgrouting
* ### osmconvert

## Problem Description

I will be creating a mobile application where given 4 long/lat coordinates, it creates a path going through all drivable roads within the rectangle created by the coordinates. The path I am looking to generate does not actually need to be an Euler path (backtracking and overlapping are allowed); it must simply cover all reachable roads. The application would then choose a starting point within the edge of the square, and guide a driver through the generated path with directions (like Google/Apple maps). This problem is known as the Chinese Postman problem.

An algorithm within the pgrouting extension can solve this problem for me. My work will be: <br>
* Acquiring road data
* Cleaning the data
* Generating a path
* Creating an app (or using an app) to give directions of the path to a mobile user

## Acquiring Data -- OpenStreetMaps


