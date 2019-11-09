
import networkx as nx
import math
import json
from ast import literal_eval as make_tuple
from networkx.readwrite import json_graph

class CallGraph(nx.Graph):
    def __init__(self, gf):
        super(CallGraph, self).__init__()
        self.gf = gf
        self.graph = self.gf.graph
        self.df = self.gf.dataframe
        self.g = nx.Graph()
        self.g = self.path_to_graph()
        
        # self.add_paths('path')
        # self.add_node_attributes()
        # self.add_edge_attributes()

    def no_cycle_path(self, path):
        ret = []
        mapper = {}
        for idx, elem in enumerate(path):
            if elem not in mapper:
                mapper[elem] = 1
                ret.append(elem)
            else:
                ret.append(elem + "/" + str(mapper[elem]))
                mapper[elem] += 1
        return tuple(ret)

    
    def path_to_graph(self):
        ret = []
        stack = []
        for root in self.graph.roots:
            stack.append(root)
        while len(stack) != 0:
            node = stack.pop()
            for child in node.children:
                # Some weird frame has no name, so ommitting it.
                if 'name' in child.frame.attrs.keys():
                    # self.g.add_edge(node.frame, child.frame)
                    self.g.add_edge(node.frame.attrs['name'], child.frame.attrs['name'])
                # If statements do not have a "name".
                else:
                    # self.g.add_edge(node.frame, child.frame)
                    self.g.add_edge(node.frame.attrs['name'], child.frame.attrs['file'])
                stack.append(child)
        # print(self.g.number_of_nodes(), self.g.number_of_edges())
        cycle_free_graph = self.generic_cycle_break(self.g)
        return cycle_free_graph

    def generic_cycle_break(self, graph):
        # print(nx.find_cycle(graph, orientation="original"))
        ret = nx.DiGraph()
        connected_components = nx.connected_component_subgraphs(graph, copy=False)
        
        for component in connected_components:
            T = nx.minimum_spanning_tree(component)
            ret.add_edges_from(T.edges())
            ret.add_nodes_from(T.nodes())
        
        return ret


    # This is just one way to load edges into networkX graph. Alternatively, one
    # can do a dfs or bfs on the graph to get the edges.
    def add_paths(self, path_name):
        print(self.df.columns)
        for idx, row in self.df.iterrows():
                path = row[path_name]
                # If it becomes a string 
                if isinstance(path, str):
                    path = make_tuple(path)
 
                corrected_path = self.no_cycle_path(path)
                if(len(corrected_path) >= 2):   
                    source = corrected_path[-2]
                    target = corrected_path[-1]

                    if not self.g.has_edge(source, target):
                        self.g.add_edge(source, target)

    def add_node_attributes(self):        
        time_inc_mapping = self.generic_map(self.g.nodes(), 'time (inc)')
        nx.set_node_attributes(self.g, name='time (inc)', values=time_inc_mapping)

        time_mapping = self.generic_map(self.g.nodes(), 'time')
        nx.set_node_attributes(self.g, name="time", values=time_mapping)

        name_mapping = self.generic_map(self.g.nodes(), 'vis_node_name')
        nx.set_node_attributes(self.g, name='name', values=name_mapping)

        nid_mapping = self.generic_map(self.g.nodes(), 'nid')
        nx.set_node_attributes(self.g, name='nid', values=nid_mapping)

    def generic_map(self, nodes, attr):
        ret = {}
        for node in nodes:
            if attr == 'time (inc)':
                group_df = self.df.groupby([groupby]).max()
                # log.info("Group df by {0} = \n {1}".format(groupby, group_df))
                ret[node] = group_df.loc[corrected_node, 'time (inc)']
            
            elif attr == 'time':
                module_df = self.df.loc[self.df['module'] == corrected_node]
                if self.group_by == 'module':
                    group_df = self.df.groupby([groupby]).max()
                elif self.group_by == 'name':
                    group_df = self.df.groupby([groupby]).mean()
                ret[node] = group_df.loc[corrected_node, 'time']
                    
            elif attr == 'nid':
                ret[node] = self.df.loc[self.df['name'] == corrected_function]['nid'].tolist()
                
            else:
                group_df = self.df.groupby(['name']).mean()
                ret[node] = group_df.loc[corrected_node, attr]
        return ret

    def tailhead(self, edge):
        return edge[0], edge[1]

    def tailheadDir(self, edge):
        return str(edge[0]), str(edge[1]), self.edge_direction[edge]
                                
    def add_edge_attributes(self):
        capacity_mapping = self.calculate_flows(self.g)
        nx.set_edge_attributes(self.g, name='weight', values=capacity_mapping)

    # Calculate the sankey flows from source node to target node.        
    def calculate_flows(self, graph):
        ret = {}
        edges = graph.edges(data=True)
        additional_flow = {}
                        
        for edge in edges:
            added_flow = 0
        
            # source edge 
            if '/' in edge[0]:
                source_module = edge[0].split('/')[0]
                source_function = edge[0].split('/')[1]
                source_df = self.df.loc[(self.df['name'] == source_function)]
            elif '=' in edge[0]:
                source_module = edge[0].split('=')[0]
                source_function = edge[0].split('=')[1]
                source_df = self.df.loc[(self.df['module'] == source_module)]

            source_inc = source_df['time (inc)'].mean()
            
            # For target edge
            if '/' in edge[1]:
                target_module = edge[1].split('/')[0]
                target_function = edge[1].split('/')[1]
                target_df = self.df.loc[(self.df['name'] == target_function)]
            elif '=' in edge[1]:
                target_module = edge[1].split('=')[0]
                target_function = edge[1].split('=')[1]
                target_df = self.df.loc[(self.df['module'] == target_module)]

            target_inc = target_df['time (inc)'].mean()
                                 
            if source_inc == target_inc:
                ret[(edge[0], edge[1])] = source_inc
            else:
                ret[(edge[0], edge[1])] = target_inc

            if math.isnan(ret[(edge[0], edge[1])]):
                ret[(edge[0], edge[1])] = 0
        return ret