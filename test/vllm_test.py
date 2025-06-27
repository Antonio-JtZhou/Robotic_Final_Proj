from openai import OpenAI
import json
import re
import os
from distill_template import template


# 替换成你的服务器地址
client = OpenAI(base_url="http://localhost:8000/v1", api_key="EMPTY")


# 数据路径
input_path = "/scratch/zhoujunting/zjt/Robotics/test/100_matrices_final.jsonl"
output_path = "/scratch/zhoujunting/zjt/Robotics/test/100_matrices_with_llm_answer_vllm.jsonl"

# 读取数据
with open(input_path, 'r', encoding='utf-8') as f:
    data_list = [json.loads(line.strip()) for line in f]

pattern = r"\$\$\s*([-\d\.]+)\s*,\s*([-\d\.]+)\s*\$\$"

results = []

for idx, item in enumerate(data_list):
    prompt = template.format(
        map_data=item['map'],
        start_point=item['start'],
        end_point=item['end']
    )
    ground_truth = item['next_position']

    try:
        response = client.chat.completions.create(
            model="/scratch/zhoujunting/zjt/LLaMA-Factory/models/robotic/checkpoint-27",  # 模型名随便写，vLLM不校验
            messages=[
                {"role": "user", "content": prompt}
            ],
            max_tokens=8192,
            temperature=0
        )

        content = response.choices[0].message.content

        match = re.search(pattern, content)
        if match:
            x = int(float(match.group(1)))
            y = int(float(match.group(2)))
            parsed_llm_answer = [x, y]
        else:
            parsed_llm_answer = None

        is_correct = parsed_llm_answer == ground_truth

        print(f"Prompt {idx} - LLM: {parsed_llm_answer}, GT: {ground_truth}, Correct: {is_correct}")

        result = {
            "map": item['map'],
            "start": item['start'],
            "end": item['end'],
            "ground_truth": ground_truth,
            "llm_answer": parsed_llm_answer,
            "llm_raw_response": content,
            "is_correct": is_correct
        }

    except Exception as e:
        print(f"Prompt {idx} - Error: {e}")
        result = {
            "map": item['map'],
            "start": item['start'],
            "end": item['end'],
            "ground_truth": ground_truth,
            "llm_answer": None,
            "llm_raw_response": None,
            "is_correct": False,
            "error": str(e)
        }

    results.append(result)


# 保存结果
os.makedirs(os.path.dirname(output_path), exist_ok=True)
with open(output_path, 'w', encoding='utf-8') as f:
    for item in results:
        f.write(json.dumps(item, ensure_ascii=False) + '\n')

# 正确率统计
correct = sum(1 for item in results if item['is_correct'])
print(f"\n✅ Correct answers: {correct}/{len(results)}")
print(f"✅ Output saved to {output_path}")
