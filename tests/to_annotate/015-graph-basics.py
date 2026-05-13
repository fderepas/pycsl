from collections import deque


def shortest_path_unweighted(graph, start, goal):
    if start not in graph or goal not in graph:
        raise KeyError("start and goal must be graph nodes")
    queue = deque([start])
    parent = {start: None}
    while queue:
        node = queue.popleft()
        if node == goal:
            break
        for neighbor in graph[node]:
            if neighbor not in parent:
                parent[neighbor] = node
                queue.append(neighbor)
    if goal not in parent:
        return None
    path = []
    current = goal
    while current is not None:
        path.append(current)
        current = parent[current]
    path.reverse()
    return path


if __name__ == "__main__":
    g = {"A": ["B", "C"], "B": ["D"], "C": ["D", "E"], "D": ["F"], "E": [], "F": []}
    print("path:", shortest_path_unweighted(g, "A", "F"))

