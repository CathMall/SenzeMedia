import streamlit as st
import requests
from PIL import Image
import io
from huggingface_hub import InferenceClient
from gtts import gTTS
import os
from transformers import pipeline

# Hugging Face API keys and endpoints
api_key = st.secrets["huggingface"]["api_key"]

# API URLs
blip_api_url = "https://api-inference.huggingface.co/models/nlpconnect/vit-gpt2-image-captioning"
flux_api_url = "https://api-inference.huggingface.co/models/black-forest-labs/FLUX.1-dev"
translation_api_url = "https://api-inference.huggingface.co/models/Helsinki-NLP/opus-mt-en-ar"
musicgen_api_url = "https://api-inference.huggingface.co/models/facebook/musicgen-small"
headers = {"Authorization": f"Bearer {api_key}"}

# Meta-Llama Chatbot
llama_model = "meta-llama/Meta-Llama-3-8B-Instruct"
client = InferenceClient(api_key=api_key)

# Function to generate an image using FLUX
def flux_generate_image(text_input):
    try:
        response = requests.post(flux_api_url, headers=headers, json={"inputs": text_input})
        response.raise_for_status()  # Raise an error for bad responses
        return response.content
    except Exception as e:
        st.error(f"Image generation error: {e}")
        return None

# Function to caption an image using BLIP
def blip_caption_image(image):
    try:
        response = requests.post(blip_api_url, headers=headers, data=image)
        response.raise_for_status()  # Raise an error for bad responses
        return response.json()
    except Exception as e:
        st.error(f"Captioning error: {e}")
        return None

# Function to handle chatbot conversation
def llama_chatbot(prompt):
    try:
        response = client.chat_completion(
            model=llama_model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=1000,
            stream=False
        )
        return response.choices[0].message['content']
    except Exception as e:
        st.error(f"Chatbot error: {e}")
        return "I'm sorry, I couldn't generate a response."

# Function to convert text to speech using gTTS
def text_to_speech(text):
    try:
        tts = gTTS(text, lang='en')
        tts_file = "story.mp3"
        tts.save(tts_file)
        return tts_file
    except Exception as e:
        st.error(f"Text-to-Speech error: {e}")
        return None

# Function to translate text from English to Arabic
def translate_to_arabic(text):
    try:
        translator = pipeline('translation_en_to_ar', model='Helsinki-NLP/opus-mt-en-ar')
        
        # Split the text into manageable chunks
        max_length = 500
        chunks = [text[i:i + max_length] for i in range(0, len(text), max_length)]
        
        # Translate each chunk
        translated_chunks = [translator(chunk)[0]['translation_text'] for chunk in chunks]
        
        # Join the translated chunks back together
        translated_text = " ".join(translated_chunks)
        return translated_text
    except Exception as e:
        st.error(f"Translation error: {e}")
        return None

# Function to generate music using MusicGen
def generate_music(genre_input):
    try:
        response = requests.post(musicgen_api_url, headers=headers, json={"inputs": genre_input})
        response.raise_for_status()  # Raise an error for bad responses
        return response.content
    except Exception as e:
        st.error(f"Music generation error: {e}")
        return None

# Enhanced Streamlit UI
st.set_page_config(page_title="Creative AI Suite", page_icon="🎨", layout="wide")

st.title("🎨 Creative AI Suite")
st.markdown("Unlock the power of AI for **image generation**, **story creation**, **music generation**, and **speech conversion**.")

# Use session state to preserve the selected option
if 'option' not in st.session_state:
    st.session_state.option = None  # Initialize the option

# Row layout for options
# Row layout for options
st.header("Choose an option:")
col1, col2, col3, col4, col5, col6 = st.columns(6)

with col1:
    if st.button("Create an Image and Story", key="create_image_story"):
        st.session_state.option = "Create an Image and Story from Your Description"

with col2:
    if st.button("Interactive AI Chat", key="interactive_ai_chat"):
        st.session_state.option = "Interactive AI Chat"

with col3:
    if st.button("Convert Text to Speech", key="convert_text_to_speech"):
        st.session_state.option = "Convert Text to Speech"

with col4:
    if st.button("Generate an Image", key="generate_image"):
        st.session_state.option = "Generate an Image"

with col5:
    if st.button("Translate to Arabic", key="translate_to_arabic"):
        st.session_state.option = "Translate to Arabic"

with col6:
    if st.button("Generate Music", key="generate_music"):
        st.session_state.option = "Generate Music"


# Add help tooltips to guide users
st.info("Select an option to interact with the AI tools.")

# Option handling
if st.session_state.option == "Create an Image and Story from Your Description":
    st.subheader("🖼️ Create an Image and Story")
    st.markdown("Describe the image you want, and we'll generate it for you along with a creative story.")
    description_input = st.text_input("🔎 Describe the image you want:")
    
    if st.button("Generate Image"):
        if description_input:
            with st.spinner("Generating image..."):
                generated_image = flux_generate_image(description_input)
                if generated_image:
                    image = Image.open(io.BytesIO(generated_image))
                    st.image(image, caption="Generated Image", use_column_width=True)

                    with st.spinner("✍️ Generating caption..."):
                        caption = blip_caption_image(generated_image)
                    
                    if caption and 'generated_text' in caption[0]:
                        title = caption[0]['generated_text']
                        st.write("### 🖋️ Caption (Title):", title)

                        with st.spinner("📖 Generating story..."):
                            story_script = llama_chatbot(f"Write a creative and useful story about: {title}.")
                            st.markdown("### 📜 Story Script:")
                            st.write(story_script)

                            # Translate the generated story to Arabic
                            with st.spinner("🌍 Translating story to Arabic..."):
                                arabic_translation = translate_to_arabic(story_script)
                            
                            if arabic_translation:
                                st.markdown("### 🌍 Arabic Translation:")
                                st.write(arabic_translation)

                        with st.spinner("🔊 Converting story to speech..."):
                            audio_file = text_to_speech(story_script)

                        if audio_file:
                            st.audio(audio_file, format="audio/mp3")
                            os.remove(audio_file)  # Cleanup after playing
                    else:
                        st.error("⚠️ Unable to generate caption for the image.")
        else:
            st.warning("Please provide a description to generate the image.")  

elif st.session_state.option == "Interactive AI Chat":
    st.subheader("🤖 Interactive AI Chat")
    st.markdown("Ask the AI any question, and it will respond with a creative answer.")
    user_input = st.text_input("💬 Enter your question or prompt:")
    
    if st.button("🚀 Submit"):
        if user_input:
            with st.spinner("🤖 AI is generating a response..."):
                response = llama_chatbot(user_input)
                if response:
                    st.markdown("### 💡 AI Response:")
                    st.success(f"🤖 {response}")  # Use emoji to enhance the feedback
        else:
            st.warning("Please enter a prompt to get started!")

elif st.session_state.option == "Generate an Image":
    st.subheader("🖼️ Generate an Image")
    st.markdown("Describe the image, and we will generate it for you.")
    image_description = st.text_input("🔎 Describe the image you want:")
    
    if st.button("Generate Image"):
        if image_description:
            with st.spinner("🔄 Generating image..."):
                generated_image = flux_generate_image(image_description)
                if generated_image:
                    image = Image.open(io.BytesIO(generated_image))
                    st.image(image, caption="Generated Image", use_column_width=True)

elif st.session_state.option == "Convert Text to Speech":
    st.subheader("🔊 Convert Text to Speech")
    st.markdown("Enter text to convert it into natural-sounding speech.")
    text_to_convert = st.text_area("📝 Enter the text you want to convert to speech:")
    
    if st.button("Convert"):
        if text_to_convert:
            with st.spinner("🔊 Converting text to speech..."):
                audio_file = text_to_speech(text_to_convert)
                if audio_file:
                    st.audio(audio_file, format="audio/mp3")
                    os.remove(audio_file)
        else:
            st.warning("Please enter the text to convert.")

elif st.session_state.option == "Translate to Arabic":
    st.subheader("🌍 Translate Text to Arabic")
    st.markdown("Enter the text you want to translate from English to Arabic.")
    text_to_translate = st.text_area("📝 Enter the text you want to translate:")
    
    if st.button("Translate"):
        if text_to_translate:
            with st.spinner("🌍 Translating text..."):
                arabic_translation = translate_to_arabic(text_to_translate)
                if arabic_translation:
                    st.markdown("### 🌍 Arabic Translation:")
                    st.write(arabic_translation)
        else:
            st.warning("Please enter the text to translate.")

elif st.session_state.option == "Generate Music":
    st.subheader("🎵 Generate Music")
    st.markdown("Enter a description of the music you want, and the AI will generate it for you.")
    genre_description = st.text_input("🔎 Describe the music genre or vibe:")
    
    if st.button("Generate Music"):
        if genre_description:
            with st.spinner("🎵 Generating music..."):
                generated_music = generate_music(genre_description)
                if generated_music:
                    st.audio(generated_music, format="audio/mp3")
        else:
            st.warning("Please provide a description to generate music.")
