from collections import deque


def are_parentheses_balanced(text):
    stack = []
    pairs = {")": "(", "]": "[", "}": "{"}
    opening = set(pairs.values())
    for ch in text:
        if ch in opening:
            stack.append(ch)
        elif ch in pairs:
            if not stack or stack[-1] != pairs[ch]:
                return False
            stack.pop()
    return len(stack) == 0


def bfs_levels(graph, start):
    if start not in graph:
        raise KeyError("start node not in graph")
    queue = deque([start])
    distance = {start: 0}
    while queue:
        node = queue.popleft()
        for neighbor in graph[node]:
            if neighbor not in distance:
                distance[neighbor] = distance[node] + 1
                queue.append(neighbor)
    return distance


if __name__ == "__main__":
    g = {"A": ["B", "C"], "B": ["D"], "C": [], "D": []}
    print("balanced:", are_parentheses_balanced("{[()]}"))
    print("levels:", bfs_levels(g, "A"))

