import streamlit as st
import pandas as pd
from io import StringIO

# Streamlit app title
st.title('CSV Bio Filter App')

# File uploader allows user to add their own CSV
uploaded_file = st.file_uploader("Choose a CSV file", type="csv")

# Input fields for users to define "include" and "exclude" keywords
include_keywords = st.text_area("Include in bio", "Enter keywords separated by commas, e.g., Python, Data Science")
exclude_keywords = st.text_area("Exclude in bio", "Enter keywords separated by commas, e.g., Java, Frontend")

def apply_filtering(df, include_list, exclude_list):
    if include_list:
        pattern_include = '|'.join(include_list)
        df = df[df['description'].str.contains(pattern_include, case=False, na=False)]
    if exclude_list:
        pattern_exclude = '|'.join(exclude_list)
        df = df[~df['description'].str.contains(pattern_exclude, case=False, na=False)]
    return df

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    original_rows = len(df)

    # Button to calculate the filtered DataFrame
    if st.button("Calculate"):
        include_list = [keyword.strip() for keyword in include_keywords.split(',')] if include_keywords else []
        exclude_list = [keyword.strip() for keyword in exclude_keywords.split(',')] if exclude_keywords else []
        filtered_df = apply_filtering(df, include_list, exclude_list)
        
        st.write(f"Total rows after filtering: {len(filtered_df)} (from {original_rows} original rows)")
        st.write("Preview of filtered data:")
        st.dataframe(filtered_df.head())  # Display the first few rows as a preview

        # Download button
        if len(filtered_df) > 0:
            def to_csv(df):
                output = StringIO()
                df.to_csv(output, index=False)
                return output.getvalue()
            
            csv = to_csv(filtered_df)
            st.download_button(
                label="Download filtered CSV",
                data=csv,
                file_name='filtered_data.csv',
                mime='text/csv',
            )
else:
    st.write("Please upload a CSV file to proceed.")
