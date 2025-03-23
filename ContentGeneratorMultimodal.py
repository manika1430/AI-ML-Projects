import streamlit as st
import os
import base64
from dotenv import load_dotenv
from google import genai
from google.genai import types
from PIL import Image
from io import BytesIO


load_dotenv(dotenv_path='.env', encoding='utf-16')
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

client = genai.Client(api_key = GEMINI_API_KEY)

st.title(" AI Image Generator")
user_prompt= st.text_input("What do you want to generate image for?")

if st.button("Generate Image"):
    if not user_prompt:
        st.warning("Please enter the prompt!")
    else:
        try:
            with st.spinner("Generating image..."):
                response = client.models.generate_content(
                model="gemini-2.0-flash-exp-image-generation",
                contents=user_prompt,
                config=types.GenerateContentConfig(
                    response_modalities=['Text', 'Image']
                )
            )
            
            st.subheader("Generated Image")
            for part in response.candidates[0].content.parts:
                if part.text is not None:
                    st.write(part.text)
                elif part.inline_data is not None:
                    base64_data = part.inline_data.data
                    binary_data = base64.b64decode(base64_data)
                    image_data = BytesIO(binary_data)
                    image = Image.open(image_data)
                    st.image(image)
                
        except Exception as e:
           st.error(f"An error occurred: {e}")


st.title("AI Image Caption Generator")
uploaded_image=st.file_uploader("Upload the image for caption generation ", type=["png", "jpg", "jpeg"])

if uploaded_image:
    image=Image.open(uploaded_image)
    st.image(image)

    if st.button("Generate Caption"):
        try:
            with st.spinner("Generating the caption....."):
                response=client.models.generate_content(
                    model="gemini-2.0-flash",
                    contents=["What is this image?", image])
                st.subheader("Generated Caption")
                st.write(response.text)

        except Exception as e:
            print(f"Exception generating caption: {e}")
            st.error("Error generating caption")


st.title("AI YouTube video summarizer")
youTube_url= st.text_input("Enter the youTube url to generate summary")

if st.button("Generate summary"):
    if not youTube_url:
        st.warning("Please enter the youTube url to generate summary")

    else:
        try:
            with st.spinner("Generating the summary......."):
             response = client.models.generate_content(
                model='models/gemini-2.0-flash',
                contents=types.Content(
                    parts=[
                        types.Part(text='Can you summarize this video?'),
                        types.Part(
                            file_data=types.FileData(file_uri=youtube_url)
                        )
                    ]
                )
            )
            st.subheader("Generated Summary")
            st.write(response.text)

        except Exception as e:
            print(f"Exception generating youTube video summary :{e}")
            st.error("Error generating youTube video summary")
            
        

