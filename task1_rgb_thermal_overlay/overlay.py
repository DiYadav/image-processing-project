import cv2
import numpy as np
import os

def rgb_to_thermal(rgb_path, output_path):
    # Load RGB image
    rgb = cv2.imread(rgb_path)
    
    if rgb is None:
        print("❌ Error: Could not load RGB image.")
        return

    print("✔ RGB image loaded successfully.")

    # Convert RGB image to grayscale
    gray = cv2.cvtColor(rgb, cv2.COLOR_BGR2GRAY)

    # Apply thermal color map (JET)
    thermal_image = cv2.applyColorMap(gray, cv2.COLORMAP_JET)

    # Save output image
    cv2.imwrite(output_path, thermal_image)
    print(f"✔ Thermal effect saved at: {output_path}")


if __name__ == "__main__":
    rgb_path = "input/rgb.jpg"  # your RGB image
    output_path = "output/thermal_output.jpg"

    rgb_to_thermal(rgb_path, output_path)
