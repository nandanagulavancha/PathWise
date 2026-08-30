from collections import defaultdict, deque


LEVEL_MAP = {"beginner": 1, "intermediate": 2, "advanced": 3}


class SkillGraph:
    """Directed acyclic graph of skills with prerequisite edges.
    Uses Kahn's algorithm for topological ordering and groups
    skills into phases by topological depth."""

    def __init__(self):
        self.adjacency: dict[str, list[str]] = defaultdict(list)  # prereq -> [dependents]
        self.reverse: dict[str, list[str]] = defaultdict(list)    # skill -> [prerequisites]
        self.in_degree: dict[str, int] = defaultdict(int)
        self.skill_info: dict[str, dict] = {}  # skill_id -> {name, category, ...}
        self.all_nodes: set[str] = set()

    def add_skill(self, skill_id: str, name: str, category: str = ""):
        self.skill_info[skill_id] = {"name": name, "category": category}
        self.all_nodes.add(skill_id)
        if skill_id not in self.in_degree:
            self.in_degree[skill_id] = 0

    def add_prerequisite(self, skill_id: str, prerequisite_id: str):
        self.adjacency[prerequisite_id].append(skill_id)
        self.reverse[skill_id].append(prerequisite_id)
        self.in_degree[skill_id] = self.in_degree.get(skill_id, 0) + 1
        self.all_nodes.add(skill_id)
        self.all_nodes.add(prerequisite_id)
        if prerequisite_id not in self.in_degree:
            self.in_degree[prerequisite_id] = 0

    def get_all_prerequisites(self, skill_id: str, visited: set = None) -> set[str]:
        """Recursively collect all transitive prerequisites for a skill."""
        if visited is None:
            visited = set()
        if skill_id in visited:
            return visited
        visited.add(skill_id)
        for prereq in self.reverse.get(skill_id, []):
            self.get_all_prerequisites(prereq, visited)
        return visited

    def get_required_subgraph(self, target_skill_ids: list[str]) -> set[str]:
        """Given target skills, find all skills needed (targets + all prerequisites)."""
        required = set()
        for sid in target_skill_ids:
            required |= self.get_all_prerequisites(sid)
        return required

    def topological_sort_with_depths(self, node_subset: set[str] = None) -> list[tuple[int, str]]:
        """Kahn's algorithm returning (depth, skill_id) pairs.
        Depth 0 = no prerequisites (foundational). Higher depth = more advanced."""
        nodes = node_subset if node_subset else self.all_nodes

        # Compute in-degrees for the subgraph
        local_in = {}
        local_adj = defaultdict(list)
        for n in nodes:
            local_in[n] = 0
        for n in nodes:
            for dep in self.adjacency.get(n, []):
                if dep in nodes:
                    local_adj[n].append(dep)
                    local_in[dep] = local_in.get(dep, 0) + 1

        # BFS with depth tracking
        queue = deque()
        for n in nodes:
            if local_in.get(n, 0) == 0:
                queue.append((0, n))

        result = []
        visited = set()
        while queue:
            depth, node = queue.popleft()
            if node in visited:
                continue
            visited.add(node)
            result.append((depth, node))
            for dep in local_adj.get(node, []):
                local_in[dep] -= 1
                if local_in[dep] == 0:
                    queue.append((depth + 1, dep))

        # Any unvisited nodes (cycles or isolated) get appended at max depth
        max_depth = max((d for d, _ in result), default=0) + 1
        for n in nodes:
            if n not in visited:
                result.append((max_depth, n))

        return result

    def build_phases(
        self,
        target_skill_ids: list[str],
        mastered_skill_ids: set[str] = None,
        gap_weights: dict[str, float] = None,
    ) -> list[list[dict]]:
        """Build ordered learning phases from target skills.

        Returns a list of phases, where each phase is a list of
        {"skill_id", "name", "category", "depth", "gap_weight"} dicts.

        Skills the user has mastered are excluded.
        Within the same depth, skills are sorted by gap_weight (critical first).
        """
        if mastered_skill_ids is None:
            mastered_skill_ids = set()
        if gap_weights is None:
            gap_weights = {}

        # Get all required skills (targets + prerequisites)
        required = self.get_required_subgraph(target_skill_ids)

        # Remove mastered skills
        to_learn = required - mastered_skill_ids

        if not to_learn:
            return []

        # Topological sort
        sorted_skills = self.topological_sort_with_depths(to_learn)

        # Group by depth
        depth_groups: dict[int, list] = defaultdict(list)
        for depth, skill_id in sorted_skills:
            info = self.skill_info.get(skill_id, {"name": skill_id, "category": ""})
            depth_groups[depth].append({
                "skill_id": skill_id,
                "name": info.get("name", skill_id),
                "category": info.get("category", ""),
                "depth": depth,
                "gap_weight": gap_weights.get(skill_id, 0.5),
            })

        # Sort within each depth by gap_weight (higher = more critical = earlier)
        phases = []
        for depth in sorted(depth_groups.keys()):
            group = depth_groups[depth]
            group.sort(key=lambda s: -s["gap_weight"])
            # If a depth has many skills, split into sub-phases of 2-3 skills max
            for i in range(0, len(group), 3):
                phases.append(group[i:i + 3])

        return phases

    @staticmethod
    def from_db(db) -> "SkillGraph":
        """Load a complete skill graph from the database."""
        graph = SkillGraph()

        # Load all skills
        skills = db.client.table("skills").select("id, name, category").execute()
        for s in (skills.data or []):
            graph.add_skill(s["id"], s["name"], s.get("category", ""))

        # Load all prerequisite edges
        prereqs = db.client.table("skill_prerequisites").select("skill_id, prerequisite_skill_id").execute()
        for p in (prereqs.data or []):
            graph.add_prerequisite(p["skill_id"], p["prerequisite_skill_id"])

        return graph
