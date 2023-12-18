import streamlit as st
#from function import graph_urls
import requests
import base64
import os
from PIL import Image
import io
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time

def scrape_graph_urls(url):
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(options=chrome_options)
    graph_urls = []

    try:
        driver.get(url)
        time.sleep(5)

        try:
            cookie_button = driver.find_element(By.XPATH, '//button[contains(text(), "Got It")]')
            cookie_button.click()
            time.sleep(2)
        except Exception as e:
            print("Cookie consent button not found or already accepted.", e)

        graph_elements = driver.find_elements(By.XPATH, '//div[@class="wp-caption alignnone"]/img')

        for element in graph_elements:
            graph_urls.append(element.get_attribute('src'))

    finally:
        driver.quit()

    return graph_urls




# OpenAI API Key
api_key = "XXXXXX"

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
              "text": "Act as a Data Scientist, Please provide a detailed, yet clear and simple interpretation of the chart. Assume you are explaining this graph to a non-technical audience."
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
      "max_tokens": 1024
    }

    response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
    return response.json()['choices'][0]['message']['content']

def download_image(image_url):
    response = requests.get(image_url)
    image = Image.open(io.BytesIO(response.content))
    image.save(f"graph.png")
    return "graph.png"


def main():
    st.title('Graph Analysis Tool')
    url = st.text_input('Enter the URL of the webpage with graphs')

    if st.button('Scrape and Analyze Graphs'):
        if url:
            graph_urls = scrape_graph_urls(url)
            for i, graph_url in enumerate(graph_urls, start=1):
                graph_path = download_image(graph_url)  # Download each graph
                interpretation = get_interpretation(graph_path)  # Analyze the downloaded graph
                st.image(graph_path, caption=f'Graph {i}', use_column_width=True)  # Display the graph
                st.write(interpretation)  # Display the analysis
        else:
            st.write("Please enter a URL")

if __name__ == "__main__":
    main()

