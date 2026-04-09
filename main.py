import numpy as np

def run_simulation(size, density):
    grid = np.random.choice([0, 1], p=[1-density, density], size=(size, size))
    start = (0, 0)
    goal = (size-1, size-1)
    
    grid[start] = 0
    grid[goal] = 0
    
    # Generate a simple mock path for visual purposes
    path = [(0, 0)]
    for _ in range(size * 2):
        curr = path[-1]
        if curr == goal:
            break
        # Move right or down
        next_steps = []
        if curr[0] + 1 < size:
            next_steps.append((curr[0] + 1, curr[1]))
        if curr[1] + 1 < size:
            next_steps.append((curr[0], curr[1] + 1))
        
        if next_steps:
            path.append(next_steps[np.random.randint(len(next_steps))])
            
    if path[-1] != goal:
        path.append(goal)
        
    paths = {
        "BFS": path,
        "DFS": path,
        "A*": path
    }
    
    stats = {
        "BFS": {"path_len": len(path), "nodes": len(path) * 4},
        "DFS": {"path_len": len(path), "nodes": len(path) * 6},
        "A*": {"path_len": len(path), "nodes": len(path) * 2}
    }
    
    return {
        "grid": grid,
        "start": start,
        "goal": goal,
        "paths": paths,
        "stats": stats
    }
