export const demoTopics = [
  { name: "Graph algorithms", subject: "Data structures & algorithms", mastery: 46, tone: "from-violet-400 to-fuchsia-400", icon: "◈" },
  { name: "Recursion & backtracking", subject: "Data structures & algorithms", mastery: 58, tone: "from-sky-400 to-indigo-400", icon: "⤴" },
  { name: "Dynamic programming", subject: "Data structures & algorithms", mastery: 61, tone: "from-amber-300 to-pink-400", icon: "⌘" },
  { name: "Trees & traversals", subject: "Data structures & algorithms", mastery: 78, tone: "from-emerald-300 to-sky-400", icon: "⑂" },
];

export const demoPacks = [
  { name: "Graph Theory · the essentials", subject: "Data structures & algorithms", chapters: 8, cards: 24, updated: "2 hours ago", progress: 68, color: "violet", icon: "⌘" },
  { name: "Operating Systems · memory", subject: "Computer science", chapters: 5, cards: 18, updated: "Yesterday", progress: 34, color: "blue", icon: "▦" },
  { name: "Database Systems · SQL & design", subject: "Computer science", chapters: 6, cards: 32, updated: "Sep 29", progress: 82, color: "pink", icon: "◫" },
];

export const demoMistakes = [
  { concept: "Dijkstra's algorithm", subject: "Graph algorithms", reason: "Used it with negative edge weights", date: "Today", status: "Due now", color: "rose" },
  { concept: "Recursive call stack", subject: "Recursion", reason: "Forgot the base case on empty input", date: "Yesterday", status: "Due now", color: "amber" },
  { concept: "Tabulation order", subject: "Dynamic programming", reason: "Filled states before dependencies", date: "Sep 30", status: "Tomorrow", color: "blue" },
];

export const quizQuestion = {
  prompt: "Which shortest-path algorithm stays correct when some edges have negative weights?",
  choices: ["Dijkstra's algorithm", "Bellman–Ford algorithm", "Prim's algorithm", "Breadth-first search"],
  answer: 1,
  explain: "Bellman–Ford relaxes every edge repeatedly, so it handles negative weights and can detect a negative cycle. Dijkstra assumes non-negative edges.",
};

export const demoQuizQuestions = [
  { id: "graph-negative-weights", type: "Multiple choice", topic: "Shortest paths", prompt: "Which shortest-path algorithm stays correct when some edges have negative weights?", choices: ["Dijkstra's algorithm", "Bellman–Ford algorithm", "Prim's algorithm", "Breadth-first search"], answer: 1, explain: "Bellman–Ford relaxes every edge repeatedly, so it handles negative weights and can detect a negative cycle." },
  { id: "graph-bfs-shortest", type: "True or false", topic: "Graph traversal", prompt: "In an unweighted graph, BFS finds a path with the fewest edges.", choices: ["True", "False"], answer: 0, explain: "BFS explores one distance layer at a time, so the first discovered path uses the fewest edges." },
  { id: "graph-dfs-visited", type: "Fill in the blank", topic: "Depth-first search", prompt: "To prevent DFS from repeatedly visiting nodes in a cycle, keep a ___ set.", choices: ["visited", "sorted", "weighted", "priority"], answer: 0, explain: "A visited set records nodes already explored and prevents cycles from causing repeated work." },
  { id: "graph-bfs-complexity", type: "Concept check", topic: "Complexity", prompt: "A graph has V vertices and E edges. With an adjacency list, BFS runs in what time?", choices: ["O(V + E)", "O(V × E)", "O(V² × E)", "O(log V)"], answer: 0, explain: "BFS visits each vertex and inspects each edge at most once, giving O(V + E)." },
];
