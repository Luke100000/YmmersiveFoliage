import json
from pathlib import Path

import numpy as np
from PIL import Image


def np_contrast(image: np.ndarray, contrast_factor: float) -> np.ndarray:
    rgb = image[..., :3]
    alpha = image[..., 3:4]

    grayscale = 0.299 * rgb[..., 0] + 0.587 * rgb[..., 1] + 0.114 * rgb[..., 2]
    mean_luminance = np.mean(grayscale)
    degenerate = np.concatenate([np.full_like(rgb, mean_luminance), alpha], axis=-1)

    return degenerate * (1 - contrast_factor) + image * contrast_factor

def np_brightness(image: np.ndarray, brightness_factor: float) -> np.ndarray:
    rgb = image[..., :3]
    alpha = image[..., 3:4]

    degenerate = np.concatenate([np.zeros_like(rgb), alpha], axis=-1)
    return degenerate * (1 - brightness_factor) + image * brightness_factor

def to_ldr(img):
    rgb = img[..., :3]
    q97 = np.percentile(rgb, 97)
    scale = min(1.0, 1.0 / (q97 + 1e-8))
    ldr_rgb = np.clip(rgb * scale, 0, 1)
    return np.concatenate([ldr_rgb, img[..., 3:4]], axis=-1)

def  get_mean_luminance(image: np.ndarray) -> float:
    rgb = image[..., :3]
    alpha = image[..., 3]
    grayscale = 0.299 * rgb[..., 0] + 0.587 * rgb[..., 1] + 0.114 * rgb[..., 2]
    return float(np.mean(grayscale[alpha > 0.5]))

def generate(src: Path, dst: Path, brightness: float, contrast: float, flip: bool = False, midpoint: float = 0.35):
    img = np.array(Image.open(src).convert("RGBA")).astype(np.float32) / 255.0

    mean_luminance = get_mean_luminance(img)
    adapt = 1.0 - (mean_luminance - midpoint)
    brightness = (brightness - 1.0) * adapt + 1.0

    img = np_contrast(img, contrast)
    img = np_brightness(img, brightness)
    img = to_ldr(img)

    if flip:
        img = np.flip(img, axis=1)

    dst.parent.mkdir(parents=True, exist_ok=True)

    Image.fromarray((img * 255).astype(np.uint8)).save(dst)


def main():
    hytale_root = Path(__file__).parent.parent.parent / "Assets"
    pack_root = Path(__file__).parent.parent / "src/main/resources"
    textures_path = "Common/Blocks/Foliage/Leaves"
    files_path = "Server/Item/Items/Plant/Leaves"

    (pack_root / textures_path).mkdir(parents=True, exist_ok=True)
    (pack_root / files_path).mkdir(parents=True, exist_ok=True)

    variations = 5
    leaves = [
        ("Ball", "Ash"),
        ("Ball", "Aspen"),
        ("Ball", "Azure"),
        ("Ball", "Beech"),
        ("Ball", "Birch"),
        ("Ball", "Fig_Blue"),
        ("Ball", "Maple", "CrimsonMaple"),
        ("Ball", "Oak"),
        ("DownShape", "Autumn"),
        ("DownShape", "Bamboo"),
        ("DownShape", "Banyan"),
        ("DownShape", "Dry"),
        ("DownShape", "Gumboab"),
        ("DownShape", "Wisteria_Wild", "Wisteria"),
        ("Hanging", "Camphor"),
        ("Hanging", "Sallow"),
        ("Hanging", "Spiral"),
        ("Hanging", "Windwillow"),
        ("PineShape", "Fir_Red", "RedPine"),
        ("PineShape", "Petrified"),
        ("PineShape", "Snow", "Leaves_Snowy"),
        ("PineShape_NSEW", "Fir", "Pine"),
        ("PineShape_NSEW", "Fir_Snow", "Pine_Snowy"),
        ("UpShapeSoft", "Amber"),
        ("UpShapeSoft", "Bottle"),
        ("UpShapeSoft", "Bramble", "Gramble"),
        ("UpShapeSoft", "Burnt"),
        ("UpShapeSoft", "Cedar"),
        ("UpShapeSoft", "Crystal"),
        ("UpShapeSoft", "Dead"),
        ("UpShapeSoft", "Fire"),
        ("UpShapeSoft", "Goldentree", "Amber"),
        ("UpShapeSoft", "Palo"),
        ("UpShapeSoft", "Poisoned"),
        ("UpShapeSoft", "Redwood"),
        ("WindyShape", "Stormbark"),
    ]

    # Copy json files
    for t in leaves:
        shape = t[0]
        leaf = t[1]
        tex = t[2] if len(t) > 2 else leaf

        name = f"Plant_Leaves_{leaf}.json"
        src_path = hytale_root / files_path / name
        dst_path = pack_root / files_path / name
        content = json.loads(src_path.read_text(encoding="utf-8"))

        content["BlockType"]["CustomModel"] = (
            f"Blocks/Foliage/Leaves/{shape}.blockymodel"
        )

        for variant in range(variations):
            darken = 0.7
            generate(
                hytale_root / textures_path / f"{shape}_Textures" / f"{tex}.png",
                pack_root
                / textures_path
                / f"{shape}_Textures"
                / f"{tex}_{variant}.png",
                1.0 + (variant - (variations - 1) / 2 - darken) * 0.07,
                1.15,
                flip=(variant % 2 == 1),
            )

        content["BlockType"]["CustomModelTexture"] = [
            {
                "Texture": f"Blocks/Foliage/Leaves/{shape}_Textures/{tex}_{variant}.png",
                "Weight": 1,
            }
            for variant in range(variations)
        ]

        dst_path.write_text(json.dumps(content, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
