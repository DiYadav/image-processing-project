import cv2
import numpy as np

def detect_changes(before_path, after_path, output_path):
    # Load images
    before = cv2.imread(before_path)
    after = cv2.imread(after_path)

    if before is None or after is None:
        print("❌ Error: Could not load images.")
        return

    print("✔ Images loaded successfully.")

    # Resize to same size (very important for stable results)
    after = cv2.resize(after, (before.shape[1], before.shape[0]))

    # Convert to grayscale
    gray_before = cv2.cvtColor(before, cv2.COLOR_BGR2GRAY)
    gray_after = cv2.cvtColor(after, cv2.COLOR_BGR2GRAY)

    # Absolute difference
    diff = cv2.absdiff(gray_before, gray_after)

    # Threshold to highlight changes
    _, thresh = cv2.threshold(diff, 30, 255, cv2.THRESH_BINARY)

    # Remove noise
    kernel = np.ones((5, 5), np.uint8)
    cleaned = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel)

    # Find contours of changed areas
    contours, _ = cv2.findContours(cleaned, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Draw bounding boxes on AFTER image
    for c in contours:
        if cv2.contourArea(c) > 50:   # remove very small changes
            x, y, w, h = cv2.boundingRect(c)
            cv2.rectangle(after, (x, y), (x + w, y + h), (0, 0, 255), 2)

    # Save result
    cv2.imwrite(output_path, after)

    print(f"✔ Change detection saved at: {output_path}")


if __name__ == "__main__":
    before_path = "input/before.jpg"   # Add your BEFORE image here
    after_path = "input/after.jpg"     # Add your AFTER image here
    output_path = "output/change_result.jpg"

    detect_changes(before_path, after_path, output_path)
