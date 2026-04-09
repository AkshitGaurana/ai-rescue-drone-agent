import numpy as np
from environment import Grid
from algorithms import bfs, dfs, astar

def run_simulation(size=15, obstacle_density=0.2):
    # Setup grid
    grid = Grid(size=size)
    grid.generate_map(obstacle_density=obstacle_density)
    grid.place_victim()
    grid.place_drone()

    start = grid.start
    goal = grid.goal

    # Run all 3 algorithms
    path_bfs, nodes_bfs = bfs(grid.map, start, goal)
    path_dfs, nodes_dfs = dfs(grid.map, start, goal)
    path_astar, nodes_astar = astar(grid.map, start, goal)

    # Mark A* path on grid
    if path_astar:
        for pos in path_astar:
            if pos != goal:
                grid.map[pos[0]][pos[1]] = 3  # mark path

    # Print comparison table
    print("=" * 45)
    print(f"{'Algorithm':<12} {'Path Length':<15} {'Nodes Explored'}")
    print("=" * 45)
    print(f"{'BFS':<12} {len(path_bfs) if path_bfs else 'No path':<15} {nodes_bfs}")
    print(f"{'DFS':<12} {len(path_dfs) if path_dfs else 'No path':<15} {nodes_dfs}")
    print(f"{'A*':<12} {len(path_astar) if path_astar else 'No path':<15} {nodes_astar}")
    print("=" * 45)

    print("\nFinal Grid (A* path marked with *):")
    grid.display()

    # Return results dict for Akshit's Streamlit UI
    return {
        'grid': grid,
        'start': start,
        'goal': goal,
        'paths': {
            'bfs': path_bfs,
            'dfs': path_dfs,
            'astar': path_astar
        },
        'stats': {
            'bfs':   {'path_len': len(path_bfs)   if path_bfs   else 0, 'nodes_explored': nodes_bfs},
            'dfs':   {'path_len': len(path_dfs)   if path_dfs   else 0, 'nodes_explored': nodes_dfs},
            'astar': {'path_len': len(path_astar) if path_astar else 0, 'nodes_explored': nodes_astar}
        }
    }

# Run directly for testing
if __name__ == "__main__":
    run_simulation(size=10, obstacle_density=0.2)