#!/usr/bin/env python
# Handler for RunPod Serverless Legato Music Transcription

import os
import runpod
import torch
from PIL import Image
import base64
import io
from legato.models import LegatoModel
from transformers import AutoProcessor


# Device configuration
DEVICE = os.environ.get("DEVICE", "cuda" if torch.cuda.is_available() else "cpu")

# Generation parameters
BEAM_SIZE = int(os.environ.get("BEAM_SIZE", "10"))
FP16 = os.environ.get("FP16", "true").lower() == "true"
# =====================================

print("RunPod Legato Handler initialized")
print(f"Device: {DEVICE}")
print(f"Beam size: {BEAM_SIZE}")
print(f"FP16: {FP16}")

MODEL_PATH = os.environ.get("MODEL_PATH", "guangyangmusic/legato")
model = LegatoModel.from_pretrained(MODEL_PATH, local_files_only=True)
model = model.to(device="cuda")
model = model.half()
processor = AutoProcessor.from_pretrained(MODEL_PATH, local_files_only=True)


def run_inference_on_image(
    image_data,
):
    """Run inference on a single image using the imported function"""
    try:
        from inference import run_inference_on_images

        print(f"Running inference on image: {image_data}")
        abc_outputs = run_inference_on_images(
            images=[image_data],
            model=model,
            processor=processor,
            device=DEVICE,
            beam_size=BEAM_SIZE,
            fp16=FP16,
            batch_size=1,
            output_path=None,
        )

        print("✅ Inference completed.")

        if abc_outputs and len(abc_outputs) > 0:
            return {"abc_transcription": abc_outputs}
        else:
            return {"error": "No transcription generated"}

    except Exception as e:
        import traceback

        traceback_str = traceback.format_exc()
        return {
            "error": f"Error processing image: {str(e)}",
            "traceback": traceback_str,
        }


def get_image_data(image_input):
    if isinstance(image_input, str) and image_input.startswith("data:image"):
        base64_data = image_input.split(",")[1]
        return Image.open(io.BytesIO(base64.b64decode(base64_data)))
    else:
        raise ValueError(
            "Invalid image format. Please provide a base64 encoded image or file path."
        )


def handler(job):
    """
    This is the handler function that will be called by the serverless worker.
    Job input format:
    {
        "image": "base64 encoded image or URL",
    }
    """

    job_input = job["input"]
    print("📥 Job input:", job_input)

    image_data = None
    image = job_input.get("image")
    if image:
        image_data = get_image_data(image)
    else:
        return {"error": "No image provided in input"}

    try:
        return run_inference_on_image(image_data)
    except Exception as e:
        import traceback

        error_trace = traceback.format_exc()
        return {"error": f"Error processing image: {str(e)}", "traceback": error_trace}


runpod.serverless.start({"handler": handler})
