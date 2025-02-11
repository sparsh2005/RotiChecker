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

    # Convert to grayscale and blur slightly to remove noise
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (5, 5), 0)

    # Apply thresholding to isolate the roti (you might need to tweak these parameters)
    ret, thresh = cv2.threshold(gray, 50, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    
    # Find contours in the thresholded image
    contours, hierarchy = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not contours:
        print("No contours found! Make sure the roti is clearly visible in the image.")
        return

    # Assume the largest contour is the roti
    largest_contour = max(contours, key=cv2.contourArea)
    
    # Compute circularity
    circ = compute_circularity(largest_contour)
    # Scale circularity to a 0-100 score (1.0 -> 100 points)
    circularity_score = min(max(circ * 100, 0), 100)
    print(f"Circularity: {circ:.3f} (Score: {circularity_score:.1f}/100)")

    # Create a mask from the roti contour
    mask = np.zeros(gray.shape, dtype=np.uint8)
    cv2.drawContours(mask, [largest_contour], -1, 255, -1)
    
    # Compute color uniformity: lower standard deviation in color means better uniformity.
    # We'll compute this for each channel and average them.
    roti_pixels = cv2.bitwise_and(image, image, mask=mask)
    # Only consider pixels inside the roti (mask != 0)
    indices = np.where(mask != 0)
    if len(indices[0]) == 0:
        print("No roti pixels found in the mask!")
        return
    # Extract pixel values for each channel
    pixel_values = roti_pixels[indices[0], indices[1], :]
    std_dev = np.std(pixel_values, axis=0).mean()  # average standard deviation over B, G, R channels

    # Convert standard deviation to a score: assuming lower std_dev (more uniform) is better.
    # Here we arbitrarily decide that a std_dev of 0 gives 100 points and higher std_devs reduce the score.
    # You might need to calibrate this based on sample images.
    color_score = max(0, 100 - std_dev)
    print(f"Color Uniformity Std Dev: {std_dev:.2f} (Score: {color_score:.1f}/100)")

    # Combine scores with weights (e.g., 70% circularity and 30% color uniformity)
    overall_score = (circularity_score * 0.7) + (color_score * 0.3)
    print(f"\nYour Roti Perfection Score is: {overall_score:.2f}/100")

if __name__ == '__main__':
    # Replace 'roti.jpg' with the path to your roti image file
    roti_checker('roti.jpg')