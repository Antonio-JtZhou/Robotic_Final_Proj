import requests
import json
import re
import matplotlib.pyplot as plt
import numpy as np

# ✅ 外部API配置
API_URL = 'https://openrouter.ai/api/v1/chat/completions'
API_KEY = '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'

headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {API_KEY}"
}

# ✅ 地图定义
map_str = """
0 0 0 0 0 0 0 0 0 0 1 1 1 1 1 1
0 0 0 0 0 0 1 1 1 1 1 1 1 1 1 1
2 0 0 0 0 0 1 1 1 1 1 0 0 0 0 3 
0 0 0 0 0 0 0 0 0 0 0 0 0 1 1 1
0 0 0 0 0 0 1 1 1 1 1 0 0 1 1 1
0 0 0 0 0 1 1 1 1 1 1 1 0 1 1 1
0 0 0 1 1 1 1 1 1 1 1 1 1 1 1 1
0 0 0 0 0 1 1 1 1 1 1 1 1 0 1 1
0 0 0 0 1 1 1 1 1 1 1 1 1 0 1 1
0 0 0 1 1 1 1 1 1 1 1 1 1 0 1 1
0 0 0 1 1 1 1 1 1 1 1 1 1 0 1 1
0 0 0 1 1 1 1 1 1 1 1 1 1 0 1 1
0 0 0 1 0 1 1 1 1 1 1 1 1 0 1 1
0 0 0 0 0 1 1 1 1 1 1 1 1 0 1 1
0 0 0 0 0 1 1 1 1 1 1 1 1 0 0 0
0 0 0 0 0 1 1 1 1 1 1 1 0 0 0 0
"""

# ✅ 将地图转成二维数组
map_data = [list(map(int, line.strip().split())) for line in map_str.strip().split('\n')]
map_array = np.array(map_data)

# ✅ 找到起点和终点
start = np.argwhere(map_array == 2)[0].tolist()  # [2, 0]
end = np.argwhere(map_array == 3)[0].tolist()    # [2, 15]

# ✅ 构造Prompt
prompt = f"""
你是一个路径规划专家。

这是一个16x16的二维网格地图，数字意义如下：
- 0：可通行
- 1：障碍物
- 2：起点
- 3：终点

地图如下：
{map_str}

规则：
- 每一步可以向上下左右或者斜对角8个方向走。
- 目标是从起点{start}到终点{end}，找到一条欧氏距离最短的路径。

请直接输出路径的坐标序列，格式如下：
[[x1, y1], [x2, y2], ..., [xn, yn]]
其中x是列（横坐标），y是行（纵坐标）。

请严格按照上述格式输出路径，不要输出其他任何文字。
"""

# ✅ 调用API
payload = {
    "model": "x-ai/grok-3-mini-beta",   # 替换为你要用的外部模型
    "messages": [
        {"role": "user", "content": prompt}
    ],
    "temperature": 0.6,
}

response = requests.post(API_URL, headers=headers, json=payload)

if response.status_code == 200:
    result = response.json()
    reply = result['choices'][0]['message']['content']
    print("✅ 模型返回路径：", reply)

    # ✅ 解析路径
    path = json.loads(reply)  # 直接反序列化
    print("✅ 解析路径:", path)

    # ✅ 绘图展示
    plt.figure(figsize=(8, 8))
    plt.imshow(map_array, cmap='Greys')

    # 起点终点
    plt.scatter(start[1], start[0], color='green', s=200, label='Start')
    plt.scatter(end[1], end[0], color='red', s=200, label='End')

    # 路径
    if path:
        path_x = [p[0] for p in path]
        path_y = [p[1] for p in path]
        plt.plot(path_x, path_y, color='blue', linewidth=2, label='Path')
        plt.scatter(path_x, path_y, color='blue')

    plt.legend()
    plt.title("Optimal Path")
    plt.grid(True)
    plt.savefig("optimal_path.png", dpi=300) 
    # plt.show()

else:
    print("❌ 请求失败:", response.status_code, response.text)
