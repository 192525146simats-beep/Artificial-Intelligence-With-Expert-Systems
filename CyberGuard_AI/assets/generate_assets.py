
from PIL import Image, ImageDraw
import math
from pathlib import Path

OUTPUT = Path(__file__).resolve().parent
OUTPUT.mkdir(exist_ok=True)


# --------------------------------
# 1. CYBERGUARD AI LOGO
# --------------------------------

logo = Image.new("RGBA", (512, 512), (0, 0, 0, 0))

draw = ImageDraw.Draw(logo)

draw.rounded_rectangle(
    (40, 40, 472, 472),
    radius=90,
    fill="#0b2945",
    outline="#00d9ff",
    width=12
)

shield = [
    (256, 100),
    (380, 150),
    (360, 290),
    (256, 410),
    (152, 290),
    (132, 150)
]

draw.polygon(
    shield,
    fill="#087fa8",
    outline="#00e5ff"
)

draw.line(
    [(190, 255), (235, 305), (330, 200)],
    fill="white",
    width=22
)

logo.save(OUTPUT / "logo.png")


# --------------------------------
# 2. CYBERSECURITY BACKGROUND
# --------------------------------

WIDTH = 1600
HEIGHT = 900

background = Image.new(
    "RGB",
    (WIDTH, HEIGHT),
    "#071426"
)

pixels = background.load()

for y in range(HEIGHT):

    for x in range(WIDTH):

        distance = math.sqrt(
            ((x - 1250) / 1000) ** 2
            + ((y - 100) / 700) ** 2
        )

        glow = max(0, 1 - distance)

        pixels[x, y] = (
            7 + int(glow * 8),
            20 + int(glow * 35),
            38 + int(glow * 55)
        )

draw = ImageDraw.Draw(background, "RGBA")

# Network grid

for x in range(0, WIDTH, 100):

    draw.line(
        (x, 0, x, HEIGHT),
        fill=(0, 210, 255, 25),
        width=1
    )

for y in range(0, HEIGHT, 100):

    draw.line(
        (0, y, WIDTH, y),
        fill=(0, 210, 255, 25),
        width=1
    )

# Network connection points

nodes = [
    (180, 170),
    (410, 280),
    (650, 130),
    (850, 390),
    (1120, 210),
    (1370, 460),
    (1040, 700),
    (480, 690),
    (220, 520),
    (1460, 130)
]

for i, (x1, y1) in enumerate(nodes):

    for x2, y2 in nodes[i + 1:]:

        if math.hypot(x2 - x1, y2 - y1) < 500:

            draw.line(
                (x1, y1, x2, y2),
                fill=(0, 210, 255, 50),
                width=2
            )

    draw.ellipse(
        (x1 - 6, y1 - 6, x1 + 6, y1 + 6),
        fill=(0, 225, 255, 220)
    )

background.save(
    OUTPUT / "background.png"
)

print("CyberGuard AI assets generated successfully!")

print("Created:")
print(OUTPUT / "logo.png")
print(OUTPUT / "background.png")

