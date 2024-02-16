import streamlit as st
import pandas as pd
from io import StringIO
import json

# Streamlit app title
st.title('CSV Bio Filter App')

# File uploader allows user to add their own CSV
uploaded_file = st.file_uploader("Choose a CSV file", type="csv")

# Input fields for users to define "include" and "exclude" keywords
include_keywords = st.text_area("Include in bio", "")
exclude_keywords = st.text_area("Exclude in bio", "")

# Input fields for minimum number of followers and tweets
col1, col2 = st.columns(2)
with col1:
    include_location = st.text_area("Include in location", "")
with col2:
    exclude_location = st.text_area("Exclude in location", "")

# Checkboxes for including or excluding empty locations
col1, col2 = st.columns(2)
with col1:
    include_empty_location = st.checkbox("Include empty locations")
with col2:
    exclude_empty_location = st.checkbox("Exclude empty locations")

col1, col2 = st.columns(2)
with col1:
    min_followers = st.number_input("Min # of followers", min_value=0, value=0, step=1)
with col2:
    min_tweets = st.number_input("Min # of tweets", min_value=0, value=0, step=1)

def apply_filtering(df, include_list, exclude_list, min_followers, min_tweets, include_loc, exclude_loc, include_empty_loc, exclude_empty_loc):
    if include_list:
        pattern_include = '|'.join(include_list)
        df = df[df['description'].str.contains(pattern_include, case=False, na=False)]
    if exclude_list:
        pattern_exclude = '|'.join(exclude_list)
        df = df[~df['description'].str.contains(pattern_exclude, case=False, na=False)]
    
    # Parse the "public_metrics" column and filter by followers and tweets
    metrics_df = pd.json_normalize(df['public_metrics'].apply(json.loads))
    df['followers_count'] = metrics_df['followers_count']
    df['tweet_count'] = metrics_df['tweet_count']
    df = df[(df['followers_count'] >= min_followers) & (df['tweet_count'] >= min_tweets)]
    
    # Filter by location
    if include_loc:
        pattern_include_loc = '|'.join(include_loc)
        df = df[df['location'].str.contains(pattern_include_loc, case=False, na=False)]
    if exclude_loc:
        pattern_exclude_loc = '|'.join(exclude_loc)
        df = df[~df['location'].str.contains(pattern_exclude_loc, case=False, na=False)]
    
    # Handling empty locations
    if include_empty_loc:
        df = df[(df['location'].isna()) | (df['location'] != '')]
    if exclude_empty_loc:
        df = df[df['location'].notna() & (df['location'] != '')]
    
    return df

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    original_rows = len(df)

    # Button to calculate the filtered DataFrame
    if st.button("Calculate"):
        include_list = [keyword.strip() for keyword in include_keywords.split(',')] if include_keywords else []
        exclude_list = [keyword.strip() for keyword in exclude_keywords.split(',')] if exclude_keywords else []
        include_loc = [loc.strip() for loc in include_location.split(',')] if include_location else []
        exclude_loc = [loc.strip() for loc in exclude_location.split(',')] if exclude_location else []
        filtered_df = apply_filtering(df, include_list, exclude_list, min_followers, min_tweets, include_loc, exclude_loc, include_empty_location, exclude_empty_location)
        
        st.write(f"Total rows after filtering: {len(filtered_df)} (from {original_rows} original rows)")
        st.write("Preview of filtered data:")
        st.dataframe(filtered_df.head(10))

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
