import streamlit as st
import os
from dotenv import load_dotenv
from google import genai
from PIL import Image
from langchain_core.output_parsers import StrOutputParser
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate


load_dotenv(dotenv_path='.env', encoding='utf-16')
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")


from langchain_groq import ChatGroq
llm=ChatGroq(model_name="llama3-8b-8192", api_key=GROQ_API_KEY)

client = genai.Client(api_key = GEMINI_API_KEY)


def identify_dish(image):
    """Identify the dish using Google's Gemini model."""
    response=client.models.generate_content(
                    model="gemini-2.0-flash",
                    contents=["What is this dish? Give dish name only", image])
    return response.text.strip()

def get_recipe(dish_name):
    """Generate a recipe based on the identified dish using GROQ."""
    recipe_prompt=ChatPromptTemplate([("system","You are a helpful chef."), ("user", "Give me a detailed recipe for {dish_name}, including ingredients, steps, and cooking time.")])
    
    dish_chain = recipe_prompt | llm| StrOutputParser()
    return dish_chain.invoke({"dish_name": dish_name})

def get_nutrition(dish_name):
    """Fetch nutrition details for the identified dish."""
    nutritional_prompt=ChatPromptTemplate([("system","You are a helpful nutritionist."), ("user", "Give me a detailed nutritional values for {dish_name} and do not include Ingredients list")])
    
    nutrition_chain = nutritional_prompt | llm| StrOutputParser()
    return nutrition_chain.invoke({"dish_name": dish_name})

def getTopYouTubeVideos(dish_name):
    """Get top rated video recipes of dish."""
    system_message="You are a helpful assistant that provides users with the top 5 best-rated YouTube videos for a given recipe. Search for the most relevant and highly-rated YouTube videos based on views, likes, and engagement. Return the video title, a short description, and the YouTube link for each. Ensure that the results are recent and high quality.Give ratings, views and likes in separate lines."
    video_prompt=ChatPromptTemplate([("system", system_message), ("user", "Find the best-rated YouTube videos for making {dish_name}. Give atmost 3 results")])
    
    video_chain = video_prompt | llm| StrOutputParser()
    return video_chain.invoke({"dish_name": dish_name})


st.title(" &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp;  :rainbow[_DISHCOVERY_] :ramen: 🔍")
marquee_html = """
    <marquee style='font-size:24px; color: #ff5733; font-weight: bold'>
        Unveil Recipes & Nutrition Instantly!
    </marquee>
"""

st.components.v1.html(marquee_html, height=50)

st.markdown("""
    <style>
    [data-testid="stFileUploader"] label p {
        font-size: 24px;
        font-weight: bold;
        color: #80d300
    }
    .stCodeBlock div {
        font-size: 30px !important;
        font-weight: bold;
    }
    [data-testid="stHeading"] h3 {
        color: #BA3A3A;
        font-size: 24px;
        font-weight: bold;
        padding: 10px 0px;
        background-color: #f0f2f6;
        padding-left: 10px;
        border-radius: 5px;
    }

    </style>

    
    """, unsafe_allow_html=True)

dish_image=st.file_uploader("Upload the image to get recipe and nutrition details", type=["png", "jpg", "jpeg"])

if dish_image:
    image=Image.open(dish_image)
    st.image(image)
    dish_name=""

    if st.button("Generate recipe and nutrtional details ", type="primary"):
        try:
            with st.spinner("Indentifying dish....."):
                dish_name=identify_dish(image)
                st.code(f"Your dish is - {dish_name}")
            with st.spinner("Generating recipe....."):
                recipe_response=get_recipe(dish_name)
                st.subheader(f"Here is your recipe for {dish_name} !")
                st.write(recipe_response)
            with st.spinner("Generating nutritional values..."):
                nutrition_response=get_nutrition(dish_name)
                st.subheader(f"Below are the nutritional values of {dish_name} !")
                st.write(nutrition_response)
            with st.spinner("Finding best videos of the recipe...."):
                urls=getTopYouTubeVideos(dish_name)
                st.subheader("Would you like to see the recipe in video?")
                st.markdown(f"#### Top rated videos of {dish_name} are-")
                st.write(urls)
               
        except Exception as e:
            print(f"Exception in Dishcovering : {e}")
            st.error("Error in Dishcovering")

    
        
                





