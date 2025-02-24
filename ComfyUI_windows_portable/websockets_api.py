import urllib.parse
import urllib.request
import uuid
import json
import websocket
import io
from PIL import Image

from settings import SERVER_ADDRESS

server_address = SERVER_ADDRESS
client_id = str(uuid.uuid4())


def queue_prompt(prompt):
    p= {"prompt":prompt, "client_id":client_id}
    data = json.dumps(p).encode("utf-8")
    req = urllib.request.Request("http://{}/prompt".format(server_address),data = data)
    return json.loads(urllib.request.urlopen(req).read())

def get_image(filename, subfolder, folder_type, server_address):
    data = {"filename": filename, "subfolder": subfolder, "type": folder_type}
    url_values = urllib.parse.urlencode(data)
    url = f"http://{server_address}/view?{url_values}"
    
    with urllib.request.urlopen(url) as response:
        return response.read()
    
def get_history(prompt_id, server_address):
    url = f"http://{server_address}/history/{prompt_id}"
    
    with urllib.request.urlopen(url) as response:
        return json.loads(response.read().decode('utf-8'))

def get_images(ws, prompt):
    prompt_id = queue_prompt(prompt)["prompt_id"]  # Ensure prompt_id is extracted correctly
    output_images = []

    while True:
        out = ws.recv()
        if isinstance(out, str):
            message = json.loads(out)                
            if message["type"] == "executing":
                data = message["data"]
                if data["node"] is None and data["prompt_id"] == prompt_id:
                    break
        else:
            continue

    # Fetch history using prompt_id
    history = get_history(prompt_id).get(prompt_id, {})

    # Iterate over the history outputs
    for node_id, node_output in history.get("outputs", {}).items():
        images_output = []
        if "images" in node_output:
            for image in node_output["images"]:
                image_data = get_image(
                    image["filename"], image["subfolder"], image["type"]  # Corrected key from "types" to "type"
                )
                images_output.append(image_data)
        
        output_images.append({node_id: images_output})  # Append node-specific images

    return output_images

def get_prompt_images(prompt, server_address, client_id):
    ws = websocket.WebSocket()
    
    try:
        # Fix WebSocket URL formatting
        ws.connect("ws://{}/ws?client_id={}".format(server_address, client_id))
        
        # Fetch images from WebSocket
        images = get_images(ws, prompt)
        outputs = []

        # Process received images
        for node_id, image_list in images.items():
            for image_data in image_list:
                image = Image.open(io.BytesIO(image_data))
                outputs.append(image)
    finally:
        ws.close()  

    return outputs
