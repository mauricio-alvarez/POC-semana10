import os
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

router = APIRouter()
IMAGE_FOLDER = os.path.join(os.getcwd(), "app/static/images")

@router.get("/image-alt/{pokemon_name}")
def get_image_fallback(pokemon_name: str):
    filename = f"{pokemon_name.lower()}.png"
    image_path = os.path.join(IMAGE_FOLDER, filename)

    if os.path.exists(image_path):
        return FileResponse(image_path, media_type="image/png")
    
    raise HTTPException(status_code=404, detail="Image not found")
