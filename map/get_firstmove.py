import json
import os
import re

def parse_first_moves_from_file(file_path):
    """
    从给定的 astar a* a* a* a* a* a* a* a* a* a* a* a* a* a* a* a* a* a* a* a* a* a* a* a* a* a* a* a* a* a* a* a* a* a* a* a* a* a* a* a* a* a* a* a* a* a* a* a* a* a* a* a* a* a* a* a* a* a* a* a* a* a* a* a* a* a* a* a* a* a* a* a* a* a* a* a* a* a* a* a* a* a* a* a* a* a* a* a* a* a* a* a* a* a* a* a* a* a* a* a* a* a* a* a* a* a* a* a* a* a* a* a* a* a* a* a* a* a* a* a* a* a* a* a* a* a* a* a* a* a* a* a* a* a* a* a* a* a* a* a* a* a* a* a* a* a* a* a* a* a* a* a* a* a* a* a* a* a* a* a* a* a* a* a* a* a* a* a* a* a* a* a* a* a* a* a* a* a* a* a* a* a* a* a* a* a* a* a* a* a* a* a* a* a* a* a* a* a* a* a* a* a* a* a* a* a* a* a* a* a* a* a* a* a* a* a* a* a* a* a* a* a* a* a* a* a* a* a* a* a* a* a* a* a* a* a* a* a* a* a* a* a* a* a* a* a* a* a* a* a* a* a* a* a* a* a* a* a* a* a* a* a* a* a* a* a* a* a* a* a* a* a-
    First step directions of all optimal paths: ...
    并将其转换为一个整数列表。
    例如：'(0, 1), (1, 1)' 会被转换为 [[0, 1], [1, 1]]
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                if "First step directions of all optimal paths:" in line:
                    # 提取冒号后面的数据部分
                    data_part = line.split(":")[1].strip()
                    
                    # 使用正则表达式查找所有 (x, y) 形式的元组
                    # 正则表达式能很好地处理数字和逗号周围可能存在的空格
                    tuples = re.findall(r'\(\s*(-?\d+)\s*,\s*(-?\d+)\s*\)', data_part)
                    
                    # 将找到的字符串元组转换为整数列表
                    first_moves = [[int(x), int(y)] for x, y in tuples]
                    return first_moves
    except FileNotFoundError:
        print(f"警告: 文件未找到 {file_path}")
    except Exception as e:
        print(f"警告: 处理文件 {file_path} 时发生错误: {e}")
    
    # 如果没有找到对应的行或文件，返回一个空列表
    return []

def get_firstmove(input_jsonl_path, output_jsonl_path, base_data_dir):
    """
    处理JSONL文件，为每一行数据添加 first_move 字段。

    :param input_jsonl_path: 输入的JSONL文件路径。
    :param output_jsonl_path: 输出的JSONL文件路径。
    :param base_data_dir: 存放 astar 结果的基础目录路径。
    """
    print(f"开始处理文件: {input_jsonl_path}")
    
    # 使用 'with' 语句确保文件会被自动关闭
    with open(input_jsonl_path, 'r', encoding='utf-8') as infile, \
         open(output_jsonl_path, 'w', encoding='utf-8') as outfile:
        
        # 使用 enumerate 来获取行号，起始为 1
        for i, line in enumerate(infile):
            line_number = i 
            
            try:
                # 解析当前行的JSON数据
                data = json.loads(line.strip())
            except json.JSONDecodeError:
                print(f"警告: 第 {line_number} 行JSON格式错误，已跳过。")
                continue

            # 构建 astar 结果文件的完整路径
            # 例如: /path/to/data/case_1/results.txt
            results_file_path = os.path.join(base_data_dir, f"case_{line_number}", "result.txt")
            
            # 从 results.txt 文件中解析出 first_move
            first_moves_list = parse_first_moves_from_file(results_file_path)
            print(first_moves_list)
            # 将解析出的列表添加到JSON数据中
            data['first_move'] = first_moves_list
            
            # 将更新后的JSON对象写回新的JSONL文件，并添加换行符
            # ensure_ascii=False 确保中文字符不会被转义
            outfile.write(json.dumps(data, ensure_ascii=False) + '\n')

    print(f"处理完成！结果已保存到: {output_jsonl_path}")


# --- 主程序入口 ---
if __name__ == "__main__":
    # --- 请在这里修改您的文件路径 ---

    input_file  = "/scratch/zhoujunting/zjt/Robotics/data/metrics.jsonl"  # Replace with your input JSONL file path
    output_file = "/scratch/zhoujunting/zjt/Robotics/data/metrics_final.jsonl" 
    # 3. astar 结果的基础目录
    astar_results_base_dir = "/scratch/zhoujunting/zjt/Robotics/data/astar_result.jsonl"
    
    # --- 文件路径修改结束 ---

    # 检查输入文件是否存在
    if not os.path.exists(input_file):
        print(f"错误: 输入文件不存在: {input_file}")
    else:
        # 调用主处理函数
        get_firstmove(input_file, output_file, astar_results_base_dir)

