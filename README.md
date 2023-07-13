# sd-webui-pushover

Adds Pushover notifications to [Stable Diffusion WebUI](https://github.com/AUTOMATIC1111/stable-diffusion-webui).

A checkbox will be added to the txt2img and img2img screens that, when ticked, will send a notification when generation fully completes. Failures will log to the console.

## Installation

In Stable Diffusion WebUI, go to the **Extensions**, then **Install from url**. Copy the URL of this GitHub repo into the input and **click install**.

The UI should reload and in the **Settings** tab you should find a **Pushover** section on the left. Here is where you provide your keys and message templates.

## Templating

The title and message can be templated by specifying tokens in `{braces}`.

The following tokens are available.

- prompt
- negative_prompt
- seed
- width
- height
- sampler_name
- cfg_scale
- steps
- batch_size
- sd_model_hash
- job_timestamp
- time_taken

For example a message of "Run {seed} complete in {time_taken}" will be sent as "Run 3252755492 complete in 28 seconds"