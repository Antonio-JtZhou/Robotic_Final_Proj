import json


def convert_map_to_string(map_data):
    """将二维地图转换为字符串，便于填入prompt"""
    return "\n".join([" ".join(map(str, row)) for row in map_data])


def convert_to_sft_json(input_file, output_file, template):
    """转换成SFT格式，output是llm的回答，保存为JSON列表"""
    data_list = []
    
    with open(input_file, "r") as f:
        for line in f:
            item = json.loads(line)
            
            # 解析字段
            map_data = convert_map_to_string(item["map"])
            start_point = item["start"]
            end_point = item["end"]
            llm_response = item["llm_raw_response"]
            
            # 构造input
            input_text = template.format(
                map_data=map_data,
                start_point=start_point,
                end_point=end_point
            )
            
            # 构造output
            try:
                output_text = llm_response.strip()
            except:
                continue        
            data_list.append({
                "instruction": input_text,
                "input": "",
                "output": output_text
            })
    
    # 保存为JSON文件（整体是一个列表）
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(data_list, f, ensure_ascii=False, indent=2)

    print(f"✅ 成功保存到 {output_file}")


# ✅ 模板
template = """**路径规划问题描述**：
这是一个 16x16 的二维地图：
{map_data}
- 地图中，`1` 表示障碍物（不可通过），`0` 表示可通行区域。
- 每个格点的索引 `[i,j]` 表示其坐标，其中`i` 为行，`j`为列号。
- 起点坐标为 {start_point}，终点坐标为 {end_point}。
- 每一步只能移动到当前格点的八邻域（即上下左右及四个对角方向的相邻格点），且目标格点必须是可通行的（值为 `0`）。
- 目标是找到从起点到终点的路径，使得整条路径的欧氏距离最短。

**任务**：
找到从起点到终点的路径，使得整条路径的欧氏距离最短。
请你首先分析问题，给出分析的思路，并在输出的末尾给出从起点 {start_point} 开始，的第一步应该移动到的格点的坐标 `[i,j]`。输出坐标的格式为$$x,y$$.
"""

input_file = "/scratch/zhoujunting/zjt/Robotics/test/100_matrices_with_llm_DS-R1.jsonl"    # 输入文件
output_file = "sft.jsonl"  # 输出文件

convert_to_sft_json(input_file, output_file, template)

print("转换完成")
