from PIL import Image, ImageDraw
import math
import random
import tkinter as tk
from tkinter import Scale, Button

# Function to generate the gradient background
def generate_gradient(width, height, color1, color2, angle_degrees):
    image = Image.new("RGB", (width, height))
    angle_radians = math.radians(angle_degrees)
    slope = math.tan(angle_radians)
    
    for y in range(height):
        for x in range(width):
            factor = (x + slope * y) / (width + slope * height)
            r = int(color1[0] + (color2[0] - color1[0]) * factor)
            g = int(color1[1] + (color2[1] - color1[1]) * factor)
            b = int(color1[2] + (color2[2] - color1[2]) * factor)
            image.putpixel((x, y), (r, g, b))
    
    return image

# Function to draw the hexagon grid with random missing sides
def draw_hexagon_grid(image, hex_size, line_color, speed_factor, distribution_factor):
    draw = ImageDraw.Draw(image)
    width, height = image.size
    hex_width = 2 * hex_size
    hex_height = math.sqrt(3) * hex_size
    
    # Calculate the number of hexagons that can fit horizontally and vertically
    cols = int(width / (hex_width * 0.75)) + 2
    rows = int(height / hex_height) + 2
    
    # Hexagon's vertical offset for staggered rows
    for row in range(rows):
        for col in range(cols):
            x = col * hex_width * 0.75
            y = row * hex_height
            
            if col % 2 == 1:
                y += hex_height / 2
            
            # Gradually increase the number of missing sides as we move across
            missing_sides = slow_increase_missing_sides(col, cols, speed_factor, distribution_factor)
            draw_hexagon(draw, x, y, hex_size, line_color, missing_sides, col, row)

# Function to calculate missing sides with speed and distribution factors
def slow_increase_missing_sides(col, total_cols, speed_factor, distribution_factor):
    progress = col / total_cols  # Relative column position
    
    # Apply the speed factor to control the rate of increase
    adjusted_progress = (progress ** speed_factor) * distribution_factor
    missing_sides = int(6 * adjusted_progress)  # Gradual increase in missing sides
    
    # Ensure missing_sides is between 0 and 6
    missing_sides = min(max(missing_sides, 0), 6)
    
    return missing_sides

# Function to draw a hexagon with some sides missing
def draw_hexagon(draw, x_center, y_center, size, line_color, missing_sides, col, row):
    vertices = []
    for i in range(6):
        angle = math.radians(60 * i)
        x = x_center + size * math.cos(angle)
        y = y_center + size * math.sin(angle)
        vertices.append((x, y))
    
    missing_sides_list = random.sample(range(6), missing_sides)
    
    # Draw the hexagon outline, skipping the specified number of sides
    for i in range(6):
        if i not in missing_sides_list:
            start = vertices[i]
            end = vertices[(i + 1) % 6]
            draw.line([start, end], fill=line_color, width=2)

# Function to draw a hollow circle overlay at the center
def draw_hollow_circle(image, hex_size, line_color):
    width, height = image.size
    circle_radius = hex_size * 3  # Set the radius of the circle
    
    # Draw the hollow circle (only the outline)
    draw = ImageDraw.Draw(image)
    center = (width // 2, height // 2)
    draw.ellipse([center[0] - circle_radius, center[1] - circle_radius, center[0] + circle_radius, center[1] + circle_radius], outline=line_color, width=3)

# Function to remove hexagon pixels inside the circle (make them transparent)
def remove_pixels_inside_circle(image, hex_size):
    width, height = image.size
    circle_radius = hex_size * 2.975
    center = (width // 2, height // 2)
    
    # Loop through every pixel in the image
    pixels = image.load()  # Create a pixel access object for manipulation
    for y in range(height):
        for x in range(width):
            # Calculate the distance from the current pixel to the circle center
            distance = math.sqrt((x - center[0]) ** 2 + (y - center[1]) ** 2)
            
            # If the pixel is inside the circle, make it transparent
            if distance <= circle_radius:
                pixels[x, y] = (0, 0, 0, 0)  # Make the pixel transparent (RGBA)

# Function to generate and display the image based on the current slider values
def generate_image():
    global gradient_image
    speed_factor = speed_slider.get()  # Get the speed factor from the slider
    distribution_factor = distribution_slider.get()  # Get the distribution factor from the slider
    
    # Generate the gradient background and convert to RGBA
    gradient_image = generate_gradient(width, height, color1, color2, angle_degrees).convert("RGBA")
    
    # Create a separate image for the hexagons
    hexagon_image = Image.new("RGBA", (width, height), (0, 0, 0, 0))  # Transparent background
    draw_hexagon_grid(hexagon_image, hex_size, line_color, speed_factor, distribution_factor)
    
    # Draw the hollow circle overlay on top of the hexagons
    draw_hollow_circle(hexagon_image, hex_size, line_color)
    
    # Remove the pixels inside the circle (make them transparent)
    remove_pixels_inside_circle(hexagon_image, hex_size)
    
    # Merge hexagon image with the gradient background
    final_image = Image.alpha_composite(gradient_image, hexagon_image)
    
    # Save and show the final image
    final_image.save("generated_image_with_hollow_circle_and_removed_hexagons.png")
    final_image.show()


# Define initial settings
color1 = (8, 14, 36)  # Dark blue
color2 = (60, 60, 60)  # Light gray
width = 1920
height = 1080
angle_degrees = 10
hex_size = 75
line_color = (173, 216, 230)  # Light blue

# Create the root window using tkinter
root = tk.Tk()
root.title("Hexagon Grid Generator")

# Create sliders for speed and distribution control
speed_slider = Scale(root, from_=1, to=5, orient=tk.HORIZONTAL, label="Speed Factor")
speed_slider.set(1)  # Default speed factor
speed_slider.pack(pady=10)

distribution_slider = Scale(root, from_=1, to=5, orient=tk.HORIZONTAL, label="Distribution Factor")
distribution_slider.set(1)  # Default distribution factor
distribution_slider.pack(pady=10)

# Create a button to generate the image with the current slider values
generate_button = Button(root, text="Generate Image", command=generate_image)
generate_button.pack(pady=20)

# Run the tkinter main loop
root.mainloop()
