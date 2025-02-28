from flask import Flask, render_template, request, jsonify
import base64
import io
from PIL import Image, ImageDraw, ImageFont

app = Flask(__name__)

def apply_polaroid_effect(image_data, filter_type="soft_pink", position=None):
    image = Image.open(io.BytesIO(base64.b64decode(image_data)))

    width, height = image.size
    new_width = int(width * 1.1)
    new_height = int(height * 1.3)

    polaroid = Image.new("RGB", (new_width, new_height), "white")
    polaroid.paste(image, ((new_width - width) // 2, (new_height - height) // 3))

    pastel_filters = {
        "soft_pink": (255, 192, 203),
        "light_blue": (173, 216, 230),
        "mint_green": (152, 251, 152),
        "warm_peach": (255, 218, 185)
    }

    if filter_type in pastel_filters:
        overlay = Image.new("RGB", polaroid.size, pastel_filters[filter_type])
        polaroid = Image.blend(polaroid, overlay, 0.2)

    draw = ImageDraw.Draw(polaroid)
    text = "Korean Booth 2025"

    try:
        font = ImageFont.truetype("arial.ttf", 20)
    except IOError:
        font = ImageFont.load_default()

    text_x, text_y = polaroid.size[0] // 2, polaroid.size[1] - 30
    draw.text((text_x, text_y), text, fill="black", font=font, anchor="mm")

    # Overlay stickers on the first and third images
    if filter_type == "sticker_effect":
        if position == 0:
            sticker = Image.open("images/1.png").convert("RGBA")  # Sticker for first photo
            sticker_size = (width // 2, height // 2)  # Make the sticker bigger
            sticker_position = (10, 10)  # Top-left
        elif position == 2:
            sticker = Image.open("images/2.png").convert("RGBA")  # Sticker for third photo
            sticker_size = (width // 2, height // 2)  # Make the sticker bigger
            sticker_position = (new_width - sticker_size[0] - 10, 10)  # Move to top-right
        else:
            sticker = None
        
        if sticker:
            sticker = sticker.resize(sticker_size)  # Resize sticker
            polaroid.paste(sticker, sticker_position, sticker)  # Place sticker

    return polaroid

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/capture_sequence", methods=["POST"])
def capture_sequence():
    images = request.json["images"]
    filter_type = request.json.get("filter", "soft_pink")

    processed_images = []
    for i, img in enumerate(images):
        image_data = img.split(",")[1]
        processed_image = apply_polaroid_effect(image_data, filter_type, i)

        output_buffer = io.BytesIO()
        processed_image.save(output_buffer, format="PNG")
        encoded_image = base64.b64encode(output_buffer.getvalue()).decode("utf-8")

        processed_images.append("data:image/png;base64," + encoded_image)

    return jsonify({"images": processed_images})

if __name__ == "__main__":
    app.run(debug=True)
