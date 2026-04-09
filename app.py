import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
import matplotlib.patches as mpatches
import pandas as pd
from main import run_simulation

st.set_page_config(page_title="AI Rescue Drone Agent", layout="wide", initial_sidebar_state="expanded")

def load_css():
    st.markdown("""
        <style>
        /* Base Streamlit theme overrides for sci-fi look */
        .stApp { background-color: #050a15; color: #4ac1e8; font-family: 'Consolas', 'Courier New', monospace; }
        h1, h2, h3 { color: #4ac1e8 !important; text-transform: uppercase; letter-spacing: 2px;}
        [data-testid="stSidebar"] { border-right: 1px solid #112240; background-color: #030712;}
        
        /* Custom Metric Boxes */
        .metric-container {
            background-color: #081226;
            border: 1px solid #16325c;
            border-radius: 4px;
            padding: 15px 20px;
            box-shadow: 0 0 12px rgba(74, 193, 232, 0.15);
            margin-bottom: 20px;
            display: flex;
            flex-direction: column;
            align-items: flex-start;
        }
        .metric-label { font-size: 11px; color: #638b9e; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 8px;}
        .metric-val { font-size: 32px; font-weight: bold; color: #4ac1e8;}
        .val-bfs { color: #00d4ff; }
        .val-dfs { color: #ff9900; }
        .val-astar { color: #00ff88; }
        
        /* Button styling */
        div.stButton > button:first-child { 
            background-color: #061c3a; 
            color: #4ac1e8; 
            border: 1px solid #4ac1e8; 
            border-radius: 4px; 
            width: 100%;
            font-weight: bold;
            letter-spacing: 1px;
            padding: 15px;
            transition: all 0.3s ease;
        }
        div.stButton > button:hover { 
            background-color: #4ac1e8; 
            color: #050a15; 
            box-shadow: 0 0 15px rgba(74, 193, 232, 0.6); 
            border: 1px solid #4ac1e8;
        }
        
        hr { border-top: 1px solid #112240; }
        </style>
    """, unsafe_allow_html=True)

def initialize_state():
    if 'sim_data' not in st.session_state:
        st.session_state.sim_data = None
    if 'run_sim' not in st.session_state:
        st.session_state.run_sim = False

def render_metric(label, value, css_class=""):
    st.markdown(f"""
        <div class="metric-container">
            <div class="metric-label">{label}</div>
            <div class="metric-val {css_class}">{value}</div>
        </div>
    """, unsafe_allow_html=True)

def plot_custom_grid(data, algo, show_path=False):
    grid = data['grid']
    start = data['start']
    goal = data['goal']
    path = data['paths'].get(algo, []) if show_path else []
    
    display_grid = np.zeros_like(grid, dtype=int)
    display_grid[grid == 1] = 1 # Obstacle
    
    for r, c in path:
        if (r, c) != start and (r, c) != goal:
            display_grid[r, c] = 2
            
    display_grid[start[0], start[1]] = 3
    display_grid[goal[0], goal[1]] = 4
    
    # Colors matching screenshot: Free Cell, Obstacle, Path, Drone Start, Target
    cmap = ListedColormap(['#141c2f', '#060a12', '#00ff88', '#00d4ff', '#ff3366'])
    
    fig, ax = plt.subplots(figsize=(6, 6))
    ax.imshow(display_grid, cmap=cmap, vmin=0, vmax=4)
    
    # Draw grid lines
    ax.set_xticks(np.arange(-0.5, grid.shape[1], 1), minor=True)
    ax.set_yticks(np.arange(-0.5, grid.shape[0], 1), minor=True)
    ax.grid(which='minor', color='#25385e', linestyle='-', linewidth=1)
    ax.tick_params(which='both', bottom=False, left=False, labelbottom=False, labelleft=False)
    
    # Add text labels 'S' and 'E' inside specific cells
    ax.text(start[1], start[0], 'S', color='black', ha='center', va='center', fontweight='bold', fontsize=12)
    ax.text(goal[1], goal[0], 'E', color='white', ha='center', va='center', fontweight='bold', fontsize=12)
    
    # Background coloring
    fig.patch.set_facecolor('#050a15')
    ax.set_facecolor('#050a15')
    
    # Legend overlay inside the plot
    legend_elements = [
        mpatches.Patch(color='#00d4ff', label='Drone Start'),
        mpatches.Patch(color='#ff3366', label='Victim (E)'),
        mpatches.Patch(color='#00ff88', label='Path'),
        mpatches.Patch(color='#060a12', label='Obstacle'),
        mpatches.Patch(color='#141c2f', label='Free Cell'),
    ]
    ax.legend(handles=legend_elements, loc='upper right', facecolor='#081226', edgecolor='#16325c', labelcolor='#638b9e', fontsize=8)
    
    plt.tight_layout()
    return fig

def plot_bar_chart(stats, algo_list, metric, colors):
    fig, ax = plt.subplots(figsize=(6, 3))
    fig.patch.set_facecolor('#050a15')
    ax.set_facecolor('#050a15')
    
    values = [stats[alg].get(metric, 0) if alg in stats else 0 for alg in algo_list]
    bars = ax.bar(algo_list, values, color=colors, width=0.4)
    
    ax.set_ylabel(metric.replace('_', ' ').upper(), color='#638b9e', fontsize=9)
    ax.tick_params(axis='x', colors='#638b9e')
    ax.tick_params(axis='y', colors='#638b9e')
    
    # Axis spine hiding
    ax.spines['bottom'].set_color('#16325c')
    ax.spines['left'].set_color('#16325c')
    ax.spines['top'].set_color('none')
    ax.spines['right'].set_color('none')
    ax.yaxis.grid(True, color='#16325c', linestyle='--')
    
    # Add value labels onto bars
    for bar in bars:
        yval = bar.get_height()
        if yval > 0:
            ax.text(bar.get_x() + bar.get_width()/2, yval + (max(values)*0.02), str(int(yval)), 
                    ha='center', va='bottom', color='white', fontsize=10, fontweight='bold')
                
    plt.tight_layout()
    return fig

def main():
    load_css()
    initialize_state()
    
    # --- Sidebar Configuration ---
    st.sidebar.markdown("<h3 style='font-size:14px;'>⚙ SIMULATION CONTROLS</h3>", unsafe_allow_html=True)
    grid_size = st.sidebar.slider("Grid Size", 5, 30, 12)
    obstacle_density = st.sidebar.slider("Obstacle Density %", 0.0, 0.5, 0.20, 0.05)
    
    st.sidebar.markdown("<hr>", unsafe_allow_html=True)
    st.sidebar.markdown("<h3 style='font-size:14px;'>🧠 SELECT ALGORITHM</h3>", unsafe_allow_html=True)
    algo_dict = {
        "BFS": "BFS - Breadth First Search",
        "DFS": "DFS - Depth First Search",
        "A*": "A* Star Search"
    }
    # Radio styled to match the list approach
    selected_algo_label = st.sidebar.radio("Algorithm", list(algo_dict.values()), label_visibility="collapsed")
    selected_algo = [k for k, v in algo_dict.items() if v == selected_algo_label][0]
    
    st.sidebar.markdown("<br><br>", unsafe_allow_html=True)
    
    if st.sidebar.button("🔄 GENERATE NEW MAP"):
        st.session_state.sim_data = run_simulation(grid_size, obstacle_density)
        st.session_state.run_sim = False
        
    st.sidebar.markdown("<br>", unsafe_allow_html=True)
    if st.sidebar.button("▶ RUN SIMULATION"):
        st.session_state.run_sim = True
        
    # --- Main Screen Layout ---
    st.markdown("<h1>🚁 AI RESCUE DRONE AGENT</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color:#638b9e; font-size:12px; letter-spacing:3px;'>— PROTOTYPE SIMULATION • BFS • DFS • A* PATHFINDING • GRID WORLD ENGINE —</p>", unsafe_allow_html=True)
    st.markdown("<hr>", unsafe_allow_html=True)
    
    if st.session_state.sim_data:
        stats = st.session_state.sim_data.get('stats', {})
        current_stats = stats.get(selected_algo, {})
        
        path_len = current_stats.get('path_len', "-") if st.session_state.run_sim else "-"
        nodes_exp = current_stats.get('nodes', "-") if st.session_state.run_sim else "-"
        
        # dynamic coloring for selected algorithm
        color_class_map = {"BFS": "val-bfs", "DFS": "val-dfs", "A*": "val-astar"}
        algo_class = color_class_map[selected_algo]
        
        # Data Header Metrics
        m1, m2, m3 = st.columns(3)
        with m1: render_metric("SELECTED ALGORITHM", selected_algo, css_class=algo_class)
        with m2: render_metric("PATH LENGTH (STEPS)", path_len, css_class=algo_class)
        with m3: render_metric("NODES EXPLORED", nodes_exp, css_class=algo_class)
        
        st.markdown("<br>", unsafe_allow_html=True)
        col1, col2 = st.columns([1.5, 1], gap="large")
        
        with col1:
            st.markdown("<h3 style='font-size:15px; letter-spacing:2px;'>📍 MISSION GRID</h3>", unsafe_allow_html=True)
            
            # Map Generation
            fig_grid = plot_custom_grid(st.session_state.sim_data, selected_algo, st.session_state.run_sim)
            st.pyplot(fig_grid, use_container_width=True)
            plt.close(fig_grid)
            
            # Mission Coordinates
            start_pos = st.session_state.sim_data['start']
            goal_pos = st.session_state.sim_data['goal']
            
            st.markdown("<h3 style='font-size:15px; letter-spacing:2px; margin-top:20px;'>🚩 MISSION COORDINATES</h3>", unsafe_allow_html=True)
            c1, c2, c3 = st.columns(3)
            with c1: render_metric("DRONE START POSITION", f"Row {start_pos[0]}, Col {start_pos[1]}")
            with c2: render_metric("VICTIM LOCATION", f"Row {goal_pos[0]}, Col {goal_pos[1]}")
            with c3: render_metric("MAP DIMENSIONS", f"{grid_size} x {grid_size}")
            
        with col2:
            st.markdown("<h3 style='font-size:15px; letter-spacing:2px;'>📊 ALGORITHM COMPARISON</h3>", unsafe_allow_html=True)
            
            # Clean dataframe block
            df_data = {'ALGORITHM': [], 'PATH LEN': [], 'NODES': []}
            for alg in ["BFS", "DFS", "A*"]:
                if alg in stats:
                    df_data['ALGORITHM'].append(alg)
                    df_data['PATH LEN'].append(stats[alg].get('path_len', '-'))
                    df_data['NODES'].append(stats[alg].get('nodes', '-'))
                    
            st.dataframe(pd.DataFrame(df_data), hide_index=True, use_container_width=True)
            
            if st.session_state.run_sim:
                st.markdown("<br><h3 style='font-size:13px; color:#638b9e;'>NODES EXPLORED</h3>", unsafe_allow_html=True)
                fig_nodes = plot_bar_chart(stats, ["BFS", "DFS", "A*"], "nodes", ['#00d4ff', '#ff9900', '#00ff88'])
                st.pyplot(fig_nodes, use_container_width=True)
                plt.close(fig_nodes)
                
                st.markdown("<h3 style='font-size:13px; color:#638b9e; margin-top:15px;'>PATH LENGTH</h3>", unsafe_allow_html=True)
                fig_paths = plot_bar_chart(stats, ["BFS", "DFS", "A*"], "path_len", ['#00d4ff', '#ff9900', '#00ff88'])
                st.pyplot(fig_paths, use_container_width=True)
                plt.close(fig_paths)
                
                st.markdown("""
                <div style='background-color:#051219; border: 1px solid #00ff88; border-radius:4px; padding:15px; margin-top:20px; font-size:12px; color:#4ac1e8;'>
                    💡 <b>Insight:</b> Notice how the <b>A* Star Search</b> has the shortest path while exploring the fewest nodes? The heuristic approach dominates grid traversal.
                </div>
                """, unsafe_allow_html=True)
                
    else:
        st.info("Awaiting command. Click GENERATE NEW MAP in the sidebar.")

if __name__ == "__main__":
    main()