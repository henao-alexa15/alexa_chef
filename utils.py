import os
import json
import google.generativeai as genai
from tavily import TavilyClient
from dotenv import load_dotenv
import pyttsx3
import time
import threading
import subprocess

# Variables globales para controlar el TTS
tts_engine = None
is_speaking = False
is_paused = False
current_text = ""

# Cargar variables de entorno
load_dotenv()

# Debug: verificar variables de entorno
print("GOOGLE_API_KEY:", os.getenv("GOOGLE_API_KEY"))
print("TAVILY_API_KEY:", os.getenv("TAVILY_API_KEY"))

# Configurar APIs
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
tavily = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

def get_structured_recipe(image, meal_type):
    """
    Genera una receta estructurada en formato JSON utilizando Gemini.
    """
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    prompt = f"""
    Eres un chef experto en IA. Analiza la imagen de los ingredientes proporcionada.
    Tu tarea es crear una receta creativa y deliciosa que sea específicamente un "{meal_type}". Esta es una restricción estricta y obligatoria. La receta DEBE ser un "{meal_type}".
    
    Sigue estas instrucciones estrictamente:
    1.  **Identifica Ingredientes:** Primero, lista TODOS los ingredientes que puedas identificar en la imagen.
    2.  **Crea una Receta:** Basándote en una selección de esos ingredientes, crea una receta completa.
    3.  **Instrucciones Detalladas:** Para la sección 'instructions', escribe cada paso de la manera más descriptiva y clara posible, como si se lo estuvieras explicando a un principiante. Incluye detalles sobre temperaturas, texturas, tiempos y consejos de preparación en cada paso.
    4.  **Formato de Salida:** Responde ÚNICAMENTE con un objeto JSON. No incluyas texto antes o después del JSON.
        El JSON debe tener la siguiente estructura exacta:
        {{
          "recipe_name": "Nombre del Plato",
          "description": "Una descripción breve y apetitosa del plato.",
          "prep_time": "X minutes",
          "cook_time": "Y minutes",
          "servings": "Z",
          "category": "Saludable",
          "difficulty": "Fácil",
          "detected_ingredients": [
            {{ "name": "Ingrediente 1 detectado", "quantity": "Descripción de la cantidad vista" }},
            {{ "name": "Ingrediente 2 detectado", "quantity": "Descripción de la cantidad vista" }}
          ],
          "recipe_ingredients": [
            {{ "name": "Ingrediente A para la receta", "quantity": "Cantidad necesaria" }},
            {{ "name": "Ingrediente B para la receta", "quantity": "Cantidad necesaria" }}
          ],
          "instructions": [
            "Paso 1 de la preparación, muy detallado.",
            "Paso 2 de la preparación, muy detallado.",
            "Paso 3 de la preparación, muy detallado."
          ],
          "pro_tips": [
            "Un consejo profesional.",
            "Otro consejo profesional."
          ],
          "nutritional_benefits": [
            "Beneficio nutricional 1.",
            "Beneficio nutricional 2."
          ]
        }}
    """
    
    response = model.generate_content([prompt, image])
    
    try:
        # Limpiar la respuesta para asegurar que sea un JSON válido
        json_text = response.text.strip().replace("```json", "").replace("```", "")
        recipe_data = json.loads(json_text)
        return recipe_data
    except (json.JSONDecodeError, IndexError) as e:
        print(f"Error al decodificar JSON: {e}")
        print(f"Respuesta recibida: {response.text}")
        return None

def get_recipe_image(recipe_name):
    """
    Busca una imagen para la receta usando Tavily.
    """
    try:
        response = tavily.search(query=f"Foto de un plato de {recipe_name}", search_depth="advanced", include_images=True, max_results=1)
        if response.get('images'):
            return response['images'][0]
    except Exception:
        return None

def init_tts_engine():
    """Inicializa el motor de TTS con configuración optimizada."""
    global tts_engine
    if tts_engine is None:
        try:
            tts_engine = pyttsx3.init()

            # Configurar velocidad y volumen para voz suave
            tts_engine.setProperty('rate', 150)  # Un poco más lento para mejor comprensión
            tts_engine.setProperty('volume', 0.8)  # Un poco más alto

            # Listar todas las voces disponibles para debug
            voices = tts_engine.getProperty('voices')
            print(f"Voces disponibles: {len(voices)}")
            for i, voice in enumerate(voices):
                gender = getattr(voice, 'gender', 'Unknown')
                print(f"  {i}: {voice.name} - Gender: {gender} - ID: {voice.id}")

            selected_voice = None

            # Buscar voz en español (Colombia, México, España, etc.)
            spanish_keywords = ['spanish', 'español', 'es-', 'colombia', 'mexico', 'espana', 'castellano']
            for voice in voices:
                voice_name = voice.name.lower()
                # Buscar voces en español
                if any(keyword in voice_name for keyword in spanish_keywords):
                    selected_voice = voice
                    print(f"Encontrada voz en español: {voice.name}")
                    break

            # Si no encontró voz en español, buscar voz femenina
            if not selected_voice:
                for voice in voices:
                    if hasattr(voice, 'gender') and voice.gender and voice.gender.lower() == 'female':
                        selected_voice = voice
                        print(f"Encontrada voz femenina: {voice.name}")
                        break

            # Si no encontró voz femenina, usar la primera voz disponible
            if not selected_voice and voices:
                selected_voice = voices[0]
                print(f"Usando primera voz disponible: {selected_voice.name}")

            # Configurar la voz seleccionada
            if selected_voice:
                tts_engine.setProperty('voice', selected_voice.id)
                print(f"Configurada voz: {selected_voice.name}")
            else:
                print("No se encontraron voces disponibles")

        except Exception as e:
            print(f"Error inicializando TTS: {e}")
            tts_engine = None

def speak_text(text):
    """
    Función simple para reproducir texto completo.
    """
    global is_speaking, current_text

    try:
        init_tts_engine()
        current_text = text
        is_speaking = True
        print("Iniciando reproducción de voz...")

        if tts_engine:
            tts_engine.say(text)
            tts_engine.runAndWait()
        else:
            speak_text_fallback(text)

        is_speaking = False
        print("Reproducción completada")

    except Exception as e:
        print(f"Error en TTS: {e}")
        is_speaking = False

def pause_speaking():
    """
    Pausa la reproducción actual.
    """
    global is_speaking, is_paused
    if is_speaking:
        is_speaking = False
        is_paused = True
        if tts_engine:
            tts_engine.stop()
        print("Lectura pausada")

def resume_speaking():
    """
    Reanuda la reproducción desde el inicio.
    """
    global is_paused, current_text
    if is_paused and current_text:
        is_paused = False
        speak_text(current_text)

def start_speaking(text):
    """
    Inicia la reproducción en un hilo separado.
    """
    def speak_thread():
        speak_text(text)

    thread = threading.Thread(target=speak_thread)
    thread.daemon = True
    thread.start()

def speak_text_fallback(text):
    """
    Función de respaldo que usa PowerShell para texto a voz con voz en español.
    """
    try:
        # Limpiar el texto para evitar problemas con comillas
        clean_text = text.replace("'", "").replace('"', '').replace('`', '')

        # Intentar diferentes voces en español disponibles en Windows
        voices_to_try = [
            'Microsoft Helena',  # Español (México)
            'Microsoft Laura',  # Español (España)
            'Microsoft Pablo',  # Español (España)
            'Microsoft Raul',   # Español (México)
            'Microsoft Sabina', # Español (México)
            'Microsoft Zira'    # Inglés (pero clara)
        ]

        for voice_name in voices_to_try:
            try:
                command = f'powershell -Command "Add-Type -AssemblyName System.Speech; $speak = New-Object System.Speech.Synthesis.SpeechSynthesizer; $speak.SelectVoice(\'{voice_name}\'); $speak.Rate = -2; $speak.Volume = 80; $speak.Speak(\'{clean_text}\');"'
                result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=30)

                if result.returncode == 0:
                    print(f"Usando voz: {voice_name}")
                    return
            except subprocess.TimeoutExpired:
                print(f"Timeout con voz: {voice_name}")
                continue
            except Exception as e:
                print(f"Error con voz {voice_name}: {e}")
                continue

        # Si ninguna voz específica funcionó, usar voz predeterminada
        print("Usando voz predeterminada del sistema")
        command = f'powershell -Command "Add-Type -AssemblyName System.Speech; $speak = New-Object System.Speech.Synthesis.SpeechSynthesizer; $speak.Rate = -2; $speak.Volume = 80; $speak.Speak(\'{clean_text}\');"'
        subprocess.run(command, shell=True, capture_output=True, text=True, timeout=60)

    except Exception as e:
        print(f"Error en función de respaldo TTS: {e}")
        # Último intento con comando más simple
        try:
            print("Intentando comando TTS simple...")
            subprocess.run(['powershell', '-Command', f'(New-Object -ComObject SAPI.SpVoice).Speak("{clean_text}")'],
                         capture_output=True, text=True, timeout=30)
        except Exception as e2:
            print(f"Error en respaldo final TTS: {e2}")

def stop_speaking():
    """
    Detiene completamente la reproducción de voz.
    """
    global tts_engine, is_speaking, is_paused, current_text
    try:
        if tts_engine:
            tts_engine.stop()
        is_speaking = False
        is_paused = False
        current_text = ""
        print("Lectura detenida")
    except Exception as e:
        print(f"Error al detener TTS: {e}")

def get_recipe_text_for_speech(recipe_data):
    """
    Prepara el texto completo de la receta para ser leído.
    """
    text_parts = []

    # Título y descripción
    text_parts.append(f"Receta: {recipe_data['recipe_name']}")
    text_parts.append(recipe_data['description'])

    # Metadatos
    text_parts.append(f"Tiempo de preparación: {recipe_data['prep_time']}")
    text_parts.append(f"Tiempo de cocción: {recipe_data['cook_time']}")
    text_parts.append(f"Porciones: {recipe_data['servings']}")
    text_parts.append(f"Categoría: {recipe_data['category']}")
    text_parts.append(f"Dificultad: {recipe_data['difficulty']}")

    # Ingredientes
    text_parts.append("Ingredientes:")
    for ing in recipe_data["recipe_ingredients"]:
        text_parts.append(f"{ing['quantity']} de {ing['name']}")

    # Instrucciones
    text_parts.append("Instrucciones:")
    for i, step in enumerate(recipe_data["instructions"]):
        text_parts.append(f"Paso {i+1}: {step}")

    # Consejos
    if recipe_data.get("pro_tips"):
        text_parts.append("Consejos profesionales:")
        for tip in recipe_data["pro_tips"]:
            text_parts.append(tip)

    # Beneficios nutricionales
    if recipe_data.get("nutritional_benefits"):
        text_parts.append("Beneficios nutricionales:")
        for benefit in recipe_data["nutritional_benefits"]:
            text_parts.append(benefit)

    return " ".join(text_parts)