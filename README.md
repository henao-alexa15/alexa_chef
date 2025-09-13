# Chef AI 🍳

Chef AI es una aplicación web inteligente construida con Streamlit que transforma una foto de tus ingredientes en recetas deliciosas y creativas. Utiliza el poder de la IA multimodal de Google Gemini para analizar las imágenes y generar recetas completas y estructuradas.

## Características

- **Análisis de Ingredientes por Imagen:** Sube una foto y la IA identificará los ingredientes disponibles.
- **Generación de Recetas Inteligentes:** Obtén recetas detalladas, incluyendo tiempos, porciones, instrucciones paso a paso, consejos y beneficios nutricionales.
- **Lectura de Recetas con Voz:** 🎵 Escucha las recetas completas con controles de reproducción, pausa y parada.
- **Interfaz Intuitiva:** Un diseño limpio y fácil de usar para una experiencia de usuario fluida.
- **Búsqueda de Imágenes de Platos:** Visualiza el resultado final con una imagen representativa de la receta generada.
- **Compatibilidad Multiplataforma:** Funciona tanto en desarrollo local como en despliegue web.

## Cómo Ejecutar el Proyecto Localmente

Sigue estos pasos para poner en marcha la aplicación en tu propio entorno.

### 1. Prerrequisitos

- Python 3.8 o superior
- `pip` y `venv` instalados

### 2. Clonar el Repositorio

```bash
git clone https://github.com/henao-alexa15/alexa_chef.git
cd alexa_chef
```

### 3. Configurar el Entorno Virtual

Es una buena práctica usar un entorno virtual para aislar las dependencias del proyecto.

```bash
# Crear el entorno virtual
python3 -m venv .venv

# Activar el entorno (en Linux/macOS)
source .venv/bin/activate

# En Windows, usa:
# .venv\Scripts\activate
```

### 4. Instalar las Dependencias

```bash
pip install -r requirements.txt
```

### 5. Configurar las Claves de API

Crea un archivo llamado `.env` en la raíz del proyecto y añade tus claves de API de Google Gemini y Tavily.

```bash
# Copia el archivo de ejemplo
cp .env.example .env
```

Luego edita el archivo `.env` con tus claves reales:

```
GOOGLE_API_KEY="TU_API_KEY_DE_GOOGLE_AQUI"
TAVILY_API_KEY="TU_API_KEY_DE_TAVILY_AQUI"
```

**⚠️ Importante:** Nunca subas el archivo `.env` al repositorio. Está incluido en `.gitignore` por seguridad.

### 6. Ejecutar la Aplicación

Una vez que todo esté configurado, lanza la aplicación con Streamlit.

```bash
streamlit run app.py
```

¡La aplicación debería abrirse automáticamente en tu navegador!

## Funcionalidades de Voz (TTS)

Chef AI incluye un sistema avanzado de texto a voz que funciona tanto en desarrollo local como en despliegue web:

### 🎵 **Modo Local (Windows):**
- Utiliza `pyttsx3` para síntesis de voz del sistema
- Voz en español con calidad nativa
- Controles completos: ▶️ Reproducir, ⏸️ Pausar, ⏹️ Detener

### 🌐 **Modo Web (Navegador):**
- Utiliza Web Speech API del navegador
- Compatible con Chrome, Firefox, Safari, Edge
- Voz natural del navegador en español
- Funciona sin instalación adicional

### 🎮 **Controles de Reproducción:**
- **▶️ Reproducir**: Inicia la lectura completa de la receta
- **⏸️ Pausar**: Detiene temporalmente la reproducción
- **⏹️ Detener**: Cancela completamente la reproducción

## Despliegue

Este proyecto está listo para ser desplegado en [Streamlit Community Cloud](https://share.streamlit.io/). Simplemente conecta tu repositorio de GitHub, añade las claves de API como "Secrets" y despliega.

### Variables de Entorno para Despliegue:
```
GOOGLE_API_KEY = "tu_clave_de_google"
TAVILY_API_KEY = "tu_clave_de_tavily"
```

## Seguridad

- Las claves de API están protegidas en el archivo `.env` (no subido al repositorio)
- El archivo `.env.example` sirve como plantilla para configuración
- Nunca subas archivos `.env` con claves reales al repositorio