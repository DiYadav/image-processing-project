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

    # Resize after image to match before
    after = cv2.resize(after, (before.shape[1], before.shape[0]))

    # Convert to grayscale
    gray_before = cv2.cvtColor(before, cv2.COLOR_BGR2GRAY)
    gray_after = cv2.cvtColor(after, cv2.COLOR_BGR2GRAY)

    # Absolute difference
    diff = cv2.absdiff(gray_before, gray_after)

    # Threshold (highlight changes)
    _, thresh = cv2.threshold(diff, 30, 255, cv2.THRESH_BINARY)

    # Remove noise
    kernel = np.ones((5, 5), np.uint8)
    cleaned = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel)

    # Find contours
    contours, _ = cv2.findContours(cleaned, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Draw polygons and rectangles
    for c in contours:
        area = cv2.contourArea(c)
        if area > 80:  # Skip very small noise
            # Draw polygon
            approx = cv2.approxPolyDP(c, 0.01 * cv2.arcLength(c, True), True)
            cv2.polylines(after, [approx], True, (0, 255, 0), 2)

            # # Draw rectangle (optional)
            # x, y, w, h = cv2.boundingRect(c)
            # cv2.rectangle(after, (x, y), (x+w, y+h), (0, 0, 255), 2)

    # Save output
    cv2.imwrite(output_path, after)
    print(f"✔ Done! Output saved at: {output_path}")


if __name__ == "__main__":
    before_path = "input/before.jpg"
    after_path = "input/after.jpg"
    output_path = "output/change_result.jpg"

    detect_changes(before_path, after_path, output_path)
