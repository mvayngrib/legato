#!/usr/bin/env python
# Image processing utilities for RunPod Legato Handler

from PIL import Image
import base64
import io


def process_image_input(image_input):
    """Process image input in various formats (base64, file path) and return PIL Image object"""
    try:
        # Case 1: Base64 encoded image
        if isinstance(image_input, str) and image_input.startswith("data:image"):
            # Extract base64 part after the comma
            base64_data = image_input.split(",")[1]
            image_data = Image.open(io.BytesIO(base64.b64decode(base64_data)))

        # Case 2: Pure base64 string (without data URI prefix)
        elif isinstance(image_input, str) and len(image_input) > 100:
            try:
                image_data = Image.open(io.BytesIO(base64.b64decode(image_input)))
            except Exception:
                # If not a valid base64, assume it's a file path
                image_data = Image.open(image_input)

        # Case 3: Local file path
        elif isinstance(image_input, str):
            # Assume it's a file path
            image_data = Image.open(image_input)

        else:
            raise ValueError(
                "Invalid image format. Please provide a base64 encoded image or file path."
            )

        # Convert to RGB mode to ensure compatibility
        image_data = image_data.convert("RGB")
        return image_data

    except Exception as e:
        raise ValueError(f"Error processing image: {str(e)}")


def image_to_base64(image, format="PNG"):
    """Convert a PIL Image to base64 string"""
    buffer = io.BytesIO()
    image.save(buffer, format=format)
    return base64.b64encode(buffer.getvalue()).decode()


def image_to_data_uri(image, format="PNG"):
    """Convert a PIL Image to data URI format"""
    base64_str = image_to_base64(image, format)
    return f"data:image/{format.lower()};base64,{base64_str}"
