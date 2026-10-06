"""Believable demo data used by local previews and the college presentation."""

DASHBOARD = {
    "student": {"name": "Arjun Sharma", "program": "Computer science · Year 2", "level": 14, "xp": 2840, "streak": 17},
    "exam": {"name": "Data structures & algorithms", "days_remaining": 12},
    "mastery": {"overall": 74, "weekly_change": 6},
    "today": {"xp": 840, "focus_minutes": 108, "mission": "Graph algorithms", "mission_mastery": 46, "mission_minutes": 42, "mission_xp": 320},
    "topics": [
        {"name": "Graph algorithms", "mastery": 46, "status": "focus"},
        {"name": "Recursion & backtracking", "mastery": 58, "status": "review"},
        {"name": "Dynamic programming", "mastery": 61, "status": "review"},
        {"name": "Trees & traversals", "mastery": 78, "status": "strong"},
    ],
    "study_packs": [
        {"id": "pack-graphs", "name": "Graph Theory · the essentials", "subject": "Data structures & algorithms", "chapters": 8, "cards": 24, "progress": 68},
        {"id": "pack-os", "name": "Operating Systems · memory", "subject": "Computer science", "chapters": 5, "cards": 18, "progress": 34},
        {"id": "pack-db", "name": "Database Systems · SQL & design", "subject": "Computer science", "chapters": 6, "cards": 32, "progress": 82},
    ],
    "mistake_count": 3,
}

SOURCE_CHUNKS = [
    {"id": "chunk-graph-12", "material_id": "pack-graphs", "title": "Graph Theory · the essentials", "page": 12, "text": "Depth-first search is naturally expressed recursively. Each call explores an unvisited neighbor, and the base condition is reached when every reachable neighbor has already been visited. Keep a visited set to avoid cycles."},
    {"id": "chunk-graph-08", "material_id": "pack-graphs", "title": "Graph Theory · the essentials", "page": 8, "text": "Breadth-first search explores vertices level by level using a queue. On an unweighted graph it finds a shortest path by number of edges. Mark each vertex as discovered when it enters the queue."},
    {"id": "chunk-graph-19", "material_id": "pack-graphs", "title": "Graph Theory · the essentials", "page": 19, "text": "Dijkstra's algorithm requires non-negative edge weights. Bellman–Ford relaxes all edges repeatedly and can detect a negative weight cycle."},
]

DEMO_QUESTIONS = [
    {
        "id": "graph-negative-weights", "topic": "Shortest paths", "type": "Multiple choice",
        "prompt": "Which shortest-path algorithm stays correct when some edges have negative weights?",
        "choices": ["Dijkstra's algorithm", "Bellman–Ford algorithm", "Prim's algorithm", "Breadth-first search"],
        "answer_index": 1,
        "explanation": "Bellman–Ford relaxes every edge repeatedly, so it handles negative weights and detects a negative cycle. Dijkstra assumes non-negative edges.",
    },
    {
        "id": "graph-bfs-shortest", "topic": "Graph traversal", "type": "True or false",
        "prompt": "In an unweighted graph, BFS finds a path with the fewest edges.",
        "choices": ["True", "False"], "answer_index": 0,
        "explanation": "BFS explores one distance layer at a time, so the first discovered path uses the fewest edges.",
    },
    {
        "id": "graph-dfs-visited", "topic": "Depth-first search", "type": "Fill in the blank",
        "prompt": "To prevent DFS from repeatedly visiting nodes in a cycle, keep a ___ set.",
        "choices": ["visited", "sorted", "weighted", "priority"], "answer_index": 0,
        "explanation": "A visited set records nodes already explored and prevents cycles from causing repeated work.",
    },
    {
        "id": "graph-bfs-complexity", "topic": "Complexity", "type": "Concept check",
        "prompt": "A graph has V vertices and E edges. With an adjacency list, BFS runs in what time?",
        "choices": ["O(V + E)", "O(V × E)", "O(V² × E)", "O(log V)"], "answer_index": 0,
        "explanation": "BFS visits each vertex and inspects each edge at most once, giving O(V + E).",
    },
]

DEMO_QUESTION = DEMO_QUESTIONS[0]
