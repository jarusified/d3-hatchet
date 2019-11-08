##############################################################################
# Copyright (c) 2018-2019, Lawrence Livermore National Security, LLC.
# Produced at the Lawrence Livermore National Laboratory.
#
# This file is part of Callflow.
# Created by Suraj Kesavan <kesavan1@llnl.gov>.
# LLNL-CODE-741008. All rights reserved.
#
# For details, see: https://github.com/LLNL/Callflow
# Please also read the LICENSE file for the MIT License notice.
##############################################################################

import hatchet as ht

import time
import networkx as nx
import pandas as pd
import json
import os

from networkx.drawing.nx_agraph import write_dot
from networkx.readwrite import json_graph

from callgraph import CallGraph


class Main:
    def __init__(self):
        self.gf = None
        pass
        
    def update(self, action):
        action_name = action['name']
        print("Executing the action: {}".format(action_name))

        if action_name == 'load_dataset':
            dataset_name = action['dataset_name']
            dirname = "data/" + dataset_name
            self.gf = ht.GraphFrame.from_hpctoolkit(dirname)
            return True

        elif action_name == "get_graph":
            nx = CallGraph(self.gf)
            return nx.g
        
