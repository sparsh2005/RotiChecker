# app.py (already in your workspace)

import cv2
import numpy as np
import math

def compute_circularity(contour):
    """
    Computes the circularity of a contour.
    Circularity = (4 * pi * Area) / (Perimeter^2)
    A perfect circle has a circularity of 1.
    """
    area = cv2.contourArea(contour)
    perimeter = cv2.arcLength(contour, True)
    if perimeter == 0:
        return 0
    circularity = 4 * math.pi * (area / (perimeter ** 2))
    return circularity

def roti_checker(image_path):
    # Load the image
    image = cv2.imread(image_path)
    if image is None:
        print("Error: Could not open image. Please check the file path.")
        return

    # 1. Convert to HSV for color-based thresholding
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    # 2. Define color range that *roughly* matches roti color
    lower = np.array([5, 40, 40])   # Lower bound for H, S, V
    upper = np.array([30, 255, 255])# Upper bound for H, S, V

    # 3. Threshold
    mask = cv2.inRange(hsv, lower, upper)

    # 4. Morphological operations
    kernel = np.ones((5, 5), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)

    # 5. Find contours
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not contours:
        print("No contours found! Make sure the roti is clearly visible and within the color range.")
        return

    # 6. Largest contour => roti
    largest_contour = max(contours, key=cv2.contourArea)

    # 7. Circularity
    circ = compute_circularity(largest_contour)
    circularity_score = min(max(circ * 100, 0), 100)
    print(f"Circularity: {circ:.3f} (Score: {circularity_score:.1f}/100)")

    # 8. Create mask from contour
    shape_mask = np.zeros(image.shape[:2], dtype=np.uint8)
    cv2.drawContours(shape_mask, [largest_contour], -1, 255, -1)

    # 9. Extract roti pixels
    roti_pixels = cv2.bitwise_and(image, image, mask=shape_mask)

    # 10. Compute color uniformity (std dev)
    indices = np.where(shape_mask != 0)
    if len(indices[0]) == 0:
        print("No roti pixels found in the mask!")
        return

    pixel_values = roti_pixels[indices[0], indices[1], :]
    std_dev = np.std(pixel_values, axis=0).mean()

    color_score = max(0, 100 - std_dev)
    print(f"Color Uniformity Std Dev: {std_dev:.2f} (Score: {color_score:.1f}/100)")

    # 11. Combine
    overall_score = (circularity_score * 0.7) + (color_score * 0.3)
    print(f"\nYour Roti Perfection Score is: {overall_score:.2f}/100")

    # Return results for the Flask app to use
    return {
        "circularity": circ,
        "circularity_score": circularity_score,
        "std_dev": std_dev,
        "color_score": color_score,
        "overall_score": overall_score
    }

if __name__ == '__main__':
    # For local testing only
    roti_checker('images/roti1.png')