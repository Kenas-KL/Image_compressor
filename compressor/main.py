
import os
from pathlib import Path
from PIL import Image
from PIL import ImageFile
from tqdm import tqdm

os.system("clear")

quality = 85
Image.MAX_IMAGE_PIXELS = None
ImageFile.LOAD_TRUNCATED_IMAGES = True
print()

entry_path = Path("")
out_path = Path(f"{entry_path}/Optmized_images")



if not out_path.exists():
    out_path.mkdir()



paths = []
for _ in entry_path.iterdir():
    if _.is_file():
        paths.append(_)



print("\nTraitement d'images en cours...")
for _ in tqdm(range(0,len(paths))):
    if Path(f"{out_path}/{Path(paths[_]).name}").exists():
        continue
    with Image.open(paths[_]) as img:
        img.thumbnail((8000,8000), Image.LANCZOS)
        img.save(os.path.join(out_path, f"{Path(paths[_]).name}"),progressive=True,optimize=True, quality=quality)

print("Done !")