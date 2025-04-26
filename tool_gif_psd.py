from PIL import Image
import psd_tools
import os

# This script operates on a multi-layered PSD file and transforms it into a GIF.

# This was created to allow easy editing of a GIF (via Photoshop).
# And then to easily export the edits as a GIF afterwards

# Configuration variables
INPUT_PSD = r"C:\Users\qtran\Desktop\blythe_sprint\jogging_NewArmor_wip2.psd"  # Replace with your PSD file path
FRAME_DURATION = 50  # Duration per frame in milliseconds
STRIP_BACKGROUND = False  # If True, makes background transparent based on top-left pixel

def create_animated_gif():
    # Load PSD file
    try:
        psd = psd_tools.PSDImage.open(INPUT_PSD)
    except Exception as e:
        print(f"Error opening PSD file: {e}")
        return

    # Prepare frames, reversing layer order (topmost layer first)
    frames = []
    for layer in reversed(psd):  # Reverse to process topmost layer first
        if not layer.is_visible():
            continue
            
        # Convert layer to PIL Image
        layer_image = layer.composite()
        
        if STRIP_BACKGROUND:
            # Get background color from top-left pixel
            bg_color = layer_image.getpixel((0, 0))
            
            # Create a new image with transparent background
            transparent = Image.new('RGBA', layer_image.size, (0, 0, 0, 0))
            pixels = layer_image.convert('RGBA').load()
            width, height = layer_image.size
            
            for y in range(height):
                for x in range(width):
                    if pixels[x, y][:3] != bg_color[:3]:  # Compare RGB, ignore alpha
                        transparent.putpixel((x, y), pixels[x, y])
            
            layer_image = transparent
        
        frames.append(layer_image)

    if not frames:
        print("No visible layers found in PSD file")
        return

    # Get the base filename from INPUT_PSD and create output path
    base_name = os.path.splitext(os.path.basename(INPUT_PSD))[0]  # Extract filename without extension
    desktop = os.path.expanduser("~/Desktop")
    output_path = os.path.join(desktop, f"{base_name}.gif")
    
    try:
        # Save the GIF
        frames[0].save(
            output_path,
            save_all=True,
            append_images=frames[1:],
            duration=FRAME_DURATION,
            loop=0,  # 0 means loop forever
            transparency=0 if STRIP_BACKGROUND else None,
            disposal=2  # Clear frame before next one
        )
        print(f"Animated GIF saved to {output_path}")
    except Exception as e:
        print(f"Error saving GIF: {e}")

if __name__ == "__main__":
    create_animated_gif()