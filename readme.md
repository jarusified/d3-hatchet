# D3-Hatchet

Sample code to retrieve data from [Hatchet](https://github.com/llnl/hatchet). The code reads a hpctoolkit database using Hatchet and the callgraph module converts the hatchet graph to a networkX graph (along with some preprocessing to remove cycles to form a tree structure)

## To run the server:

''' 
    python3 server.py
'''

Then open index.html. 