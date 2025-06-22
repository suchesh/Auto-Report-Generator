from dotenv import load_dotenv
import os
import streamlit as st
import PyPDF2 as pdf
import google.generativeai as genai
import DB_Setup as db
import pandas as pd

# Streamlit app
st.set_page_config(page_title="Report Writer")


# Load environment variables and configure GenAI
load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
model = genai.GenerativeModel("gemini-2.0-flash-exp")


# Initialize Database only ONCE using st.session_state
if "database" not in st.session_state:
    st.session_state.database = db.Database()  # Create DB instance once
    st.write("Database configured successfully!")  # Only logs once

database = st.session_state.database  # Use the stored instance


def pdf_data(file):
    """Extract text from an uploaded PDF file."""
    if file is not None:
        reader = pdf.PdfReader(file)
        return "".join(page.extract_text() for page in reader.pages if page.extract_text())
    return None



def image_data(file):
    if file is not None:
        bytes_data = file.getvalue()
        image_parts = [
            {
                "mime_type" : file.type,
                "data" : bytes_data
            }
        ]
        return image_parts
    else:
        raise FileNotFoundError("NO file uploaded")


def excel_data(file):
    """Extract text content from an Excel file."""
    try:
        if file is not None:
            df = pd.read_excel(file)
            return df.to_string(index=False)
    except Exception as e:
        st.error(f"Error reading Excel file: {e}")
    return None


def generate_response(content,extra_query):
    """Generate a summary based on the content."""
    if content:
        combined_input = f"""User Query:\n Content:\n{content}\nGenerate a summary over the given content. 
                            this might be image or text or pdf or excel kind of extracted data
                            Be careful while provideing the summary
                            if its  an image : then provide summary on what is present in the image
                            Addtional Instructions : {extra_query}"""
        return model.generate_content(combined_input).text
    return "No valid content to process."



st.header("Report Writer")

# Sidebar Title
st.sidebar.title("Navigation")

# Select Option
option = st.selectbox("Select your input", ("Text", "PDF", "Image", "Excel"))

input_data = None
input_component = None
input_file = None

# Dynamically assign the input component based on selection
if option == "Text":
    input_data = st.text_area("Enter your text here:")
elif option == "PDF":
    input_component = st.file_uploader("Upload a PDF file", type=["pdf"])
    if input_component:
        input_file = input_component
        input_data = pdf_data(input_component)
elif option == "Image":
    input_component = st.file_uploader("Upload an Image", type=["jpg", "png", "jpeg"])
    if input_component:
        input_file = input_component
        input_data = image_data(input_component)
elif option == "Excel":
    input_component = st.file_uploader("Upload an Excel file", type=["xlsx", "xls"])
    if input_component:
        input_file = input_component
        input_data = excel_data(input_component)


# Store Data
if st.button("Store Data"):
    if input_data:
        extra_instruction = """Make the summary of the data as if you were real witness of the content
                                It should simulate real person view."""
        input_data_summary = generate_response(input_data,extra_instruction)
        if not input_file:
            database.store_data(input_data, input_data_summary)
        else:
            database.store_data(input_file.name, input_data_summary)
        st.success("Data stored successfully!")
    else:
        st.warning("No valid input data to store.")


# Generate report button
user_query = st.text_input("Enter your query:")
if st.button("Get Report"):
    if user_query:
        retrieved_data = database.retrieve_data()
        extra_instruction = """You were given already existing summaries of different occasions.
                                Now you need to generate a real-time Report for Presentation Ready.
                                If you want , you can make partions in the report regarding the timeline only if needeed.
                                Make sure it should simulate real time Report."""
        overall_report = generate_response(retrieved_data,extra_instruction)
        if retrieved_data:
            st.header("The Response is:")
            st.write(overall_report)
        else:
            st.warning("No matching data found in the database.")
    else:
        st.warning("Please enter a query before generating the report.")