import streamlit as st
import time
import mss
import anthropic
import base64
import os
from dotenv import load_dotenv

load_dotenv()
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

# Initialize Streamlit session state
if 'running' not in st.session_state:
    st.session_state['running'] = False
if 'results' not in st.session_state:
    st.session_state['results'] = []
if 'first_run' not in st.session_state:
    st.session_state['first_run'] = True

def make_api_req(img_file):
    image_url = img_file.read()
    image_media_type = "image/png"
    image_data = base64.b64encode(image_url).decode("utf-8")

    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

    message = client.messages.create(
        model="claude-3-haiku-20240307",
        max_tokens=1024,
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": image_media_type,
                            "data": image_data,
                        },
                    },
                    {
                "type": "text",
                "text": """You will be extracting patient information from an image file. I will provide the image file, and your task is to use OCR (Optical Character Recognition) to extract all the text from the image. Once you have the extracted text, parse through it to find the following key pieces of information:
                
                - Patient Name
                - Patient Age
                - Patient Date of Birth (DOB)
                - gender
                - Patient Contact Number
                - Appointment Date
                - Reason for Visit

                
                The image file path will be provided in the following format:
                
                
                After extracting the text from the image, search through it carefully to locate the key information listed above. If any of the information cannot be found, use "N/A" as the value for that field.
                
                Once you have found as much of the key information as possible, return it in JSON format. The JSON should have the following structure:
                
                {
                "name": patient_name,
                "age": patient_age,
                "gender": patient_gender,
                "contact": patient_contact,
                "appointment_date": appointment_date,
                "reason_for_visit": reason_for_visit
            }
                
                Remember to use "N/A" as the value for any fields that could not be found in the extracted text.
                
                Perform this task carefully and thoroughly, making sure to extract all the available information from the image. Double check the spelling of names and numbers to ensure accuracy. Provide the final result in valid JSON format as shown above."""
            }
                ],
            }
        ],
    )
    print(message.content[0])
    return message.content[0].text

# Function to take a screenshot and send to API
def take_and_send_screenshot():
    with mss.mss() as sct:
        screenshot = sct.shot(output='screenshot.png')

        with open("screenshot.png", "rb") as img_file:
            analysis_result = make_api_req(img_file)

        st.session_state.results = analysis_result

# Main function for the Streamlit app
def main():
    st.title("Dental App")

    with st.form("patient_info_form"):
        st.header("Patient Information")
        patient_name = st.text_input("Name")
        patient_age = st.number_input("Age", min_value=0, max_value=120)
        patient_gender = st.selectbox("Gender", ["Male", "Female", "Other"])
        patient_contact = st.text_input("Contact Number")
        
        st.header("Appointment Details")
        appointment_date = st.date_input("Appointment Date")
        reason_for_visit = st.text_area("Reason for Visit")

        submitted = st.form_submit_button("Submit")

        if submitted:
            st.write(f"Patient Name: {patient_name}")
            st.write(f"Age: {patient_age}")
            st.write(f"Gender: {patient_gender}")
            st.write(f"Contact: {patient_contact}")
            st.write(f"Appointment Date: {appointment_date}")
            st.write(f"Reason for Visit: {reason_for_visit}")

    
    st.header("Screenshot Analysis")
    
    if st.button("Start Analysis" if not st.session_state.running else "Stop Analysis"):
        if not st.session_state.running:
            st.session_state.running = True
            st.write("Started taking screenshots and analyzing...")
        else:
            st.session_state.running = False
            st.write("Stopped taking screenshots and analyzing.")
    
    while st.session_state.running:
        if st.session_state.first_run:
            st.session_state.first_run = False
            time.sleep(10)
        
        take_and_send_screenshot()
        st.write("Analysis Results:")
        st.write(st.session_state.results)
        
        time.sleep(60)  

if __name__ == "__main__":
    main()
