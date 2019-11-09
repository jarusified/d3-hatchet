# Library imports
from flask import Flask, jsonify, render_template, send_from_directory, current_app, request
from flask_socketio import SocketIO, emit, send
import os
import sys
import json
from flask_cors import CORS
from networkx.readwrite import json_graph

from main import *
from callgraph import CallGraph

app = Flask(__name__, static_url_path='/public')
sockets = SocketIO(app)
CORS(app)

class App():
    def __init__(self):
        self.callflow_path = os.path.abspath(os.path.join(__file__, '../../..'))

        self.callflow = Main()

        # Start server if preprocess is not called.
        self.create_socket_server()
        sockets.run(app, debug=True, use_reloader=True)

    def create_socket_server(self):
        @sockets.on('load_dataset_request', namespace='/')
        def init(request):
            # It is preferred to keep the code logic and request separate to
            # avoid huge files
            dataset_name = request['dataset_name']
            result = self.callflow.update({
                "name": "load_dataset",
                "dataset_name": dataset_name,
            })
            emit('load_dataset', result, json=True)

        @sockets.on('get_graph_request', namespace='/')
        def group(data):
            print('[Request] Get graph: {}'.format(data))
            g = self.callflow.update({
                'name': 'get_graph'
            })
            result = json_graph.tree_data(g, '<program root>')
            emit('get_graph', result, json=True)

if __name__ == '__main__':
    App()
