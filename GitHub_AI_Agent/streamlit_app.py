import streamlit as st
import pandas as pd
from data_cleaning.cleaning_agent import AIDataCleaningAgent

# 🚀 Set up the Streamlit page
st.set_page_config(page_title="AI-Powered Data Cleaning", page_icon="✨", layout="wide")

# 🏆 App Title
st.title("🚀 AI-Powered Data Cleaning Web App")
st.write("Upload your dataset, and let AI clean it automatically!")

# 📂 Upload File Widget
uploaded_file = st.file_uploader("📂 Upload your dataset (CSV or Excel)", type=["csv", "xlsx"])

if uploaded_file:
    # 🔍 Load Dataset
    df = pd.read_csv(uploaded_file) if uploaded_file.name.endswith(".csv") else pd.read_excel(uploaded_file)
    
    st.write("📊 **Raw Data Preview:**")
    st.dataframe(df.head())

    # 🧼 Clean Data Button
    if st.button("🔍 Clean Data"):
        with st.spinner("🛠️ AI is cleaning your data... Please wait..."):
            cleaning_agent = AIDataCleaningAgent(df)
            cleaned_df = cleaning_agent.clean_data()
        
        st.success("✅ Data cleaning complete!")
        st.write("📊 **Cleaned Data Preview:**")
        st.dataframe(cleaned_df.head())

        # 📩 Download cleaned data
        csv = cleaned_df.to_csv(index=False).encode("utf-8")
        st.download_button(label="📥 Download Cleaned Data", data=csv, file_name="cleaned_data.csv", mime="text/csv")

st.markdown("---")
st.info("🔹 This AI-powered app automatically cleans missing values, removes outliers, and ensures correct column types using OpenAI and Machine Learning.")

