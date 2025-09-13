import os
import json
import google.generativeai as genai
from tavily import TavilyClient
from dotenv import load_dotenv

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