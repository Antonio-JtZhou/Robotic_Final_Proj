import random
import json
import math
from check_reachable import check_reachable
import signal

def generate_random_matrix(n, m_percent, seed=None):
    # Set random seed if provided
    if seed is not None:
        random.seed(seed)
    # Initialize nxn matrix with zeros
    matrix = [[0 for _ in range(n)] for _ in range(n)]
    # Calculate number of positions to set to 1
    total_positions = n * n
    ones_to_place = math.floor(total_positions * m_percent / 100)
    # Randomly select positions for 1s
    positions = random.sample([(i, j) for i in range(n) for j in range(n)], ones_to_place)    
    # Set selected positions to 1
    for i, j in positions:
        matrix[i][j] = 1
    return matrix

def select_start_end_points(matrix):
    n = len(matrix)
    start_candidates = []
    end_candidates = []
    
    # Define eight neighbors relative positions
    neighbors = [(-1,-1), (-1,0), (-1,1), (0,-1), (0,1), (1,-1), (1,0), (1,1)]
    
    # Check each position in the matrix
    for i in range(n):
        for j in range(n):
            if matrix[i][j] == 0:  # Only consider positions with value 0
                # Calculate sum of eight neighbors
                neighbor_sum = 0
                for di, dj in neighbors:
                    ni, nj = i + di, j + dj
                    if 0 <= ni < n and 0 <= nj < n:
                        neighbor_sum += matrix[ni][nj]
                
                # Check conditions for start and end points
                if neighbor_sum < 4:
                    start_candidates.append([i, j])
                if neighbor_sum < 8:
                    end_candidates.append([i, j])
    
    # If no valid points found, return None
    if not start_candidates or not end_candidates:
        return None, None
    
    # Try to find valid start-end pair with Manhattan distance >= n
    random.shuffle(start_candidates)
    for start in start_candidates:
        valid_ends = [
            end for end in end_candidates
            if abs(start[0] - end[0]) + abs(start[1] - end[1]) >= n
        ]
        if valid_ends:
            return start, random.choice(valid_ends)
    
    # If no valid pair found, return None
    return None, None

# Define timeout handler
class TimeoutException(Exception):
    pass

def timeout_handler(signum, frame):
    raise TimeoutException("check_reachable timed out")

def get_map(filename, nums, n, m_percent):
    data = []
    seed = 0
    
    # Set up signal handler for timeout
    signal.signal(signal.SIGALRM, timeout_handler)
    
    while nums:
        seed += 1
        print("seed:", seed, " nums=", nums)
        matrix = generate_random_matrix(n, m_percent, seed=seed)
        start_point, end_point = select_start_end_points(matrix)
        print("points selected!")
        
        try:
            # Set timeout for 10 seconds
            signal.alarm(10)
            if check_reachable(matrix, start_point, end_point, 5):
                matrix_data = {
                    "n": n,
                    "m%": m_percent,
                    "map": matrix,
                    "start": start_point,
                    "end": end_point
                }
                data.append(matrix_data)
                nums -= 1
            # Disable alarm after successful execution
            signal.alarm(0)
            
        except TimeoutException:
            print(f"Seed {seed} timed out, skipping to next seed")
            signal.alarm(0)  # Disable alarm
            continue
            
    with open(filename, 'w') as f:
        for item in data:
            json.dump(item, f)
            f.write('\n')
# Example usage
if __name__ == "__main__":
    # Example parameters
    n = 16           # Size of matrix (n x n)
    m_percent = 50  # Percentage of positions to set to 1
    nums = 100        # Number of matrices to generate
    
    get_map("matrices.jsonl", nums, n, m_percent)