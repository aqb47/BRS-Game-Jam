import math
import pygame
import os

# Get an arc from a circle. Angle should be in degrees
def get_circle_slice(surface : pygame.Surface, start_angle, end_angle):
    size = surface.get_size()
    center = (size[0] // 2, size[1] // 2)
    radius = min(size) // 2
    
    # Create a matching transparent surface for the final image
    sliced_surface = pygame.Surface(size, pygame.SRCALPHA)
    
    # Create a separate transparent mask surface
    mask = pygame.Surface(size, pygame.SRCALPHA)
    
    # Generate the wedge points using trigonometry
    points = [center]
    
    # Ensure end_angle sweeps correctly if it crosses the 0/360 boundary
    if end_angle < start_angle:
        end_angle += 360
        
    # Step through angles to draw a smooth outer curve for large arcs
    steps = int(abs(end_angle - start_angle) // 5) + 2
    for i in range(steps):
        angle = start_angle + (end_angle - start_angle) * (i / (steps - 1))
        rad = math.radians(angle)
        
        # Pygame's Y-axis is inverted (down is positive), so we subtract Y
        x = center[0] + radius * math.cos(rad)
        y = center[1] - radius * math.sin(rad)
        points.append((x, y))
        
    # Draw the solid wedge white (opaque) onto the mask
    pygame.draw.polygon(mask, (255, 255, 255, 255), points)
    
    # Combine the original sprite and the mask
    sliced_surface.blit(surface, (0, 0))
    sliced_surface.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    
    return sliced_surface

# Get number of files in a directory
def file_count(path):
    if not os.path.isdir(path):
        return 0
    return sum(1 for file in os.listdir(path) if os.path.isfile(os.path.join(path, file)))
