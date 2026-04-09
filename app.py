import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
import pandas as pd
from main import run_simulation
import time

# 1. PAGE CONFIGURATION
st.set_page_config(page_title="Disaster Rescue Simulation Map", layout="wide", page_icon="🚁")

# 2. SESSION STATE MANAGEMENT
def initialize_session_state():
    if 'sim_data' not in st.session_state:
        st.session_state.sim_data = None
    if 'extra_victims' not in st.session_state:
        st.session_state.extra_victims = []
    if 'animate' not in st.session_state:
        st.session_state.animate = False

# 3. HELPER FUNCTIONS
def get_scenario_defaults(scenario):
    """Adjusts density based on the selected disaster scenario."""
    if scenario == "Urban Rescue":
        return 0.35
    elif scenario == "Earthquake Area":
        return 0.25
    elif scenario == "Flood Zone":
        return 0.15
    return 0.25

def generate_extra_victims(grid, start, goal, num_extra=2):
    """Generates dummy victims to demonstrate a multi-victim scenario visually."""
    free_cells = np.argwhere(grid == 0)
    # Filter out start and goal
    free_cells = [tuple(c) for c in free_cells if tuple(c) != start and tuple(c) != goal]
    np.random.shuffle(free_cells)
    return free_cells[:num_extra]

def plot_grid(data, selected_algo, extra_victims, current_step=None):
    """Renders the grid with matplotlib to look like a map UI."""
    grid = data['grid']
    start = data['start']
    goal = data['goal']
    path = data['paths'].get(selected_algo, [])
    
    # Handle animation path slicing
    if current_step is not None:
        path = path[:current_step]
        
    display_grid = np.zeros_like(grid, dtype=int)
    display_grid[grid == 1] = 1 # Obstacle/Debris
    
    # Mapping values: 0: free, 1: debris, 2: path, 3: drone start, 4: victim
    
    for r, c in path:
        if (r, c) != start and (r, c) != goal:
            display_grid[r, c] = 2
            
    display_grid[start[0], start[1]] = 3
    display_grid[goal[0], goal[1]] = 4
    
    # Render additional non-targeted victims
    for v in extra_victims:
        if v not in path: # Don't overwrite if path overlaps
            display_grid[v[0], v[1]] = 4
            
    # Colors: Light grey (road), dark grey/black (debris), green (path), blue (drone), red (victim)
    cmap = ListedColormap(['#EAEAEA', '#2C3E50', '#27AE60', '#2980B9', '#E74C3C'])
    
    # Scaled down to prevent vertical scrolling
    fig, ax = plt.subplots(figsize=(5.5, 5.5))
    ax.imshow(display_grid, cmap=cmap, vmin=0, vmax=4)
    
    # Map Enhancements: Render grid lines like map boundaries
    ax.set_xticks(np.arange(-0.5, grid.shape[1], 1), minor=True)
    ax.set_yticks(np.arange(-0.5, grid.shape[0], 1), minor=True)
    ax.grid(which='minor', color='white', linestyle='-', linewidth=1.5)
    
    # Optionally overlay coordinate markers every 5 units for realism
    ax.set_xticks(np.arange(0, grid.shape[1], 5))
    ax.set_yticks(np.arange(0, grid.shape[0], 5))
    ax.set_xticklabels(np.arange(0, grid.shape[1], 5), fontsize=8, color='gray')
    ax.set_yticklabels(np.arange(0, grid.shape[0], 5), fontsize=8, color='gray')
    ax.tick_params(which='both', bottom=False, left=False)
    
    return fig

# 4. MAIN APP LAYOUT
def main():
    initialize_session_state()
    
    # Header Section
    st.title("🚁 Disaster Rescue Simulation Map")
    st.markdown("An AI-powered drone navigation map for disaster response and victim locator operations.")
    st.divider()
    
    # Main Layout
    col_map, col_panel = st.columns([2, 1], gap="large")
    
    with col_panel:
        st.subheader("⚙️ Scenario Controls")
        
        scenario = st.selectbox("Disaster Scenario", ["Urban Rescue", "Earthquake Area", "Flood Zone"])
        default_density = get_scenario_defaults(scenario)
        
        grid_size = st.slider("Map Size (Grid)", 10, 30, 15)
        obstacle_density = st.slider("Debris Density", 0.0, 0.5, default_density, 0.05)
        
        if st.button("🗺️ Generate Area Map", use_container_width=True):
            with st.spinner("Mapping disaster area..."):
                st.session_state.sim_data = run_simulation(grid_size, obstacle_density)
                # Conceptually spawn 2 extra victims
                st.session_state.extra_victims = generate_extra_victims(
                    st.session_state.sim_data['grid'], 
                    st.session_state.sim_data['start'], 
                    st.session_state.sim_data['goal'], 
                    num_extra=2
                )
                st.session_state.animate = False

        st.divider()
        st.subheader("🧠 Navigation System")
        selected_algo = st.selectbox("Search Algorithm", ["BFS", "DFS", "A*"], index=2)
        
        col_btn1, col_btn2 = st.columns(2)
        if col_btn1.button("🏃 Run Instantly", use_container_width=True):
            st.session_state.animate = False
            
        if col_btn2.button("▶️ Animate Path", use_container_width=True):
            st.session_state.animate = True

        # Render Stats Panel
        if st.session_state.sim_data is not None:
            st.divider()
            st.subheader("📊 Performance Diagnostics")
            
            stats = st.session_state.sim_data.get('stats', {})
            df_data = {'Algorithm': [], 'Path Length': [], 'Nodes Explored': []}
            
            for alg in ["BFS", "DFS", "A*"]:
                if alg in stats:
                    df_data['Algorithm'].append(alg)
                    df_data['Path Length'].append(stats[alg].get('path_len', '-'))
                    df_data['Nodes Explored'].append(stats[alg].get('nodes', '-'))
                    
            st.dataframe(pd.DataFrame(df_data), hide_index=True, use_container_width=True)
            st.success("✨ **A* Algorithm** optimally balances path length and fewer nodes explored, making it ideal for drone battery constraints.")
            
    with col_map:
        if st.session_state.sim_data is None:
            st.info("👈 Please define the scenario and click 'Generate Area Map' to begin the simulation.")
            
            # Map Legend Placeholder
            st.markdown("### Map Legend")
            st.markdown("🟦 **Drone Deploy Base**")
            st.markdown("🟥 **Identified Victim Locator**")
            st.markdown("⬛ **Impassable Debris / Blocked**")
            st.markdown("🟩 **Secure Flight Path**")
            st.markdown("⬜ **Clear Zone / Accessible Range**")
        else:
            st.subheader(f"📍 Area Map: {scenario}")
            
            start_pos = st.session_state.sim_data['start']
            target_pos = st.session_state.sim_data['goal']
            victims_count = len(st.session_state.extra_victims) + 1
            
            # Smart UI info element
            st.info(f"🚁 **Drone Base:** {start_pos} &nbsp; | &nbsp; 🎯 **Target Victim:** {target_pos} &nbsp; | &nbsp; ⚠️ **Total Victims Detected:** {victims_count}")
            st.markdown("🔄 *Status:* `Drone calculating optimal route & navigating to nearest targeted priority victim...`")
            
            # Map rendering placeholder
            map_placeholder = st.empty()
            
            # Animation Logic
            if st.session_state.animate:
                path = st.session_state.sim_data['paths'].get(selected_algo, [])
                for i in range(1, len(path) + 1):
                    fig = plot_grid(st.session_state.sim_data, selected_algo, st.session_state.extra_victims, current_step=i)
                    map_placeholder.pyplot(fig, use_container_width=False)
                    plt.close(fig)
                    time.sleep(0.02) # Quick delay for snappy animation
                st.session_state.animate = False # Disable post-animation to prevent infinite loops
            else:
                # Static render
                fig = plot_grid(st.session_state.sim_data, selected_algo, st.session_state.extra_victims)
                map_placeholder.pyplot(fig, use_container_width=False)
                plt.close(fig)
            
            # Bottom Legend
            st.caption("🟦 Base Start | 🟥 SOS Victim | ⬛ Debris Barrier | 🟩 Safe AI Flight Path | ⬜ Clear Trajectory")

if __name__ == "__main__":
    main()