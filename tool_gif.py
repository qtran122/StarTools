from PIL import Image
import os

# This script operates on a folder of PNG files and transforms them into a GIF.

# This was created to revert the effects of Texture Packer. We would take a gif and
# break it into a folder of PNGs for TexturePacker to compile into one big spritesheet.
# Overtime, there was a need to go in the reverse direction, hence this tool.

# Configuration
INPUT_FOLDER = r"C:\Users\qtran\Desktop\blythe_sprint"  # Replace with your folder path
FRAME_DURATION = 60                                          # Duration per frame in milliseconds (lower = faster)
STRIP_BACKGROUND = False                                      # Set to True to make background transparent, False to preserve

# Automatically generate OUTPUT_GIF (desktop path with folder name)
desktop = os.path.join(os.path.expanduser("~"), "Desktop")
folder_name = os.path.basename(INPUT_FOLDER)
OUTPUT_GIF = os.path.join(desktop, f"{folder_name}.gif")

def create_gif(input_folder, output_gif, duration, strip_background):
    """
    Create an animated GIF from PNG files in a folder, with optional background stripping.
    
    Args:
        input_folder (str): Path to folder containing PNG files
        output_gif (str): Path for output GIF file
        duration (int): Duration per frame in milliseconds
        strip_background (bool): If True, make background transparent; if False, preserve original
    """
    # Get list of PNG files
    files = [f for f in os.listdir(input_folder) if f.endswith('.png')]
    
    # Sort files numerically based on the number in parentheses
    files.sort(key=lambda x: int(x.strip('().png')))
    
    # Open images
    images = []
    for file in files:
        file_path = os.path.join(input_folder, file)
        img = Image.open(file_path)
        
        if strip_background:
            # Convert to RGBA and make background transparent
            if img.mode != 'RGBA':
                img = img.convert('RGBA')
            # Assume the background is the color of the top-left pixel
            bg_color = img.getpixel((0, 0))
            data = img.getdata()
            new_data = []
            for item in data:
                # Replace background color with transparent
                if item[:3] == bg_color[:3]:
                    new_data.append((0, 0, 0, 0))
                else:
                    new_data.append(item)
            img.putdata(new_data)
        else:
            # Preserve original image data
            if img.mode != 'RGBA':
                img = img.convert('RGBA')  # Still convert to RGBA for GIF compatibility
            
        images.append(img)
    
    if not images:
        print("No PNG files found in the folder!")
        return
    
    # Save GIF
    save_kwargs = {
        'save_all': True,
        'append_images': images[1:],
        'duration': duration,
        'loop': 0,  # 0 means loop forever
    }
    
    if strip_background:
        save_kwargs['transparency'] = 0
        save_kwargs['disposal'] = 2  # Maintain transparency between frames
    else:
        save_kwargs['disposal'] = 0  # No special disposal needed
    
    images[0].save(output_gif, **save_kwargs)
    print(f"GIF created successfully: {output_gif}")

# Run the script
if __name__ == "__main__":
    create_gif(INPUT_FOLDER, OUTPUT_GIF, FRAME_DURATION, STRIP_BACKGROUND)