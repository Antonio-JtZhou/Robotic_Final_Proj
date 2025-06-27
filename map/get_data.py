from get_astar import get_astar
from get_map import get_map
from get_firstmove import get_firstmove

if __name__ == "__main__":
    # Example parameters
    n = 16           # Size of matrix (n x n)
    m_percent = 50  # Percentage of positions to set to 1
    nums = 1000        # Number of matrices to generate
    
    get_map("matrices.jsonl", nums, n, m_percent)
    get_astar()

    input_file  = "/scratch/zhoujunting/zjt/Robotics/data/metrics.jsonl"  # Replace with your input JSONL file path
    output_file = "/scratch/zhoujunting/zjt/Robotics/data/metrics_final.jsonl" 
    astar_results_base_dir = "/scratch/zhoujunting/zjt/Robotics/data/astar_result.jsonl"
    get_firstmove(input_file, output_file, astar_results_base_dir)