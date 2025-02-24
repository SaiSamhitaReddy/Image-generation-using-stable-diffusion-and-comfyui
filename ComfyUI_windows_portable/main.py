import gradio as gr
import json
from websockets_api import get_prompt_images
import uuid
from settings import SERVER_ADDRESS

server_address = SERVER_ADDRESS
client_id = str(uuid.uuid4())

def process(positive):
    with open("workflow_api.json","r",encoding="utf-8") as f:
        prompt = json.load(f)
    
    prompt["6"]["inputs"]["text"] = "a half portrait of a "+ positive + "highly detail, high resolution"
    images = get_prompt_images(prompt,server_address, client_id)
    return images


demo = gr.Interface(
    fn = process,
    inputs = [gr.Textbox(label = "Positive prompt: ")],
    outputs = [gr.Gallery(label = 'Outputs: ')]
)


demo.queue()
demo.launch()