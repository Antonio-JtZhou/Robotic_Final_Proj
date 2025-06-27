def check_reachable(grid, start, end, n):
    if not grid or not start or not end or n < 1:
        return False
    
    rows, cols = len(grid), len(grid[0])
    
    # 检查起点和终点是否有效
    if (start[0] < 0 or start[0] >= rows or 
        start[1] < 0 or start[1] >= cols or 
        end[0] < 0 or end[0] >= rows or 
        end[1] < 0 or end[1] >= cols or 
        grid[start[0]][start[1]] == 1 or 
        grid[end[0]][end[1]] == 1):
        return False
    
    # 八个方向：上下左右及对角
    directions = [
        (-1, 0), (1, 0), (0, -1), (0, 1),
        (-1, -1), (-1, 1), (1, -1), (1, 1)
    ]
    
    # 记录路径数量
    path_count = [0]
    
    def dfs(x, y, visited):
        # 提前终止：找到足够路径
        if path_count[0] >= n:
            return
        
        # 到达终点
        if x == end[0] and y == end[1]:
            path_count[0] += 1
            return
        
        # 遍历每个方向
        for dx, dy in directions:
            new_x, new_y = x + dx, y + dy
            # 检查新坐标是否有效
            if (0 <= new_x < rows and 
                0 <= new_y < cols and 
                grid[new_x][new_y] == 0 and 
                (new_x, new_y) not in visited):
                visited.add((new_x, new_y))
                dfs(new_x, new_y, visited)
                visited.remove((new_x, new_y))
    
    # 初始化访问集合
    visited = {(start[0], start[1])}
    dfs(start[0], start[1], visited)
    
    # 返回是否找到至少 n 条路径
    return path_count[0] >= n

# 示例用法
if __name__ == "__main__":
    # 示例地图：0表示可走，1表示障碍
    example_grid = [
        [0, 0, 0, 1],
        [1, 1, 0, 1],
        [0, 0, 0, 0]
    ]
    start_pos = [0, 0]  # 起点
    end_pos = [2, 3]   # 终点
    n_paths = 2        # 要求至少2条路径
    result = has_n_paths(example_grid, start_pos, end_pos, n_paths)
    print(f"Has at least {n_paths} paths: {result}")