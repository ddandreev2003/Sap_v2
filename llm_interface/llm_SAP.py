import requests
import json
import re
import ast
from pathlib import Path
import sys

# Добавляем путь к parent директории для импорта sap_fallback
parent_dir = Path(__file__).parent.parent
if str(parent_dir) not in sys.path:
    sys.path.insert(0, str(parent_dir))


def LLM_SAP(prompts_list, llm='GPT', key='', llm_model=None):
    if isinstance(prompts_list, str):
        prompts_list = [prompts_list]
    if llm == 'Zephyr':
        result = LLM_SAP_batch_Zephyr(prompts_list, llm_model)
    elif llm == 'GPT':
        result = LLM_SAP_batch_gpt(prompts_list, key)
    return result

# Load the Zephyr model once and reuse it
def load_Zephyr_pipeline():
    from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
    import torch

    model_id = "HuggingFaceH4/zephyr-7b-beta"

    tokenizer = AutoTokenizer.from_pretrained(model_id)
    model = AutoModelForCausalLM.from_pretrained(
        model_id,
        torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
        device_map="auto"
    )

    # Zephyr prefers specific generation parameters to stay aligned
    pipe = pipeline(
        "text-generation",
        model=model,
        tokenizer=tokenizer,
        return_full_text=False,
        max_new_tokens=512,  # you can tune this
        do_sample=True,
        temperature=0.7,
        top_p=0.9,
        eos_token_id=tokenizer.eos_token_id
    )

    return pipe
    

def LLM_SAP_batch_Zephyr(prompts_list, llm_model):
    print("### run LLM_SAP_batch with zephyr-7b-beta###")

    # Load templates
    with open('llm_interface/template/template_SAP_system_short.txt', 'r') as f:
        template_system = ' '.join(f.readlines())

    with open('llm_interface/template/template_SAP_user.txt', 'r') as f:
        template_user = ' '.join(f.readlines())

    # Load Zephyr
    if llm_model is None:
        pipe = load_Zephyr_pipeline()
    else: 
        pipe = llm_model

    # Process each prompt separately for better reliability with Zephyr
    all_outputs = []
    
    for i, prompt in enumerate(prompts_list):
        print(f"\n🔄 Обработка промта {i+1}/{len(prompts_list)}: '{prompt[:50]}...'")
        
        # Create prompt for single input
        numbered_prompt = f"### Input 1: {prompt}\n### Output:"
        full_prompt = template_system + "\n\n" + template_user + "\n\n" + numbered_prompt
        
        try:
            # Run inference - increased max_new_tokens for more complete output
            output = pipe(
                full_prompt,
                max_new_tokens=512,
                temperature=0.5,  # Reduced temperature for more consistent output
                do_sample=True,
                top_p=0.95,
                return_full_text=False
            )[0]["generated_text"]
            
            print(f"  📝 LLM ответ: {output[:100]}...")
            
            # Parse single output
            try:
                result = get_params_dict_SAP(output)
                if result is not None:
                    all_outputs.append(result)
                    print(f"  ✅ Успешно распарсено")
                else:
                    print(f"  ⚠️  Не удалось распарсить, используется fallback")
                    all_outputs.append(create_fallback_decomposition(prompt))
            except Exception as parse_error:
                print(f"  ⚠️  Ошибка парсинга: {parse_error}")
                print(f"     Используется резервная декомпозиция")
                all_outputs.append(create_fallback_decomposition(prompt))
                
        except Exception as e:
            print(f"  ❌ Ошибка при вызове LLM: {e}")
            print(f"     Используется резервная декомпозиция")
            all_outputs.append(create_fallback_decomposition(prompt))
    
    return all_outputs

def LLM_SAP_batch_gpt(prompts_list, key):
    print("### run LLM_SAP_batch with gpt-4o ###")

    url = "https://api.openai.com/v1/chat/completions"
    api_key = key

    with open('llm_interface/template/template_SAP_system.txt', 'r') as f:
        template_system=f.readlines()
        prompt_system=' '.join(template_system)

    with open('llm_interface/template/template_SAP_user.txt', 'r') as f:
        template_user=f.readlines()
        template_user=' '.join(template_user)

    numbered_prompts = [f"### Input {i + 1}: {p}\n### Output:" for i, p in enumerate(prompts_list)]
    prompt_user = template_user + "\n\n" + "\n\n".join(numbered_prompts)
    payload = json.dumps({
    "model": "gpt-4o", 
    "messages": [
        {
            "role": "system",
            "content": prompt_system
        },
        {
            "role": "user",
            "content": prompt_user
        }
    ]
    })
    headers = {
        'Accept': 'application/json',
        'Authorization': f'Bearer {api_key}',
        'User-Agent': 'Apifox/1.0.0 (https://apifox.com)',
        'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)
    obj=response.json()
    
    text=obj['choices'][0]['message']['content']
    print(f"text: {text}")
    parsed_outputs = parse_batched_llm_output(text, prompts_list)

    return parsed_outputs


def parse_batched_llm_output(llm_output_text, original_prompts):
    """
    llm_output_text: raw string returned by the llm for multiple prompts
    original_prompts: list of the multiple original input strings
    """
    outputs = re.split(r"### Input \d+: ", llm_output_text)
    results = []

    for i in range(len(original_prompts)):
        # Check if we have enough outputs
        if i >= len(outputs):
            print(f"⚠️  Не удалось парсить промт {i+1}: недостаточно сегментов (ожидается {len(original_prompts)}, получено {len(outputs)})")
            # Используем fallback для этого промта
            results.append(create_fallback_decomposition(original_prompts[i]))
            continue
            
        out = outputs[i]
        cleaned = out.strip()
        
        # Skip empty outputs
        if not cleaned:
            print(f"⚠️  Не удалось парсить промт {i+1}: пустой вывод")
            results.append(create_fallback_decomposition(original_prompts[i]))
            continue
            
        try:
            result = get_params_dict_SAP(cleaned)
            if result is None:
                # Если парсинг вернул None, используем fallback
                results.append(create_fallback_decomposition(original_prompts[i]))
            else:
                results.append(result)
        except Exception as e:
            print(f"⚠️  Не удалось парсить промт {i+1}: {e}")
            results.append(create_fallback_decomposition(original_prompts[i]))
    return results


def get_params_dict_SAP(response):
    """
    Parses the LLM output from SAP-style few-shot prompts.
    Cleans up Markdown-style code fences and returns a dict.
    More robust parsing that handles different formats.
    """
    try:
        # Try to extract explanation
        if "a. Explanation:" in response and "b. Final dictionary:" in response:
            explanation = response.split("a. Explanation:")[1].split("b. Final dictionary:")[0].strip()
            dict_block = response.split("b. Final dictionary:")[1].strip()
        elif "Explanation:" in response and "dictionary:" in response:
            # More flexible format
            explanation = response.split("Explanation:")[1].split("dictionary:")[0].strip()
            dict_block = response.split("dictionary:")[1].strip()
        else:
            # If no explanation found, try to extract just the dictionary
            print(f"Warning: Could not find explanation section in response")
            explanation = "Not provided"
            dict_block = response

        # Remove ```python and ``` if present
        dict_str = re.sub(r"```[^\n]*\n?", "", dict_block).replace("```", "").strip()
        
        # Try to find dictionary in the text if direct parsing fails
        if not dict_str.startswith("{"):
            # Look for dictionary pattern
            dict_match = re.search(r"\{.*\}", dict_str, re.DOTALL)
            if dict_match:
                dict_str = dict_match.group(0)
            else:
                raise ValueError("Could not find dictionary pattern in response")

        # Parse dictionary safely
        final_dict = ast.literal_eval(dict_str)

        return {
            "explanation": explanation,
            "prompts_list": final_dict.get("prompts_list", []),
            "switch_prompts_steps": final_dict.get("switch_prompts_steps", [])
        }

    except Exception as e:
        print(f"Parsing failed: {e}")
        print(f"Response snippet: {response[:200]}")
        return None


def create_fallback_decomposition(original_prompt):
    """
    Создает резервную SAP декомпозицию когда LLM не может парсить
    Используется как fallback для Zephyr и других моделей
    """
    try:
        from sap_fallback import create_simple_sap_decomposition
        fallback_result = create_simple_sap_decomposition(original_prompt)
        print(f"  💡 Используется резервная декомпозиция (LLM не смог распарсить ответ)")
        return fallback_result
    except Exception as e:
        print(f"  ⚠️  Fallback также не сработал: {e}")
        # Просто возвращаем исходный промт
        return {
            "explanation": "Fallback: using original prompt as-is (LLM parsing failed)",
            "prompts_list": [original_prompt],
            "switch_prompts_steps": []
        }