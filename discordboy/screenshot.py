"""Screenshot capture and processing for Discord."""

import io
import logging

from PIL import Image, ImageDraw, ImageFont

from discordboy.config import Config
from discordboy.emulator import GameBoyEmulator

logger = logging.getLogger(__name__)


async def capture_screenshot(emulator: GameBoyEmulator, overlay_text: str = None) -> io.BytesIO:
    """Capture screenshot from emulator and prepare for Discord upload.

    Args:
        emulator: GameBoyEmulator instance
        overlay_text: Optional text to overlay on the image

    Returns:
        BytesIO buffer containing PNG image data
    """
    try:
        # Get current screen from emulator
        image = emulator.get_screenshot()

        # Scale up using nearest neighbor to keep pixels sharp
        # Game Boy screen is 160x144, we scale by 3x to 480x432
        scaled_width = image.width * Config.SCREEN_SCALE
        scaled_height = image.height * Config.SCREEN_SCALE
        scaled_image = image.resize((scaled_width, scaled_height), Image.NEAREST)

        # Add overlay if provided
        if overlay_text:
            scaled_image = add_overlay(scaled_image, overlay_text)

        # Convert to BytesIO for Discord upload
        buffer = io.BytesIO()
        scaled_image.save(buffer, format="PNG")
        buffer.seek(0)

        return buffer

    except Exception as e:
        logger.error(f"Error capturing screenshot: {e}")
        raise


def add_overlay(image: Image.Image, text: str) -> Image.Image:
    """Add text overlay to an image.

    Args:
        image: PIL Image to add overlay to
        text: Text to display

    Returns:
        Image with overlay added
    """
    try:
        # Create a copy to avoid modifying original
        img_with_overlay = image.copy()
        draw = ImageDraw.Draw(img_with_overlay)

        # Try to use a nice font, fall back to default if not available
        try:
            font = ImageFont.truetype("arial.ttf", 16)
        except OSError:
            font = ImageFont.load_default()

        # Calculate text position (bottom right corner with padding)
        # Use textbbox instead of deprecated textsize
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]

        padding = 10
        x = image.width - text_width - padding
        y = image.height - text_height - padding

        # Draw background rectangle for better readability
        background_bbox = [x - 5, y - 5, x + text_width + 5, y + text_height + 5]
        draw.rectangle(background_bbox, fill=(0, 0, 0, 180))

        # Draw text in white
        draw.text((x, y), text, fill=(255, 255, 255), font=font)

        return img_with_overlay

    except Exception as e:
        logger.error(f"Error adding overlay: {e}")
        # Return original image if overlay fails
        return image


def add_border(
    image: Image.Image, border_color: tuple = (50, 50, 50), border_width: int = 10
) -> Image.Image:
    """Add a border around the image.

    Args:
        image: PIL Image to add border to
        border_color: RGB tuple for border color
        border_width: Width of border in pixels

    Returns:
        Image with border added
    """
    try:
        # Create new image with border
        new_width = image.width + (border_width * 2)
        new_height = image.height + (border_width * 2)

        bordered_image = Image.new("RGB", (new_width, new_height), border_color)
        bordered_image.paste(image, (border_width, border_width))

        return bordered_image

    except Exception as e:
        logger.error(f"Error adding border: {e}")
        return image


async def create_error_image(error_message: str) -> io.BytesIO:
    """Create an error image with a message.

    Args:
        error_message: Error message to display

    Returns:
        BytesIO buffer containing error image
    """
    try:
        # Create a simple error image
        width, height = 480, 432
        image = Image.new("RGB", (width, height), color=(20, 20, 20))
        draw = ImageDraw.Draw(image)

        # Try to load a font
        try:
            font = ImageFont.truetype("arial.ttf", 20)
        except OSError:
            font = ImageFont.load_default()

        # Draw error message
        text = f"Error:\n{error_message}"

        # Calculate text position (centered)
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]

        x = (width - text_width) // 2
        y = (height - text_height) // 2

        draw.text((x, y), text, fill=(255, 100, 100), font=font)

        # Convert to BytesIO
        buffer = io.BytesIO()
        image.save(buffer, format="PNG")
        buffer.seek(0)

        return buffer

    except Exception as e:
        logger.error(f"Error creating error image: {e}")
        raise
