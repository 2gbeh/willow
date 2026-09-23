import base64
import io
import os
import runpod
import torch
from diffusers import FluxPipeline
from dotenv import load_dotenv

load_dotenv()

DEFAULT_WIDTH = 512
DEFAULT_HEIGHT = 512
DEFAULT_STEPS = 28

MODEL_ID = "black-forest-labs/FLUX.1-dev"

pipeline = None

def load_model():
    global pipeline
    if pipeline is None:
        hf_token = os.environ.get("HF_TOKEN")
        if not hf_token:
            raise RuntimeError("Missing HF_TOKEN env var")
        
        pipeline = FluxPipeline.from_pretrained(
            MODEL_ID,
            torch_dtype=torch.bfloat16,
            token=hf_token
        )

        pipeline.to("cuda")
        pipeline.enable_model_cpu_offload()
    return pipeline

def validate_input(job_input: dict) -> tuple[dict | None, str | None]:
    if job_input is None:
        return None, "Request 'input' is required"

    prompt = job_input.get("prompt")
    if not prompt or not isinstance(prompt, str):
        return None, "Request 'prompt' is required"

    width = job_input.get("width", DEFAULT_WIDTH)
    height = job_input.get("height", DEFAULT_HEIGHT)
    steps = job_input.get("num_inference_steps", DEFAULT_STEPS)

    for name, value in (("width", width), ("height", height), ("num_inference_steps", steps)):
        if not isinstance(value, int) or value <= 0:
            return None, f"'{name}' must be a positive integer."

    return {
        "prompt": prompt,
        "width": width,
        "height": height,
        "num_inference_steps": steps,
    }, None

def run_inference(pipe, validated: dict) -> str:
    result = pipe(
        prompt=validated["prompt"],
        width=validated["width"],
        height=validated["height"],
        num_inference_steps=validated["num_inference_steps"],
    )
    image = result.images[0]
 
    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    return base64.b64encode(buffer.getvalue()).decode("utf-8")

def build_error(message: str, error_type: str) -> dict:
    return {"error": message, "error_type": error_type}

def handler(job):
    job_input = job.get("input")

    validated, error = validate_input(job_input)
    if error or validated is None:
        return build_error(error or "Invalid input.", "validation_error")

    try:
        pipe = load_model()
    except Exception as e:
        return build_error(f"Model load failed: {e}", "model_load_error")
    
    try:
        image_b64 = run_inference(pipe, validated)
    except torch.cuda.OutOfMemoryError:
        torch.cuda.empty_cache()
        return build_error(
            "GPU ran out of memory. Try a smaller width/height.", "oom_error"
        )
    except Exception as e:
        return build_error(f"Inference failed: {e}", "inference_error")
 
    return {"image": image_b64}


if __name__ == '__main__':
    runpod.serverless.start({'handler': handler })
