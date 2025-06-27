import asyncio
import json
import re
import ast
import httpx
# from template import template

from distill_template import template
# 配置
api_key = ''
base_url = ''
input_path = ""
output_path = ""

with open(input_path, 'r', encoding='utf-8') as f:
    data_list = [json.loads(line.strip()) for line in f]

async def fetch_response(client, idx, prompt, ground_truth, semaphore):
    url = f"{base_url}/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    payload = {
        # "model": "x-ai/grok-3-mini-beta",
        # 'model': "deepseek/deepseek-r1-0528",
        "model": "openai/gpt-4.1-mini",
        "messages": [
            {"role": "user", "content": prompt}
        ]
    }

    async with semaphore:
        try:
            resp = await client.post(url, headers=headers, json=payload, timeout=60)
            resp.raise_for_status()
            data = resp.json()
            content = data['choices'][0]['message']['content']

            # 正则提取答案
            pattern = r"\$\$\s*([-\d\.]+)\s*,\s*([-\d\.]+)\s*\$\$"
            match = re.search(pattern, content)

            if match:
                # llm_answer_str = match.group(1).strip()
                x = int(match.group(1))
                y = int(match.group(2))
                parsed_llm_answer = [x, y]
                # try:
                #     parsed_llm_answer = ast.literal_eval(llm_answer_str)
                # except (ValueError, SyntaxError):
                #     parsed_llm_answer = None
            else:
                parsed_llm_answer = None

            is_correct = parsed_llm_answer == ground_truth

            print(f"Prompt {idx} - LLM: {parsed_llm_answer}, GT: {ground_truth}, Correct: {is_correct}")

            return {
                "map": data_list[idx]['map'],
                "start": data_list[idx]['start'],
                "end": data_list[idx]['end'],
                "ground_truth": ground_truth,
                "llm_answer": parsed_llm_answer,
                "llm_raw_response": content,
                "is_correct": is_correct
            }

        except Exception as e:
            print(f"Prompt {idx} - Error: {e}")
            return {
                "map": data_list[idx]['map'],
                "start": data_list[idx]['start'],
                "end": data_list[idx]['end'],
                "ground_truth": ground_truth,
                "llm_answer": None,
                "llm_raw_response": None,
                "is_correct": False,
                "error": str(e)
            }


async def main():
    prompts = [
        template.format(map_data=item['map'], start_point=item['start'], end_point=item['end'])
        for item in data_list
    ]
    ground_truths = [item['next_position'] for item in data_list]

    semaphore = asyncio.Semaphore(10)  

    async with httpx.AsyncClient() as client:
        tasks = [
            fetch_response(client, idx, prompts[idx], ground_truths[idx], semaphore)
            for idx in range(len(prompts))
        ]
        results = await asyncio.gather(*tasks)

    # 写入到jsonl文件
    with open(output_path, 'w', encoding='utf-8') as f:
        for item in results:
            f.write(json.dumps(item, ensure_ascii=False) + '\n')

    correct = sum(1 for item in results if item['is_correct'])
    print(f"Correct answers: {correct}/{len(results)}")
    print(f"Output saved to {output_path}")


if __name__ == "__main__":
    asyncio.run(main())
