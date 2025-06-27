import requests
import numpy as np
import matplotlib.pyplot as plt
import json
import re

# 地图数据
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

map_data = np.array([
    list(map(int, line.strip().split()))
    for line in map_str.strip().split('\n')
])

start = tuple(map(int, np.argwhere(map_data == 2)[0]))  # (行, 列)
end = tuple(map(int, np.argwhere(map_data == 3)[0]))    # (行, 列)

prompt = f"""
你面前有一个16x16的地图，用数字表示：
- 0 表示空地，可以通行。
- 1 表示障碍物，不能通过。
- 2 表示起点。
- 3 表示终点。

地图：
{map_str}
不要输出其他任何文字，不要输出思考过程
请你找到从起点到终点的最短路径。路径表示为一组坐标序列，每个坐标是 [行, 列]，按顺序排列。
请直接输出路径的Python列表，例如：
[[2,0], [3,0], [4,0], ..., [2,15]]

"""

# 调用API
url = ""
headers = {"Content-Type": "application/json"}

payload = {
    "model": "robotic",  # 根据你的served-model-name
    "messages": [
        {"role": "user", "content": prompt}
    ],
    "max_tokens": 14000,
    "temperature": 0
}

response = requests.post(url, headers=headers, json=payload)
result = response.json()

reply = result['choices'][0]['message']['content']
print("模型回复：", reply)

try:
    path = eval(re.findall(r'(\[\[.*?\]\])', reply, re.S)[0])
except:
    raise ValueError("路径解析失败，模型回复格式不正确")

print("预测路径：", path)

with open('predicted_path.json', 'w') as f:
    json.dump(path, f)

plt.figure(figsize=(8, 8))
plt.imshow(map_data == 1, cmap="gray", origin="upper") 
path = np.array(path)
plt.plot(path[:, 1], path[:, 0], color='red', linewidth=2, marker='o', label='Predicted Path')


plt.scatter(start[1], start[0], color='green', s=100, label='Start')
plt.scatter(end[1], end[0], color='blue', s=100, label='End')

plt.legend()
plt.title('Predicted Shortest Path by LLM')
plt.grid(True)
plt.savefig('predicted_path.png')
plt.show()

