# Medieval Vision Curation Agent

Agente de IA especializado en la **automatización de etiquetado semántico** para imágenes de temática medieval. Está diseñado específicamente para la creación de datasets de alta calidad destinados al entrenamiento de modelos de difusión (Stable Diffusion XL, Flux, LoRA).

## Objetivo

Transformar una colección de imágenes heterogéneas en un dataset estructurado. El agente utiliza modelos de visión avanzados para extraer detalles precisos de:
*   **Materiales:** weathered iron, hammered steel, coarse wool, worn leather.
*   **Iluminación:** torchlight, dramatic chiaroscuro, volumetric fog.
*   **Fidelidad Histórica:** 14th century style, gothic architecture, authentic heraldry.

## Características Principales

*   **Optimización Automática:** Redimensiona imágenes automáticamente (máx 1024px) para reducir costos de tokens y evitar errores de límite de carga (413 Payload Too Large).
*   **Agnóstico al Proveedor:** Compatible con cualquier API que siga el formato de OpenAI (DeepSeek, OpenAI, SiliconFlow, Novita AI, etc.).
*   **Gestión Inteligente de Archivos:** Genera archivos `.txt` con los tags y organiza las imágenes procesadas en una carpeta de destino.
*   **Basado en `uv`:** Utiliza `uv` para una gestión de dependencias ultrarrápida y entornos aislados.

##  Instalación y Configuración

### 1. Requisitos 
[uv](https://github.com/astral-sh/uv)

### 2. Inicialización
```powershell
# Clonar o entrar al directorio
cd medieval-tagger

# Sincronizar dependencias
uv sync
```

### 3. Configuración de Entorno
Copia el archivo de ejemplo y configura tu API Key:
```powershell
cp .env.example .env
```
Edita `.env` con tus credenciales:
```env
API_KEY=tu_api_key_aqui
BASE_URL=https://api.openai.com/v1 # O tu proveedor de preferencia
MODEL_NAME=gpt-4o-mini # O el modelo vision que elijas
```

## Uso

1. Coloca tus imágenes en la carpeta `input_images/`.
2. Ejecuta el agente:
```powershell
uv run main.py
```
3. El agente procesará cada imagen, generará los tags y moverá los archivos a `medieval_dataset/`.

## Estructura del Proyecto

```text
medieval-tagger/
├── input_images/       # Imágenes crudas a procesar
├── medieval_dataset/   # Dataset final (imágenes + .txt)
├── main.py             # Lógica central del agente
├── .env                # Configuración privada
├── pyproject.toml      # Dependencias y metadatos
└── README.md           # Esta guía
```

## Auditoría de Tokens
Al final de cada ejecución, el agente muestra un resumen con:
*   Total de imágenes procesadas exitosamente.
*   Gasto total de tokens.
*   Promedio de tokens por imagen.

## Autor
**Ricardo Urdaneta**
