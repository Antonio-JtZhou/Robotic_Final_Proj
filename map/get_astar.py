import math
import numpy as np
import matplotlib.pyplot as plt
import json
import os
from collections import defaultdict

# --- 辅助函数 (未改变) ---

def heuristic(point1, point2):
    """计算两点之间的欧几里得距离作为启发函数。"""
    return math.sqrt((point1[0] - point2[0]) ** 2 + (point1[1] - point2[1]) ** 2)

def get_neighors(point):
    """获取一个点的所有8个邻居点。"""
    neighbours = []
    for i in range(-1, 2):
        for j in range(-1, 2):
            if i == 0 and j == 0:
                continue
            neighbours.append((point[0] + i, point[1] + j))
    return neighbours

def current_cost(point1, point2):
    """计算从一个点到其邻居点的移动成本。"""
    return math.sqrt((point1[0] - point2[0]) ** 2 + (point1[1] - point2[1]) ** 2)

# --- 路径重构和A*算法 (未改变) ---

def reconstruct_all_paths(parent_map, start_point, end_point):
    """
    使用深度优先搜索从parent_map中重构所有最优路径。
    """
    # 如果终点没有父节点，说明没有路径
    if end_point not in parent_map:
        return []
    
    # 使用一个栈来进行DFS
    stack = [(end_point, [end_point])]
    all_paths = []
    
    while stack:
        current_node, path = stack.pop()
        
        # 如果回溯到了起点，说明找到了一条完整路径
        if current_node == start_point:
            all_paths.append(path[::-1]) # 反转路径使其从起点开始
            continue
        
        # 将父节点推入栈中继续回溯
        if current_node in parent_map:
            for parent in parent_map[current_node]:
                new_path = path + [parent]
                stack.append((parent, new_path))
                
    return all_paths

def astar_find_all_optimal(road_map, start_point, end_point):
    """
    修改后的A*算法，用于寻找所有最优路径。
    """
    x_max, y_max = road_map.shape
    open_list = []
    
    # g_values 存储实际代价
    g_values = defaultdict(lambda: float('inf'))
    # parent_map 的值现在是一个列表，允许多个等价的父节点
    parent_map = defaultdict(list)
    
    min_cost = float('inf') # 记录已找到的到终点的最小代价

    # 初始化
    g_values[start_point] = 0
    f_value_start = heuristic(start_point, end_point)
    # open_list 中存储 (f_value, point)，以便高效排序
    open_list.append((f_value_start, start_point)) 
    
    while open_list:
        # 按f值排序，取出最小的节点
        open_list.sort(key=lambda x: x[0], reverse=True)
        current_f, current_point = open_list.pop()

        # 剪枝：如果当前节点的f值已经超过找到的最优路径代价，则放弃
        if current_f > min_cost:
            continue
        
        # 如果到达终点，更新最小代价
        if current_point == end_point:
            min_cost = min(min_cost, g_values[current_point])
            continue # 继续搜索其他等价路径

        # 探索邻居
        for neighbor in get_neighors(current_point):
            if not (0 <= neighbor[0] < x_max and 0 <= neighbor[1] < y_max and road_map[neighbor[0], neighbor[1]] != 1):
                continue
            
            tentative_g_value = g_values[current_point] + current_cost(current_point, neighbor)
            
            # 剪枝：如果新g值已经不优于已知的最优路径，则放弃
            if tentative_g_value + heuristic(neighbor, end_point) > min_cost:
                continue
            
            # 找到一条更优的路径
            if tentative_g_value < g_values[neighbor]:
                g_values[neighbor] = tentative_g_value
                parent_map[neighbor] = [current_point] # 重置父节点列表
                f_value_neighbor = tentative_g_value + heuristic(neighbor, end_point)
                open_list.append((f_value_neighbor, neighbor))
            # 找到一条成本相等的路径
            elif tentative_g_value == g_values[neighbor]:
                parent_map[neighbor].append(current_point) # 添加到父节点列表

    # 搜索结束后，从终点开始重构所有路径
    if min_cost == float('inf'):
        print("未能找到路径。")
        return [], float('inf')
    
    all_paths = reconstruct_all_paths(parent_map, start_point, end_point)
    print(f"路径搜索完成！找到 {len(all_paths)} 条最优路径。")
    print(f"路径代价: {min_cost}")
    return all_paths, min_cost

# --- 绘图 (未改变) ---

def plot_map_and_save(road_map, start_point, end_point, paths, save_path):
    """
    绘制地图和路径。为了清晰，只绘制第一条找到的最优路径。
    """
    plt.figure()
    plt.imshow(road_map, cmap='gray', origin='lower') # origin='lower' ensures (0,0) is bottom-left

    # Plotting start and end points with swapped coordinates (x, y)
    plt.plot(start_point[1], start_point[0], 'go', markersize=10, label='Start') # Swap (row, col) to (col, row) for plotting
    plt.plot(end_point[1], end_point[0], 'ro', markersize=10, label='End')     # Swap (row, col) to (col, row) for plotting

    if paths:
        # 只绘制第一条路径以保持图片清晰
        first_path = paths[0]
        # Swap (row, col) to (col, row) for plotting the path
        path_cols = [point[1] for point in first_path]
        path_rows = [point[0] for point in first_path]
        plt.plot(path_cols, path_rows, 'b-', linewidth=2, label=f'Optimal Path (1 of {len(paths)})')

    plt.xlabel('X Coordinate')
    plt.ylabel('Y Coordinate')
    plt.title('A* All Optimal Paths Finding')
    plt.legend()
    plt.grid(True)
    plt.savefig(save_path)
    plt.close()



def get_astar():
    """
    主函数，为每个案例执行A*算法，保存所有找到的最优路径，并保存处理过的地图。
    """
    input_filename = "matrices.jsonl"
    output_base_dir = "astar_results_all_paths"

    os.makedirs(output_base_dir, exist_ok=True)
    print(f"结果将保存在 '{output_base_dir}' 文件夹中。")

    if not os.path.exists(input_filename):
        print(f"错误: 输入文件 '{input_filename}' 未找到。")
        return

    with open(input_filename, 'r') as f:
        for i, line in enumerate(f):
            print(f"\n--- 正在处理案例 {i} ---")
            data = json.loads(line)
            road_map = np.array(data["map"])
            start_point = tuple(data["start"])
            end_point = tuple(data["end"])
            
            print(f"起点: {start_point}, 终点: {end_point}")

            case_dir = os.path.join(output_base_dir, f"case_{i}")
            os.makedirs(case_dir, exist_ok=True)

            # 保存处理过的地图到 map.jsonl
            map_save_path = os.path.join(case_dir, "map.jsonl")
            map_data = {
                "map": road_map.tolist(),  # 转换为列表以兼容JSON
                "start": list(start_point),  # 转换为列表以兼容JSON
                "end": list(end_point)  # 转换为列表以兼容JSON
            }
            with open(map_save_path, 'w') as map_file:
                json.dump(map_data, map_file)
                map_file.write('\n')  # 确保JSONL格式
            print(f"处理过的地图已保存到: {map_save_path}")

            # 使用新算法查找所有最优路径
            paths, cost = astar_find_all_optimal(road_map, start_point, end_point)

            # 保存可视化图片（只显示第一条路径）
            image_save_path = os.path.join(case_dir, "path_visualization.png")
            plot_map_and_save(road_map, start_point, end_point, paths, image_save_path)
            print(f"路径可视化图片已保存到: {image_save_path}")

            # 保存包含所有路径和第一步走向的结果文本
            result_save_path = os.path.join(case_dir, "result.txt")
            with open(result_save_path, 'w') as res_file:
                if paths:
                    res_file.write(f"Status: Found {len(paths)} optimal path(s).\n")
                    res_file.write(f"Optimal Path Cost: {cost}\n")
                    
                    # 计算并记录所有最优路径的第一步的唯一走向
                    first_steps = set()
                    for path in paths:
                        # 确保路径至少有两个点才能计算走向
                        if len(path) > 1:
                            # 走向 = (下一个点的行 - 起点的行, 下一个点的列 - 起点的列)
                            direction = (path[1][0] - path[0][0], path[1][1] - path[0][1])
                            first_steps.add(direction)
                    
                    # 为保证输出顺序一致，对集合进行排序
                    sorted_first_steps = sorted(list(first_steps))
                    # 将走向列表转换为字符串，如 "(-1, 1), (0, 1)"
                    first_steps_str = ', '.join(map(str, sorted_first_steps))
                    res_file.write(f"First step directions of all optimal paths: {first_steps_str}\n\n")
                    
                    for j, path in enumerate(paths):
                        path_str = " -> ".join(map(str, path))
                        res_file.write(f"Path #{j+1}: {path_str}\n")
                else:
                    res_file.write("Status: Path not found.\n")
            print(f"所有最优路径及第一步走向结果已保存到: {result_save_path}")

if __name__ == '__main__':
    get_astar()