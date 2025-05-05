# import libraries
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from wordcloud import WordCloud, STOPWORDS
import PyPDF2
from docx import Document
import base64
from io import BytesIO
from collections import Counter

# ---------- File Reading Functions ----------
def read_pdf(file):
    pdf_reader = PyPDF2.PdfReader(file)
    text = ''
    for page in pdf_reader.pages:
        text += page.extract_text()
    return text

def read_docx(file):
    doc = Document(file)
    return '\n'.join(para.text for para in doc.paragraphs)

def read_txt(file):
    return file.read().decode('utf-8')

def read_csv(file):
    df = pd.read_csv(file)
    return ' '.join(df.astype(str).values.flatten())

# ---------- Helper Functions ----------
def filter_stopwords(text, stopwords):
    words = text.split()
    filtered = [word for word in words if word.lower() not in stopwords and word.isalpha()]
    return ' '.join(filtered), filtered

def create_download_link(image, filename='wordcloud.png'):
    buffered = BytesIO()
    image.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode()
    return f'<a href="data:file/png;base64,{img_str}" download="{filename}">📥 Download WordCloud</a>'

# ---------- App Layout ----------
st.set_page_config(page_title="Word Cloud Generator", layout="wide")

# Sidebar
st.sidebar.title("⚙️ Customization Settings")
st.sidebar.markdown("You can configure your word cloud below:")

stopwords_input = st.sidebar.text_area("✏️ Extra Stopwords (comma-separated)", value="the, and, is, in, to, of")
custom_stopwords = set(STOPWORDS).union(set(map(str.strip, stopwords_input.split(','))))

width = st.sidebar.slider("🌐 Image Width", 400, 2000, 800)
height = st.sidebar.slider("🌐 Image Height", 200, 1000, 400)
max_words = st.sidebar.slider("🔢 Max Words", 10, 200, 100)
background_color = st.sidebar.selectbox("🎨 Background Color", ["white", "black", "blue", "red"])
file_name = st.sidebar.text_input("📁 Output Filename", value="wordcloud.png")

st.sidebar.markdown("---")
st.sidebar.markdown("👨‍💻 Created by: M Jawad")

# ---------- Main Content ----------
st.title("☁️ Word Cloud Generator")
st.markdown("""
Welcome to the **Word Cloud Generator App**!  
Upload a document (PDF, DOCX, TXT, or CSV), customize the settings in the sidebar, and generate a word cloud with frequency analysis.
""")

uploaded_file = st.file_uploader("📄 Upload your file here", type=["pdf", "docx", "txt", "csv"])

if not uploaded_file:
    st.info("Please upload a file to begin.")
    st.stop()

# Show progress/loading bar while processing
with st.spinner("Processing file..."):
    file_type = uploaded_file.type
    if file_type == "application/pdf":
        text = read_pdf(uploaded_file)
    elif file_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        text = read_docx(uploaded_file)
    elif file_type == "text/plain":
        text = read_txt(uploaded_file)
    elif file_type == "text/csv":
        text = read_csv(uploaded_file)
    else:
        st.error("Unsupported file type.")
        st.stop()

# Text preview
st.subheader("📜 Text Preview")
st.text_area("First 1000 characters of your document:", text[:1000], height=150)

# Filter and process text
filtered_text, word_list = filter_stopwords(text, custom_stopwords)
word_counts = Counter(word_list)
word_freq_df = pd.DataFrame(word_counts.items(), columns=['Word', 'Frequency']).sort_values(by='Frequency', ascending=False)

# Generate word cloud
wordcloud = WordCloud(width=width, height=height, max_words=max_words,
                      background_color=background_color).generate(filtered_text)

# Display word cloud
st.subheader("🌈 Word Cloud Output")
fig, ax = plt.subplots(figsize=(width / 100, height / 100))
ax.imshow(wordcloud, interpolation='bilinear')
ax.axis('off')
st.pyplot(fig)

# Download link
st.markdown(create_download_link(wordcloud.to_image(), filename=file_name), unsafe_allow_html=True)

# Word Frequency Table
st.subheader("📊 Word Frequency Table")
st.dataframe(word_freq_df.reset_index(drop=True))
