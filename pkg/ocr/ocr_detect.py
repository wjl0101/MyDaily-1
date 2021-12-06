import easyocr
from PIL import Image
from PIL import ImageEnhance
import io
import numpy as np

def read_image(image_byte):
    
    img = Image.open(io.BytesIO(image_byte)).convert('L')
    
    enh_bri = ImageEnhance.Brightness(img)
    new_img = enh_bri.enhance(factor=1.5)
    image = np.array(new_img)
    reader = easyocr.Reader(['en'])
    horizontal_list, free_list = reader.detect(image, optimal_num_chars=4)
    character = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    allow_list = list(character)
    allow_list.extend(list(character.lower()))

    result = reader.recognize(image, 
                            allowlist=allow_list,
                            horizontal_list=horizontal_list[0],
                            free_list=free_list[0],
                            detail = 0)
    return result[0]
    
    