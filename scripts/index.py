import contextlib
import requests
import os

import gradio as gr
from modules import scripts
from modules import script_callbacks
from modules import shared

def on_ui_settings():
    section = ('template', "Template")
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

global_send_pushover_checkbox_txt2txt = gr.Checkbox(
    label='Send Pushover Notification',
    value=False,
    elem_id='pushover_send_notification_txt2img'
)
global_send_pushover_checkbox_txt2img = gr.Checkbox(
    label='Send Pushover Notification',
    value=False,
    elem_id='pushover_send_notification_img2img'
)

def on_after_component(component, **_kwargs):
    global global_send_pushover_checkbox
    if getattr(component, 'elem_id', None) == 'txt2img_enable_hr':
        global_send_pushover_checkbox_txt2txt.render()
    if getattr(component, 'elem_id', None) == 'img2img_tiling':
        global_send_pushover_checkbox_txt2img.render()

script_callbacks.on_after_component(on_after_component)
script_callbacks.on_ui_settings(on_ui_settings)

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

    if response.status_code == 200:
        print("Notification sent successfully.")
    else:
        print(f"Failed to send notification. Status code: {response.status_code}")


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
        # print(processed.js())
        send_notification = args[0]
        pushover_app_token = shared.opts.data.get("pushover_app_token", "")
        pushover_user_token = shared.opts.data.get("pushover_user_token", "")
        if send_notification and pushover_app_token != "" and pushover_user_token != "":
            send_pushover_notification(
                token=pushover_app_token, 
                user=pushover_user_token, 
                message="Stable Diffusion Run Complete"
            )