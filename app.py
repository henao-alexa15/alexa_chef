import streamlit as st
from PIL import Image
import utils
import threading

st.set_page_config(layout="centered")

def display_recipe(recipe_data):
    """Función para mostrar la receta completa con botones de control"""
    # 2. Obtener una imagen para la receta
    recipe_image_url = utils.get_recipe_image(recipe_data["recipe_name"])

    # --- Mostrar la receta con el nuevo diseño vertical ---

    # Imagen del plato
    if recipe_image_url:
        st.image(recipe_image_url, caption=recipe_data["recipe_name"], width='stretch')

    # Título y descripción
    st.header(recipe_data["recipe_name"])
    st.write(recipe_data["description"])

    # Metadatos de la receta
    meta_cols = st.columns(5)
    with meta_cols[0]:
        st.info(f"**Prep:**\n{recipe_data['prep_time']}")
    with meta_cols[1]:
        st.info(f"**Cook:**\n{recipe_data['cook_time']}")
    with meta_cols[2]:
        st.info(f"**Servings:**\n{recipe_data['servings']}")
    with meta_cols[3]:
        st.info(f"**Category:**\n{recipe_data['category']}")
    with meta_cols[4]:
        st.success(f"**{recipe_data['difficulty']}**")

    st.divider()

    # Ingredientes
    st.subheader("🛒 Ingredientes")
    for ing in recipe_data["recipe_ingredients"]:
        st.checkbox(f"**{ing['quantity']}** {ing['name']}")

    st.divider()

    # Instrucciones
    st.subheader("👨‍🍳 Instrucciones")
    for i, step in enumerate(recipe_data["instructions"]):
        st.markdown(f"**Paso {i+1}:** {step}")

    st.divider()

    # Consejos y Beneficios
    if recipe_data.get("pro_tips"):
        st.subheader("💡 Pro Tips")
        for tip in recipe_data["pro_tips"]:
            st.markdown(f"• {tip}")

    if recipe_data.get("nutritional_benefits"):
        st.subheader("🥗 Beneficios Nutricionales")
        for benefit in recipe_data["nutritional_benefits"]:
            st.markdown(f"• {benefit}")

    st.divider()

    # Botones para controlar la lectura
    col1, col2, col3 = st.columns([1, 1, 1])

    with col1:
        if st.button("▶️ Reproducir", key="play_recipe", help="Reproducir la receta completa"):
            if not st.session_state.is_reading:
                st.session_state.is_reading = True
                st.session_state.is_paused = False
                with st.spinner("Preparando la lectura..."):
                    recipe_text = utils.get_recipe_text_for_speech(recipe_data)
                    def speak_thread():
                        try:
                            utils.speak_text(recipe_text)
                        finally:
                            st.session_state.is_reading = False
                            st.session_state.is_paused = False

                    thread = threading.Thread(target=speak_thread)
                    thread.daemon = True
                    thread.start()
                    st.success("🎵 Reproduciendo la receta...")

    with col2:
        if st.button("⏸️ Pausar", key="pause_reading", help="Pausar la reproducción"):
            if st.session_state.is_reading:
                utils.pause_speaking()
                st.session_state.is_reading = False
                st.session_state.is_paused = True
                st.warning("⏸️ Lectura pausada")

    with col3:
        if st.button("⏹️ Detener", key="stop_reading", help="Detener completamente la reproducción"):
            utils.stop_speaking()
            st.session_state.is_reading = False
            st.session_state.is_paused = False
            st.info("⏹️ Lectura detenida")

    # Mostrar estado de la lectura
    if st.session_state.is_reading:
        st.info("🔊 Reproduciendo receta...")
    elif hasattr(st.session_state, 'is_paused') and st.session_state.get('is_paused', False):
        st.warning("⏸️ Lectura pausada - presiona Reproducir para continuar")

def main():
    # Inicializar session_state para mantener la receta
    if 'recipe_data' not in st.session_state:
        st.session_state.recipe_data = None
    if 'is_reading' not in st.session_state:
        st.session_state.is_reading = False
    if 'is_paused' not in st.session_state:
        st.session_state.is_paused = False

    # --- Header Centrado ---
    with st.container():
        st.image("logo.png", width=200) # Logo centrado y con tamaño fijo
        st.title("Chef AI 🍳")
        st.subheader("Sube una foto de tus ingredientes y descubre una receta increíble.")

    st.divider()

    uploaded_file = st.file_uploader(
        "Arrastra y suelta una imagen aquí o haz clic para seleccionar",
        type=["jpg", "png", "jpeg"]
    )

    meal_type = st.selectbox(
        "¿Para qué comida buscas una receta?",
        ("Desayuno", "Almuerzo", "Cena", "Postre", "Snack")
    )

    submit_button = st.button("Generar Receta")

    # Mostrar receta guardada si existe
    if st.session_state.recipe_data:
        display_recipe(st.session_state.recipe_data)

    if submit_button and uploaded_file is not None:
        image = Image.open(uploaded_file)
        
        with st.spinner("Creando una receta única para ti... 👨‍🍳"):
            try:
                # 1. Generar la receta estructurada
                recipe_data = utils.get_structured_recipe(image, meal_type)
                
                if recipe_data:
                    # Guardar la receta en session_state
                    st.session_state.recipe_data = recipe_data
                    # Mostrar la receta inmediatamente
                    display_recipe(recipe_data)
                else:
                    st.error("No se pudo generar una receta. La respuesta de la IA no fue válida. Inténtalo de nuevo.")

            except Exception as e:
                st.error(f"Ocurrió un error inesperado: {e}")
    elif submit_button and uploaded_file is None:
        st.warning("Por favor, sube una imagen primero.")

if __name__ == "__main__":
    main()