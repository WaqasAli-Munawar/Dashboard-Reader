import streamlit as st
import requests
import base64
import os

# OpenAI API Key
api_key = "XXXXX"

# Function to encode the image
def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

# Function to get interpretation from OpenAI
def get_interpretation(image):
    base64_image = encode_image(image)

    headers = {
      "Content-Type": "application/json",
      "Authorization": f"Bearer {api_key}"
    }

    payload = {
      "model": "gpt-4-vision-preview",
      "messages": [
        {
          "role": "user",
          "content": [
            {
              "type": "text",
              "text": "As a Data Scientist, Please provide a detailed, yet clear and simple interpretation of the chart. Assume you are explaining this graph to a non-technical audience."
            },
            {
              "type": "image_url",
              "image_url": {
                "url": f"data:image/jpeg;base64,{base64_image}"
              }
            }
          ]
        }
      ],
      "max_tokens": 300
    }

    response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
    return response.json()['choices'][0]['message']['content']

# Streamlit app
def main():
    st.title('Data Visualization Analysis Tool')

    uploaded_files = st.file_uploader("Upload a Chart for Analysis", accept_multiple_files=True)

    for uploaded_file in uploaded_files:
        if uploaded_file is not None:
            st.image(uploaded_file, caption='Uploaded Chart', use_column_width=True)

            # Save uploaded file to disk
            with open(uploaded_file.name, "wb") as f:
                f.write(uploaded_file.getbuffer())
            
            # Get interpretation
            interpretation = get_interpretation(uploaded_file.name)
            st.write(interpretation)

if __name__ == "__main__":
    main()
