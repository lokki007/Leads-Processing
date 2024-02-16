import streamlit as st
import pandas as pd
from io import StringIO
import json
from datetime import datetime


# Set the page to wide mode
st.set_page_config(layout="wide")

# Streamlit app title
st.title('CSV Bio Filter App')

# File uploader allows user to add their own CSV
uploaded_file = st.file_uploader("Choose a CSV file", type="csv")

# Input fields for minimum number of followers and tweets
col1, col2 = st.columns(2)
with col1:
    include_keywords = st.text_input("Include in bio", "")
with col2:
    include_keywords_and = st.text_input("Also include", "")

# Input fields for minimum number of followers and tweets
col1, col2 = st.columns(2)
with col1:
    exclude_keywords = st.text_input("Exclude in bio", "")
with col2:
    exclude_keywords_and = st.text_input("Also exclude", "")


# Input fields for minimum number of followers and tweets
col1, col2 = st.columns(2)
with col1:
    include_location = st.text_input("Include location", "")
with col2:
    exclude_location = st.text_input("Exclude location", "")

# Checkboxes for including or excluding empty locations
empty_location_option = st.radio(
    "Empty locations",
    ('Include', 'Exclude', 'Only', 'No preference')
)

col1, col2 = st.columns(2)
with col1:
    min_followers = st.number_input("Min # of followers", min_value=0, value=0, step=1)
with col2:
    min_tweets = st.number_input("Min # of tweets", min_value=0, value=0, step=1)

def apply_filtering(df, include_list, exclude_list, include_list_and, exclude_list_and, min_followers, min_tweets, include_loc, exclude_loc, empty_location_option):
    if include_list:
        pattern_include = '|'.join(include_list)
        df = df[df['description'].str.contains(pattern_include, case=False, na=False)]
    if exclude_list:
        pattern_exclude = '|'.join(exclude_list)
        df = df[~df['description'].str.contains(pattern_exclude, case=False, na=False)]
    
    # Apply AND logic for include and exclude lists
    for keyword in include_list_and:
        df = df[df['description'].str.contains(keyword, case=False, na=False)]
    for keyword in exclude_list_and:
        df = df[~df['description'].str.contains(keyword, case=False, na=False)]
    
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
    
    # Handling empty locations based on the radio button selection
    if empty_location_option == 'Include':
        df = df[(df['location'].isna()) | (df['location'] != '')]
    elif empty_location_option == 'Exclude':
        df = df[df['location'].notna() & (df['location'] != '')]
    elif empty_location_option == 'Only':
        df = df[df['location'].isna()]
    
    return df

def generate_filename(include_list, exclude_list, include_list_and, exclude_list_and, min_followers, min_tweets, include_loc, exclude_loc, empty_location_option):
    timestamp = datetime.now().strftime("%m%d")
    filename = f"leads_{timestamp}"
    
    if include_list:
        filename += f"_inc-{'-'.join(include_list)}"
    if exclude_list:
        filename += f"_exc-{'-'.join(exclude_list)}"
    if include_list_and:
        filename += f"_andinc-{'-'.join(include_list_and)}"
    if exclude_list_and:
        filename += f"_andexc-{'-'.join(exclude_list_and)}"
    if min_followers > 0:
        filename += f"_minfollowers-{min_followers}"
    if min_tweets > 0:
        filename += f"_mintweets-{min_tweets}"
    if include_loc:
        filename += f"_incloc-{'-'.join(include_loc)}"
    if exclude_loc:
        filename += f"_excloc-{'-'.join(exclude_loc)}"
    if empty_location_option != 'No preference':
        filename += f"_{empty_location_option.lower()}emptyloc"
    
    filename += ".csv"
    return filename

def to_csv(df):
    output = StringIO()
    df.to_csv(output, index=False)
    return output.getvalue()


if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    original_rows = len(df)

    # Button to calculate the filtered DataFrame
    if st.button("Calculate"):
        include_list = [keyword.strip() for keyword in include_keywords.split(',')] if include_keywords else []
        exclude_list = [keyword.strip() for keyword in exclude_keywords.split(',')] if exclude_keywords else []
        include_list_and = [keyword.strip() for keyword in include_keywords_and.split(',')] if include_keywords_and else []
        exclude_list_and = [keyword.strip() for keyword in exclude_keywords_and.split(',')] if exclude_keywords_and else []
        include_loc = [loc.strip() for loc in include_location.split(',')] if include_location else []
        exclude_loc = [loc.strip() for loc in exclude_location.split(',')] if exclude_location else []
        filtered_df = apply_filtering(df, include_list, exclude_list, include_list_and, exclude_list_and, min_followers, min_tweets, include_loc, exclude_loc, empty_location_option)
        
        st.write(f"Total rows after filtering: {len(filtered_df)} (from {original_rows} original rows)")
        st.write("Preview of filtered data:")
        st.dataframe(filtered_df.head(10))

        # Download button
        if len(filtered_df) > 0:
            csv = to_csv(filtered_df)
            dynamic_filename = generate_filename(include_list, exclude_list, include_list_and, exclude_list_and, min_followers, min_tweets, include_loc, exclude_loc, empty_location_option)
            st.download_button(
                label="Download filtered CSV",
                data=csv,
                file_name=dynamic_filename,
                mime='text/csv',
            )
else:
    st.write("Please upload a CSV file to proceed.")
