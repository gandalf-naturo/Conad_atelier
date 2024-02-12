import os
from PIL import Image

def compress_images_in_folder(folder_path, output_folder, max_size=(300, 300), quality=85):
    # Assicurati che l'output folder esista, altrimenti crealo
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    # Attraversa tutti i file nella cartella
    for filename in os.listdir(folder_path):
        filepath = os.path.join(folder_path, filename)
        # Controlla se il file è un'immagine
        if os.path.isfile(filepath) and any(filename.lower().endswith(ext) for ext in ['.jpg', '.jpeg', '.png', '.bmp']):
            # Apri l'immagine e comprimila
            with Image.open(filepath) as img:
                img.thumbnail(max_size)
                img.save(os.path.join(output_folder, filename), quality=quality)

# Esempio di utilizzo:
input_folder = '/home/paolo/Desktop/Conad_atelier/static/immagini/'
output_folder = '/home/paolo/Desktop/img_compresse'
compress_images_in_folder(input_folder, output_folder)
