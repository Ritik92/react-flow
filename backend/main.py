from fastapi import FastAPI, Form
from typing import Dict, List, Any
import json
from collections import defaultdict

app = FastAPI()
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

def is_dag(nodes: List[Dict[str, Any]], edges: List[Dict[str, Any]]) -> bool:
    """
    Check if the graph is a DAG using a DFS-based cycle detection algorithm.
    """
    adj_list = defaultdict(list)
    for edge in edges:
        adj_list[edge['source']].append(edge['target'])

    visited = set()
    path = set()

    def has_cycle(node: str) -> bool:
        if node in path:
            return True
        if node in visited:
            return False

        visited.add(node)
        path.add(node)

        for neighbor in adj_list[node]:
            if has_cycle(neighbor):
                return True

        path.remove(node)
        return False

    for node in [node['id'] for node in nodes]:
        if node not in visited:
            if has_cycle(node):
                return False

    return True

@app.get('/')
def read_root():
    return {'Ping': 'Pong'}

@app.post('/pipelines/parse')
async def parse_pipeline(pipeline: str = Form(...)):
    """
    Parse the pipeline data and return analysis results.
    """
    try:
        pipeline_data = json.loads(pipeline)
        nodes = pipeline_data['nodes']
        edges = pipeline_data['edges']

        num_nodes = len(nodes)
        num_edges = len(edges)
        is_dag_result = is_dag(nodes, edges)

        return {
            'num_nodes': num_nodes,
            'num_edges': num_edges,
            'is_dag': is_dag_result
        }
    except Exception as e:
        return {
            'error': f'Failed to parse pipeline: {str(e)}'
        }