import contextlib
import requests
import os
import datetime

import gradio as gr
from modules import scripts
from modules import script_callbacks
from modules import shared

def create_checkbox(el_id):
    return gr.Checkbox(
        label="Send Pushover Notification",
        value=False,
        elem_id="pushover_send_notification_" + el_id
    )

# Create checkboxes for each section
global_send_pushover_checkbox_txt2txt = create_checkbox("txt2txt")
global_send_pushover_checkbox_txt2img = create_checkbox("txt2img")

# Add options to settings
def on_ui_settings():
    section = ("pushover", "Pushover")
    shared.opts.add_option(
        "pushover_app_token",
        shared.OptionInfo(
            "",
            "App Token",
            section=section
        )
    )
    shared.opts.add_option(
        "pushover_user_token",
        shared.OptionInfo(
            "",
            "User Token",
            section=section
        )
    )
    
    shared.opts.add_option(
        "pushover_message_template",
        shared.OptionInfo(
            "Stable Diffusion Run Complete",
            "Message Template",
            section=section
        )
    )
    
    shared.opts.add_option(
        "pushover_title_template",
        shared.OptionInfo(
            "Stable Diffusion",
            "Title Template",
            section=section
        )
    )
    
# Add checkboxes to UI in appropriate places
def on_after_component(component, **_kwargs):
    global global_send_pushover_checkbox
    if getattr(component, "elem_id", None) == "txt2img_enable_hr":
        global_send_pushover_checkbox_txt2txt.render()
    if getattr(component, "elem_id", None) == "img2img_tiling":
        global_send_pushover_checkbox_txt2img.render()

script_callbacks.on_after_component(on_after_component)
script_callbacks.on_ui_settings(on_ui_settings)

# Send pushover notification
def send_pushover_notification(token, user, message, title=None, url=None, url_title=None, priority=0):
    data = {
        "token": token,
        "user": user,
        "message": message,
        "priority": priority
    }

    if title is not None:
        data["title"] = title

    if url is not None:
        data["url"] = url

    if url_title is not None:
        data["url_title"] = url_title

    response = requests.post("https://api.pushover.net/1/messages.json", data=data)

    if response.status_code is not 200:
        print(f"Failed to send notification. Status code: {response.status_code}")

# Construct user friendly time difference string
def time_diff(start, end):
    diff = end - start
    seconds = diff.total_seconds()
    hours, remainder = divmod(seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    result = ""
    if hours > 0:
        result += f"{int(hours)} hour{'s' if hours > 1 else ''}, "
    if minutes > 0:
        result += f"{int(minutes)} minute{'s' if minutes > 1 else ''}, "
    result += f"{int(seconds)} second{'s' if seconds > 1 else ''}"
    return result

# Swap tokens in template
def swap_tokens(template, obj):
    tokens = {
        "prompt": obj.all_prompts[0],
        "negative_prompt": obj.all_negative_prompts[0],
        "seed": obj.seed,
        "width": obj.width,
        "height": obj.height,
        "sampler_name": obj.sampler_name,
        "cfg_scale": obj.cfg_scale,
        "steps": obj.steps,
        "batch_size": obj.batch_size,
        "sd_model_hash": obj.sd_model_hash,
        "job_timestamp": datetime.datetime.strptime(obj.job_timestamp, "%Y%m%d%H%M%S"),
        "time_taken": time_diff(datetime.datetime.strptime(obj.job_timestamp, "%Y%m%d%H%M%S"), datetime.datetime.now())
    }
    for attr, value in tokens.items():
        template = template.replace("{" + attr + "}", str(value))
    return template

class PushoverScript(scripts.Script):
    def __init__(self) -> None:
        super().__init__()

    def ui(self, is_img2img):
        pushover_checkbox = global_send_pushover_checkbox_txt2txt if not is_img2img else global_send_pushover_checkbox_txt2img 
        controls = (pushover_checkbox,)
        return controls

    def title(self):
        return "Pushover"

    def show(self, is_img2img):
        return scripts.AlwaysVisible

    def postprocess(self, p, processed, *args):
        send_notification = args[0] # Populated from ui function
        pushover_app_token = shared.opts.data.get("pushover_app_token", "")
        pushover_user_token = shared.opts.data.get("pushover_user_token", "")
        pushover_message_template = shared.opts.data.get("pushover_message_template", "")
        pushover_title_template = shared.opts.data.get("pushover_title_template", "")
        if send_notification and pushover_app_token != "" and pushover_user_token != "":
            send_pushover_notification(
                token=pushover_app_token, 
                user=pushover_user_token, 
                title=swap_tokens(pushover_title_template, processed),
                message=swap_tokens(pushover_message_template, processed)
            )

