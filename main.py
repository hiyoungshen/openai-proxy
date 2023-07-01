import os
import yaml
import requests
from flask import Flask, request, Response, make_response
import time
import re
import logging

app = Flask(__name__)

# 设置app.log输出文件
app.logger.handlers = []
file_handler = logging.FileHandler("log/app.log")
app.logger.addHandler(file_handler)
app.logger.setLevel(logging.INFO)

# 从配置文件config/config.yaml中载入一些用clear户的配置
config = yaml.load(open("config/config.yaml", "r"), Loader=yaml.FullLoader)
OPENAI_API_URL = config["OPENAI_API_URL"]
GPT3_5_04K = config["PRICE"]["GPT3_5_04K"]
GPT3_5_16K = config["PRICE"]["GPT3_5_16K"]
GPT4_0_16K = config["PRICE"]["GPT4_0_16K"]
GPT4_0_32K = config["PRICE"]["GPT4_0_32K"]

@app.route("/alluseage", methods=["GET"])
def get_alluseage():
    
    # 检查是否是授权的用户
    OPENAI_API_KEY = request.headers.get("Authorization", "")
    if OPENAI_API_KEY == "":
        return "Unauthorized User 1"
    
    # 获取授权用户的OPENAI_API_KEY
    OPENAI_API_KEY = OPENAI_API_KEY.strip().split(' ')[-1]
    # app.logger.info(f"OPENAI_API_KEY: {OPENAI_API_KEY}")
    for user in config["USERS"]:
        if user["OPENAI_API_KEY"] == OPENAI_API_KEY: # 是授权的用户
            total_prompt_tokens_3_5_04k, total_comple_tokens_3_5_04k = 0, 0
            total_prompt_tokens_3_5_16k, total_comple_tokens_3_5_16k = 0, 0
            total_prompt_tokens_4_0_16k, total_comple_tokens_4_0_16k = 0, 0
            total_prompt_tokens_4_0_32k, total_comple_tokens_4_0_32k = 0, 0
            with open(f"./log/usage.log", "r") as log_file:
                lines = log_file.readlines()
            for line in lines:
                model_name = re.search(r"\|\sModel:\s(.+?)\s\|", line)
                prompt_tokens = re.search(r"Prompt Tokens: (\d+)", line)
                comple_tokens = re.search(r"Completion Tokens: (\d+)", line)
                
                if model_name:
                    model_name = model_name.group(1)
                else:
                    raise Exception("Model Name Not Found")
                if prompt_tokens:
                    prompt_tokens = int(prompt_tokens.group(1))
                else:
                    raise Exception("Prompt Tokens Not Found")
                if comple_tokens:
                    comple_tokens = int(comple_tokens.group(1))
                else:
                    raise Exception("Completion Tokens Not Found")
                
                if "gpt-3.5" in model_name and "16k" not in model_name:
                    total_prompt_tokens_3_5_04k += prompt_tokens
                    total_comple_tokens_3_5_04k += comple_tokens
                elif "gpt-3.5" in model_name and "16k" in model_name:
                    total_prompt_tokens_3_5_16k += prompt_tokens
                    total_comple_tokens_3_5_16k += comple_tokens
                elif "gpt-4" in model_name and "32k" not in model_name:
                    total_prompt_tokens_4_0_16k += prompt_tokens
                    total_comple_tokens_4_0_16k += comple_tokens
                elif "gpt-4" in model_name and "32k" in model_name:
                    total_prompt_tokens_4_0_32k += prompt_tokens
                    total_comple_tokens_4_0_32k += comple_tokens
                else:
                    raise Exception("Model Name Not Found in GPT 3.5 or GPT 4")
            
            price_3_5_04k = (total_prompt_tokens_3_5_04k+total_comple_tokens_3_5_04k)/1000*GPT3_5_04K
            price_3_5_16k = (total_prompt_tokens_3_5_16k+total_comple_tokens_3_5_16k)/1000*GPT3_5_16K
            price_4_0_16k = (total_prompt_tokens_4_0_16k+total_comple_tokens_4_0_16k)/1000*GPT4_0_16K
            price_4_0_32k = (total_prompt_tokens_4_0_32k+total_comple_tokens_4_0_32k)/1000*GPT4_0_32K
            price_total = price_3_5_04k + price_3_5_16k + price_4_0_16k + price_4_0_32k
            summary = \
              f"Total Prompt Token of GPT 3.5 04k Used: {total_prompt_tokens_3_5_04k}<br>\
                Total Comple Token of GPT 3.5 04k Used: {total_comple_tokens_3_5_04k}<br>\
                Total Cost: ${price_3_5_04k}<br>\
                \
                Total Prompt Token of GPT 3.5 16k Used: {total_prompt_tokens_3_5_16k}<br>\
                Total Comple Token of GPT 3.5 16k Used: {total_comple_tokens_3_5_16k}<br>\
                Total Cost: ${price_3_5_16k}<br>\
                \
                Total Prompt Token of GPT 4.0 16k Used: {total_prompt_tokens_4_0_16k}<br>\
                Total Comple Token of GPT 4.0 16k Used: {total_comple_tokens_4_0_16k}<br>\
                Total Cost: ${price_4_0_16k}<br>\
                \
                Total Prompt Token of GPT 4.0 16k Used: {total_prompt_tokens_4_0_32k}<br>\
                Total Comple Token of GPT 4.0 32k Used: {total_comple_tokens_4_0_32k}<br>\
                Total Cost: ${price_4_0_32k}<br>\
                \
                TOTAL COST: ${price_total}<br>\
                <br>\
                "
            log_content = summary + "<br>".join(lines)
            return log_content
    return "Unauthorized User 2"

@app.route("/singleuseage", methods=["GET"])
def get_singleuseage():
    
    # 检查是否是授权的用户
    OPENAI_API_KEY = request.headers.get("Authorization", "")
    if OPENAI_API_KEY == "":
        return "Unauthorized 1"
    
    # 获取授权用户的OPENAI_API_KEY
    OPENAI_API_KEY = OPENAI_API_KEY.strip().split(' ')[-1]
    # app.logger.info(f"OPENAI_API_KEY: {OPENAI_API_KEY}")
    for user in config["USERS"]:
        if user["OPENAI_API_KEY"] == OPENAI_API_KEY: # 是授权的用户
            total_prompt_tokens_3_5_04k, total_comple_tokens_3_5_04k = 0, 0
            total_prompt_tokens_3_5_16k, total_comple_tokens_3_5_16k = 0, 0
            total_prompt_tokens_4_0_16k, total_comple_tokens_4_0_16k = 0, 0
            total_prompt_tokens_4_0_32k, total_comple_tokens_4_0_32k = 0, 0
            with open(f"./log/usage.log", "r") as log_file:
                lines = log_file.readlines()
            
            records = []
            for line in lines:
                openai_api_key = re.search(r'\|\sOPENAI_API_KEY:\s([\w\-]+?)\s\|', line)
                if openai_api_key:
                    openai_api_key = openai_api_key.group(1)
                    if openai_api_key != OPENAI_API_KEY:
                        continue
                else:
                    raise Exception("OPENAI_API_KEY Not Found")
                records.append(line)
                model_name = re.search(r"\|\sModel:\s(.+?)\s\|", line)
                prompt_tokens = re.search(r"Prompt Tokens: (\d+)", line)
                comple_tokens = re.search(r"Completion Tokens: (\d+)", line)
                
                if model_name:
                    model_name = model_name.group(1)
                else:
                    raise Exception("Model Name Not Found")
                if prompt_tokens:
                    prompt_tokens = int(prompt_tokens.group(1))
                else:
                    raise Exception("Prompt Tokens Not Found")
                if comple_tokens:
                    comple_tokens = int(comple_tokens.group(1))
                else:
                    raise Exception("Completion Tokens Not Found")
                
                if "gpt-3.5" in model_name and "16k" not in model_name:
                    total_prompt_tokens_3_5_04k += prompt_tokens
                    total_comple_tokens_3_5_04k += comple_tokens
                elif "gpt-3.5" in model_name and "16k" in model_name:
                    total_prompt_tokens_3_5_16k += prompt_tokens
                    total_comple_tokens_3_5_16k += comple_tokens
                elif "gpt-4" in model_name and "32k" not in model_name:
                    total_prompt_tokens_4_0_16k += prompt_tokens
                    total_comple_tokens_4_0_16k += comple_tokens
                elif "gpt-4" in model_name and "32k" in model_name:
                    total_prompt_tokens_4_0_32k += prompt_tokens
                    total_comple_tokens_4_0_32k += comple_tokens
                else:
                    raise Exception("Model Name Not Found in GPT 3.5 or GPT 4")
                
            price_3_5_04k = (total_prompt_tokens_3_5_04k+total_comple_tokens_3_5_04k)/1000*GPT3_5_04K
            price_3_5_16k = (total_prompt_tokens_3_5_16k+total_comple_tokens_3_5_16k)/1000*GPT3_5_16K
            price_4_0_16k = (total_prompt_tokens_4_0_16k+total_comple_tokens_4_0_16k)/1000*GPT4_0_16K
            price_4_0_32k = (total_prompt_tokens_4_0_32k+total_comple_tokens_4_0_32k)/1000*GPT4_0_32K
            price_total = price_3_5_04k + price_3_5_16k + price_4_0_16k + price_4_0_32k
            summary = \
              f"Total Prompt Token of GPT 3.5 04k Used: {total_prompt_tokens_3_5_04k}<br>\
                Total Comple Token of GPT 3.5 04k Used: {total_comple_tokens_3_5_04k}<br>\
                Total Cost: ${price_3_5_04k}<br>\
                \
                Total Prompt Token of GPT 3.5 16k Used: {total_prompt_tokens_3_5_16k}<br>\
                Total Comple Token of GPT 3.5 16k Used: {total_comple_tokens_3_5_16k}<br>\
                Total Cost: ${price_3_5_16k}<br>\
                \
                Total Prompt Token of GPT 4.0 16k Used: {total_prompt_tokens_4_0_16k}<br>\
                Total Comple Token of GPT 4.0 16k Used: {total_comple_tokens_4_0_16k}<br>\
                Total Cost: ${price_4_0_16k}<br>\
                \
                Total Prompt Token of GPT 4.0 16k Used: {total_prompt_tokens_4_0_32k}<br>\
                Total Comple Token of GPT 4.0 32k Used: {total_comple_tokens_4_0_32k}<br>\
                Total Cost: ${price_4_0_32k}<br>\
                \
                TOTAL COST: ${price_total}<br>\
                <br>\
                "
            log_content = summary + "<br>".join(records)
            return log_content
    return "Unauthorized 2"

@app.route("/v1/chat/completions", methods=["POST"])
def mchat_proxy():
    app.logger.info(f"{time.strftime('%Y-%m-%d %H:%M:%S')}")
    OPENAI_API_KEY = request.headers.get("Authorization").split(' ')[-1]
    headers = {}
    for key, value in request.headers.items(): 
        if key in ["Host"]:
            continue
        headers[key] = value
    response = requests.post(OPENAI_API_URL, headers=headers, json=request.get_json())
    # app.logger.info(f"Response: {type(response)}")

    json_response = response.json()
    if response.status_code == 200:
        model = json_response.get("model", "")
        usage = json_response.get("usage", {})
        prompt_tokens = usage.get("prompt_tokens", 0)
        completion_tokens = usage.get("completion_tokens", 0)
        total_tokens = usage.get("total_tokens", 0)
        log_entry = f"{time.strftime('%Y-%m-%d %H:%M:%S')} | OPENAI_API_KEY: {OPENAI_API_KEY} | Model: {model} | Prompt Tokens: {prompt_tokens} | Completion Tokens: {completion_tokens} | Total Tokens: {total_tokens}\n"
        with open(f"./log/usage.log", "a") as log_file:
            log_file.write(log_entry)

    # # 使用 make_response 函数将 requests.models.Response 对象转换为 Flask 的 Response 对象
    # flask_response = make_response(response.content, response.status_code)    
    # app.logger.info(f"Response.content: {response.content}, {response.status_code}")
    # # 复制 requests.models.Response 对象的响应头部到 Flask 的 Response 对象
    # for header, value in response.headers.items():
    #     flask_response.headers[header] = value
    #     app.logger.info(f"Response: {header}, {value}")
    return json_response
    # return flask_response

def start_response(status, headers):
    response = Response(status=status)
    for header_name, header_value in headers:
        response.headers[header_name] = header_value
    return response

def main(request):
    return app.__call__(request.environ, start_response)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")