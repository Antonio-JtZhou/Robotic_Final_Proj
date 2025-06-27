from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline
import json
import re
import os

from distill_template import template

model_path = ""  # 替换成你本地模型的路径
model = AutoModelForCausalLM.from_pretrained(model_path, device_map="auto")
tokenizer = AutoTokenizer.from_pretrained(model_path)

generator = pipeline("text-generation", model=model, tokenizer=tokenizer)


# 数据路径
input_path = ""
output_path = ""


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
        output = generator(prompt, max_new_tokens=16384)[0]['generated_text']
        content = output[len(prompt):] 

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


os.makedirs(os.path.dirname(output_path), exist_ok=True)
with open(output_path, 'w', encoding='utf-8') as f:
    for item in results:
        f.write(json.dumps(item, ensure_ascii=False) + '\n')

correct = sum(1 for item in results if item['is_correct'])
print(f"Correct answers: {correct}/{len(results)}")
print(f"Output saved to {output_path}")
