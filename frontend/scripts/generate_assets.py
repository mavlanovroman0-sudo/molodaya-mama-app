from pathlib import Path

from PIL import Image, ImageDraw

assets = Path(__file__).resolve().parent.parent / "assets"
assets.mkdir(parents=True, exist_ok=True)

icon = Image.new("RGB", (1024, 1024), "#D4919A")
ImageDraw.Draw(icon).ellipse((200, 200, 824, 824), fill="#F8F4F0")
icon.save(assets / "icon.png")

splash = Image.new("RGB", (1242, 2436), "#F8F4F0")
ImageDraw.Draw(splash).ellipse((421, 968, 821, 1368), fill="#D4919A")
splash.save(assets / "splash.png")

print("Generated", assets / "icon.png", assets / "splash.png")
