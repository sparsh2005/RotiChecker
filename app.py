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

    # 2. Define a color range that *roughly* matches roti color
    # NOTE: These values are guesses — you will need to experiment!
    lower = np.array([5, 40, 40])   # Lower bound for H, S, V
    upper = np.array([30, 255, 255])# Upper bound for H, S, V

    # 3. Threshold to isolate the roti based on color
    mask = cv2.inRange(hsv, lower, upper)

    # 4. Clean up the mask using morphological operations
    kernel = np.ones((5, 5), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)   # Remove small noise
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)  # Close small holes

    # 5. Find contours in the masked image
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not contours:
        print("No contours found! Make sure the roti is clearly visible and within the color range.")
        return

    # 6. Assume the largest contour is the roti
    largest_contour = max(contours, key=cv2.contourArea)

    # 7. Compute circularity
    circ = compute_circularity(largest_contour)
    # Scale circularity to a 0-100 score (1.0 -> 100 points).
    # You can tweak this to be more forgiving by multiplying circ by something > 1.
    circularity_score = min(max(circ * 100, 0), 100)
    print(f"Circularity: {circ:.3f} (Score: {circularity_score:.1f}/100)")

    # 8. Create a mask from the largest contour for analyzing color uniformity
    shape_mask = np.zeros(image.shape[:2], dtype=np.uint8)
    cv2.drawContours(shape_mask, [largest_contour], -1, 255, -1)

    # 9. Extract roti pixels from the original image
    roti_pixels = cv2.bitwise_and(image, image, mask=shape_mask)

    # 10. Compute color uniformity: 
    #     lower standard deviation = more uniform color
    indices = np.where(shape_mask != 0)
    if len(indices[0]) == 0:
        print("No roti pixels found in the mask!")
        return

    pixel_values = roti_pixels[indices[0], indices[1], :]
    std_dev = np.std(pixel_values, axis=0).mean()  # average std dev over B, G, R channels

    # 11. Convert standard deviation to a score
    #     You may need to calibrate the 100 - std_dev formula for your images.
    color_score = max(0, 100 - std_dev)
    print(f"Color Uniformity Std Dev: {std_dev:.2f} (Score: {color_score:.1f}/100)")

    # 12. Combine scores with weights (adjust as you see fit)
    #     Example: 70% circularity, 30% color uniformity
    overall_score = (circularity_score * 0.7) + (color_score * 0.3)
    print(f"\nYour Roti Perfection Score is: {overall_score:.2f}/100")

if __name__ == '__main__':
    # Replace with your own image path
    roti_checker('/Users/spars/Desktop/RotiChecker/images/roti1.png')