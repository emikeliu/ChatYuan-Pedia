from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List
import json
import datetime
from bs4 import BeautifulSoup
import time
from transformers import T5Tokenizer, T5ForConditionalGeneration, pipeline, AutoTokenizer, AutoModelForTokenClassification
import torch
import re
import argparse
import uvicorn
drv = None
args = {}
browser = False
if __name__ == "__main__" :
    uvicorn.run("NewYuan:app")
    exit(0)
parser = argparse.ArgumentParser()
group = parser.add_mutually_exclusive_group()
group.add_argument("-F", "--firefox", help="使用 Firefox 来爬取百度百科", action="store_true")
group.add_argument("-C", "--chromium", help="使用 Chromium 来爬取百度百科", action="store_true")
group.add_argument("-E", "--edge", help="使用 Edge 来爬取百度百科", action="store_true")
group.add_argument("-R", "--requests", help="使用 requests 来爬取百度百科", action="store_true")
args = parser.parse_args()

if args.firefox:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    drv = webdriver.Firefox()
    browser = True
elif args.chromium:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    drv = webdriver.Chrome()
    browser = True
elif args.edge:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    drv = webdriver.ChromiumEdge()
    browser = True
class Content(BaseModel):
    content: str
    role: str

class PostData(BaseModel):
    prompt: str
    temperature: float
    top_p: float
    max_length: int
    history: List[Content]
    pedia: bool
    sample: bool


xlm_model = None
xlm_tokenizer = None
classifier = None
model = None
tokenizer = None
device = None


print("Loading models please wait... Attention: This may take a long time")
print("T5Tokenizer")
tokenizer = T5Tokenizer.from_pretrained("ClueAI/ChatYuan-large-v2", local_files_only=False)
print("T5ForConditionalGeneration")
model = T5ForConditionalGeneration.from_pretrained("ClueAI/ChatYuan-large-v2", local_files_only=False)
print("BERTaTokenizer")
xlm_tokenizer = AutoTokenizer.from_pretrained("xlm-roberta-large-finetuned-conll03-english")
print("BERTa")
xlm_model = AutoModelForTokenClassification.from_pretrained("xlm-roberta-large-finetuned-conll03-english")
classifier = pipeline("token-classification", model=xlm_model, tokenizer=xlm_tokenizer, aggregation_strategy="simple")
print("Model Loaded")

app = FastAPI()
app.mount("/static", StaticFiles(directory="static/static", html=True), name="static")

@app.post('/api/chat_stream')
def api_chat_stream(data: PostData):
    global browser
    ret = []
    prompt = data.prompt
    if prompt == None:
        prompt=""
    max_length = data.max_length
    if max_length is None:
        max_length = 2048
    top_p = data.top_p
    if top_p is None:
        top_p = 0.7
    temperature = data.temperature
    if temperature is None:
        temperature = 0.9
    use_pedia = data.pedia
    history = data.history
    history_formatted = ""
    if history is not None:
        tmp = []
        for i, old_chat in enumerate(history):
            if len(tmp) == 0 and old_chat.role == "user":
                history_formatted=history_formatted+("用户："+old_chat.content+"\n")
            elif old_chat.role == "AI":
                history_formatted=history_formatted+("小元："+old_chat.content+"\n")
            else:
                continue
    response=history_formatted

    footer = ''
    if use_pedia:
        keywords = classifier(prompt)
        print(keywords)
        response_d = []
        for i in keywords:
            if not browser:
                import requests
                ff = requests.get("https://baike.baidu.com/item/{}".format(i['word']),headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36 Edg/83.0.478.50','Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9'})
                soup = BeautifulSoup(ff.text)
                dest = soup.find_all(class_="lemma-summary")
                dest = list(map(lambda x: x.get_text(), dest))
            else:
                drv.get("https://baike.baidu.com/item/{}".format(i['word']))
                result = drv.find_element(By.CLASS_NAME,"lemma-summary")
                dest = [result.text]
            if len(dest)>0:
                response_d.append(re.sub(r"\[[0-9]*-[0-9]*\]","",re.sub(r"\[[0-9]*\]","",dest[0])))
        output_sources = ['{}. [百度百科-{}]({})'.format(i+1,keywords[i]['word'],"https://baike.baidu.com/item/{}".format(keywords[i]['word'])) for i in range(len(response_d))]
        results ='\n'.join([i for i in response_d])
        if(len(response_d) != 0):
            prompt =  results+'\n'+prompt
            footer =  "\n来源：\n"+('\n').join(output_sources)
    try:
        input_text = response + "\n用户：" + prompt + "\n小元："
        print(input_text)
        response = answer(input_text,sample=data.sample)
    except Exception as e:
        # pass
        print("错误",str(e),e)
    ret.append(response)
    if footer != '':
        ret.append(footer)
    return ret

user_data=['模型加载中','','']
@app.get('/api/chat_now')
def api_chat_now():
    return '当前用户：'+user_data[0]+"\n问题："+user_data[1]+"\n回答："+user_data[2]+''

@app.get('/')
def index() -> FileResponse:
    return FileResponse(path="./static/index.html", media_type="text/html")


def preprocess(text):
  text = text.replace("\n", "\\n").replace("\t", "\\t")
  return text

def postprocess(text):
  return text.replace("\\n", "\n").replace("\\t", "\t").replace('%20','  ')

def answer(text, sample=True, top_p=1, temperature=0.7):
  text = preprocess(text)
  encoding = tokenizer(text=[text], truncation=True, padding=True, max_length=8192, return_tensors="pt").to(device)
  if not sample:
    out = model.generate(**encoding, return_dict_in_generate=True, output_scores=False, max_new_tokens=8192, num_beams=1, length_penalty=0.6)
  else:
    out = model.generate(**encoding, return_dict_in_generate=True, output_scores=False, max_new_tokens=8192, do_sample=True, top_p=top_p, temperature=temperature, no_repeat_ngram_size=12)
  out_text = tokenizer.batch_decode(out["sequences"], skip_special_tokens=True)
  return postprocess(out_text[0])


