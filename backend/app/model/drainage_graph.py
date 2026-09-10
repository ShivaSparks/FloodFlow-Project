from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path

import networkx as nx


@dataclass(frozen=True)
class DrainageEdgeState:
    edge_id: str
    inflow_cumecs: float
    storage_fraction: float
    utilization: float
    surcharge: bool


class DrainageGraph:
    def __init__(self, graph: nx.DiGraph, state: dict[str, float] | None = None):
        self.graph = graph
        self.state = state or {
            data["edge_id"]: 0.0 for _, _, data in graph.edges(data=True)
        }
        self.edge_by_id = {
            data["edge_id"]: (source, target)
            for source, target, data in graph.edges(data=True)
        }

    @classmethod
    def from_csv(cls, nodes_path: Path, edges_path: Path) -> DrainageGraph:
        graph = nx.DiGraph()
        with nodes_path.open("r", encoding="utf-8-sig", newline="") as handle:
            for row in csv.DictReader(handle):
                if row.get("node_id", "").strip().startswith("N"):
                    graph.add_node(row["node_id"].strip(), **row)
        with edges_path.open("r", encoding="utf-8-sig", newline="") as handle:
            for row in csv.DictReader(handle):
                edge_id = row.get("edge_id", "").strip()
                if not edge_id.startswith("E"):
                    continue
                if row["from_node"] not in graph or row["to_node"] not in graph:
                    raise ValueError(f"Unknown drainage node in {edge_id}")
                attributes = dict(row)
                attributes["edge_id"] = edge_id
                attributes["capacity_cumecs"] = float(row["design_capacity_cumecs"])
                graph.add_edge(row["from_node"], row["to_node"], **attributes)
        if not nx.is_directed_acyclic_graph(graph):
            raise ValueError("Prototype drainage graph must be acyclic")
        return cls(graph)

    def update(
        self, local_inflow_by_node: dict[str, float], dt_seconds: float = 900.0
    ) -> list[DrainageEdgeState]:
        if dt_seconds <= 0:
            raise ValueError("dt_seconds must be positive")
        node_flow = {
            node: max(0.0, float(local_inflow_by_node.get(node, 0.0)))
            for node in self.graph.nodes
        }
        states: list[DrainageEdgeState] = []
        for node in nx.topological_sort(self.graph):
            incoming = node_flow[node]
            outgoing = list(self.graph.out_edges(node, data=True))
            if not outgoing:
                continue
            per_edge = incoming / len(outgoing)
            for source, target, data in outgoing:
                edge_id = data["edge_id"]
                capacity = max(float(data["capacity_cumecs"]), 0.001)
                utilization = per_edge / capacity
                prior = self.state.get(edge_id, 0.0)
                # A small reservoir approximation keeps memory of prior rainfall.
                storage = max(0.0, min(1.5, prior * 0.75 + utilization * 0.5))
                self.state[edge_id] = storage
                node_flow[target] = node_flow.get(target, 0.0) + per_edge
                states.append(
                    DrainageEdgeState(
                        edge_id, per_edge, storage, utilization, storage > 1.0
                    )
                )
        return states
