import streamlit as st
import pandas as pd
from helper import apply_filtering, generate_filename, to_csv


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
    exclude_keywords = st.text_input("Exclude in bio", "crypto, cryptocurrency, bitcoin, btc")
with col2:
    exclude_keywords_and = st.text_input("Also exclude", "")


# Input fields for minimum number of followers and tweets
col1, col2 = st.columns(2)
with col1:
    include_location = st.text_input("Include location", "Alabama, Alaska, Arizona, Arkansas, California, Colorado, Connecticut, Delaware, Florida, Georgia, Hawaii, Idaho, Illinois, Indiana, Iowa, Kansas, Kentucky, Louisiana, Maine, Maryland, Massachusetts, Michigan, Minnesota, Mississippi, Missouri, Montana, Nebraska, Nevada, New Hampshire, New Jersey, New Mexico, New York, North Carolina, North Dakota, Ohio, Oklahoma, Oregon, Pennsylvania, Rhode Island, South Carolina, South Dakota, Tennessee, Texas, Utah, Vermont, Virginia, Washington, West Virginia, Wisconsin, Wyoming, AL, AK, AZ, AR, CA, CO, CT, DE, FL, GA, HI, ID, IL, IN, IA, KS, KY, LA, ME, MD, MA, MI, MN, MS, MO, MT, NE, NV, NH, NJ, NM, NY, NC, ND, OH, OK, OR, PA, RI, SC, SD, TN, TX, UT, VT, VA, WA, WV, WI, WY, United States, US, USA, The USA, United Kingdom, UK, England, Canada, CA, Australia, AU, Ireland, IE, New Zealand, NZ, Singapore, SG, Malta, MT, Bahamas, BS, Barbados, BB, Cyprus, CY, Luxembourg, LU, Switzerland, CH, Belgium, BE, Netherlands, NL, Sweden, SE, Norway, NO, Denmark, DK, Finland, FI, New York, New York City, NYC, Los Angeles, LA, Chicago, Houston, Phoenix, Philadelphia, San Antonio, San Diego, Dallas, San Jose, Austin, Jacksonville, Fort Worth, Columbus, Charlotte, San Francisco, Indianapolis, Seattle, Denver, Washington D.C., Boston, El Paso, Nashville, Detroit, Oklahoma City, Portland, Las Vegas, Memphis, Louisville, Baltimore, Milwaukee, Albuquerque, Tucson, Fresno, Sacramento, Kansas City, Mesa, Atlanta, Omaha, Colorado Springs, Raleigh, Miami, Long Beach, Virginia Beach, Oakland, Minneapolis, Tulsa, Arlington, Tampa, London, Birmingham, Manchester, Glasgow, Liverpool, Edinburgh, Leeds, Bristol, Sheffield, Cardiff, Toronto, Montreal, Vancouver, Calgary, Ottawa, Edmonton, Sydney, Melbourne, Brisbane, Perth, Adelaide, Dublin, Cork, Auckland, Wellington, Christchurch, Singapore City, Valletta, Nassau, Bridgetown, Nicosia, Luxembourg City, Zurich, Geneva, Brussels, Antwerp, Amsterdam, Rotterdam, Stockholm, Gothenburg, Oslo, Bergen, Copenhagen, Aarhus, Helsinki, Tampere")
    
with col2:
    exclude_location = st.text_input("Exclude location", "India, Africa, Nigeria, Singapore, Philippines, China, Russia, Belarus, Pakistan, Bangladesh, Venezuela, Iran, Iraq, Syria, Afghanistan, Sudan, North Korea, Myanmar, Yemen, Libya, Somalia, Zimbabwe, Haiti, Honduras, Guatemala, El Salvador, Nicaragua, Mongolia, Papua New Guinea")

# Checkboxes for including or excluding empty locations
empty_location_option = st.radio(
    "Empty locations",
    ('Include', 'Exclude', 'Only', 'No preference')
)

col1, col2 = st.columns(2)
with col1:
    min_followers = st.number_input("Min # of followers", min_value=0, value=100, step=25)
with col2:
    min_tweets = st.number_input("Min # of tweets", min_value=0, value=200, step=25)


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
        st.dataframe(filtered_df.head(20))

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
