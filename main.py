import os
import base64
import shutil
import dotenv
import io
from pathlib import Path
from PIL import Image
from openai import OpenAI

# Carga de configuración
dotenv.load_dotenv()

class MedievalTaggerAgent:
    def __init__(self):
        self.api_key = os.getenv("API_KEY")
        self.base_url = os.getenv("BASE_URL", "https://api.deepseek.com")
        self.model = os.getenv("MODEL_NAME", "deepseek-vl-7b-chat")
        
        self.client = OpenAI(
            api_key=self.api_key,
            base_url=self.base_url
        )
        self.input_path = Path(os.getenv("INPUT_DIR", "input_images"))
        self.output_path = Path(os.getenv("DATASET_DIR", "medieval_dataset"))
        self.max_size = int(os.getenv("MAX_IMAGE_SIZE", "1024"))
        self.total_tokens = 0
        
        # System Prompt especializado en Difusión Medieval
        self.system_prompt = (
            "Eres un experto en historia medieval y curador de datasets para Stable Diffusion. "
            "Tu tarea es describir imágenes usando tags separados por comas. "
            "Prioriza: sujeto (clase social, equipo), materiales (polished steel, linen), "
            "iluminación (cinematic, moody), y ambiente (dark fantasy, historical). "
            "Los tags deben estar solo en inglés, no uses palabras en español. "
            "Solo devuelve los tags, sin introducciones ni explicaciones."
        )

    def process_image(self, path):
        """Redimensiona y prepara la imagen para la API."""
        with Image.open(path) as img:
            # Convertir a RGB si es necesario (ej. para PNG con alpha o otros formatos)
            if img.mode != "RGB":
                img = img.convert("RGB")
            
            # Redimensionar manteniendo el aspect ratio si supera el máximo
            if max(img.size) > self.max_size:
                ratio = self.max_size / max(img.size)
                new_size = (int(img.size[0] * ratio), int(img.size[1] * ratio))
                img = img.resize(new_size, Image.Resampling.LANCZOS)
                print(f"  📏 Redimensionada a {new_size[0]}x{new_size[1]}")

            # Guardar en buffer como JPEG
            buffer = io.BytesIO()
            img.save(buffer, format="JPEG", quality=85)
            return base64.b64encode(buffer.getvalue()).decode('utf-8')

    def run(self):
        self.output_path.mkdir(exist_ok=True)
        if not self.input_path.exists():
            print(f"⚠️ El directorio de entrada {self.input_path} no existe.")
            return

        # Verificar configuración básica
        if "api.deepseek.com" in self.base_url and "vl" in self.model:
            print("⚠️ AVISO: El modelo Vision (deepseek-vl) podría no estar disponible en el endpoint oficial de DeepSeek.")
            print("   Si recibes un error '400', considera usar un proveedor compatible o verificar el nombre del modelo.\n")

        images = [f for f in self.input_path.iterdir() if f.suffix.lower() in ['.jpg', '.jpeg', '.jfif', '.png']]
        
        if not images:
            print(f"⚠️ No se encontraron imágenes en {self.input_path}")
            return

        print(f"🚀 Iniciando procesamiento de {len(images)} imágenes...\n")

        for img in images:
            try:
                b64_img = self.process_image(img)
                size_kb = len(b64_img) * 3 / 4 / 1024
                print(f"🖼️  Procesando {img.name} ({round(size_kb, 1)} KB)...")

                # Llamada a la API
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": self.system_prompt},
                        {"role": "user", "content": [
                            {"type": "text", "text": "Genera tags medievales para esta imagen:"},
                            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64_img}"}}
                        ]}
                    ]
                )

                tags = response.choices[0].message.content.strip().lower()
                tokens = response.usage.total_tokens
                self.total_tokens += tokens

                # 1. Crear archivo de tags (.txt)
                txt_filename = self.output_path / f"{img.stem}.txt"
                with open(txt_filename, "w", encoding="utf-8") as f:
                    f.write(tags)
                
                # 2. Trasladar imagen original
                shutil.move(str(img), str(self.output_path / img.name))
                
                print(f"✅ OK | Tokens: {tokens:<6} | Tags: {tags[:50]}...")

            except Exception as e:
                print(f"❌ Error en {img.name}: {e}")
                if "unknown variant `image_url`" in str(e):
                    print("   💡 RECOMENDACIÓN: El modelo/endpoint no soporta imágenes. Cambia el MODEL_NAME o BASE_URL.")
                elif "413" in str(e):
                    print("   💡 RECOMENDACIÓN: La imagen sigue siendo demasiado grande para el servidor.")

        self._print_summary(len(images))

    def _print_summary(self, count):
        print("\n" + "="*50)
        print(f"📊 RESUMEN DE LA OPERACIÓN")
        print(f"Imágenes procesadas finalizadas: {count}")
        print(f"Gasto total estimado: {self.total_tokens} tokens")
        if count > 0:
            print(f"Promedio: {round(self.total_tokens/count, 2)} tokens/img")
        print("="*50)

if __name__ == "__main__":
    agent = MedievalTaggerAgent()
    agent.run()
