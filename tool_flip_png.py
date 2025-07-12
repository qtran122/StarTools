import os
from PIL import Image

# Define input folder path here
INPUT_FOLDER = r"C:\Users\qtran\Desktop\crouch"  # Change this to your folder path

def flip_png_images(input_folder):
    # Define output folder on Desktop
    desktop = os.path.join(os.path.expanduser("~"), "Desktop")
    output_folder = os.path.join(desktop, "Flipped_PNGs")
    
    # Create output folder if it doesn't exist
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    # Walk through input folder and its subfolders
    for root, _, files in os.walk(input_folder):
        for file in files:
            if file.lower().endswith('.png'):
                # Get full path of input PNG
                input_path = os.path.join(root, file)
                
                # Calculate relative path and create corresponding output directory
                rel_path = os.path.relpath(root, input_folder)
                output_subfolder = os.path.join(output_folder, rel_path)
                if not os.path.exists(output_subfolder):
                    os.makedirs(output_subfolder)
                
                # Define output path for flipped image
                output_path = os.path.join(output_subfolder, file)
                
                try:
                    # Open and flip the image
                    with Image.open(input_path) as img:
                        flipped_img = img.transpose(Image.FLIP_LEFT_RIGHT)
                        # Save flipped image
                        flipped_img.save(output_path, 'PNG')
                    print(f"Flipped: {input_path} -> {output_path}")
                except Exception as e:
                    print(f"Error processing {input_path}: {str(e)}")

def main():
    # Verify input folder exists
    if not os.path.isdir(INPUT_FOLDER):
        print(f"Error: The specified folder '{INPUT_FOLDER}' does not exist.")
        return
    
    # Process the images
    print("Starting PNG flipping process...")
    flip_png_images(INPUT_FOLDER)
    print("PNG flipping process completed.")

if __name__ == "__main__":
    main()