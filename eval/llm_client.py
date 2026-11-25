#不知道自己在干什么———— 它只负责发送请求、接收返回结果
import os

import requests

#带默认值的参数必须排在没默认值的参数后面
#类型注解不会检查你传的是不是真的列表
API_URL="https://api.deepseek.com/chat/completions"
def chat(messages:list[dict],model:str="deepseek-chat",
         temperature=0.3, api_key:str|None = None,api_url: str = API_URL) -> str:
    if api_key is None:
        api_key=os.getenv("LLM_API_KEY")
        if not api_key:
            raise ValueError("LLM_API_KEY 未设置")

    headers={"Authorization":f"Bearer {api_key}",
             "Content-Type":"application/json"}
    payload={
        "model":model,
        "messages":messages,
        "temperature":temperature
        }

    resp=requests.post(api_url,headers=headers,json=payload,timeout=30)
    resp.raise_for_status()
    return resp.json()["choices"][0]["message"]["content"]

if __name__=="__main__":
    print(chat([{"role":"user","content":"1+1=?"}]))