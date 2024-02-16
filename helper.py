from io import StringIO
import json
from datetime import datetime
import pandas as pd

import pandas as pd
import json

def apply_filtering(df, include_list, exclude_list, include_list_and, exclude_list_and, min_followers, min_tweets, include_loc, exclude_loc, empty_location_option):
    # Apply filters based on description keywords
    if include_list:
        pattern_include = '|'.join(include_list)
        df = df[df['description'].str.contains(pattern_include, case=False, na=False)]
    if exclude_list:
        pattern_exclude = '|'.join(exclude_list)
        df = df[~df['description'].str.contains(pattern_exclude, case=False, na=False)]

    # Apply AND logic for include and exclude lists
    if include_list_and:
        df = df[df['description'].apply(lambda x: all(word in x.lower() for word in include_list_and))]
    for keyword in exclude_list_and:
        df = df[~df['description'].str.contains(keyword, case=False, na=False)]

    # Normalize and filter by public metrics
    metrics_df = pd.json_normalize(df['public_metrics'].apply(safe_json_loads))
    df['followers_count'] = metrics_df['followers_count']
    df['tweet_count'] = metrics_df['tweet_count']
    df = df[(df['followers_count'] >= min_followers) & (df['tweet_count'] >= min_tweets)]

    # Begin location filtering adjustments
    if 'location' in df.columns:
        df['location'] = df['location'].fillna('')  # Ensure no NaN values to simplify logic

    # First, exclude locations if specified
    if exclude_loc:
        pattern_exclude_loc = '|'.join(exclude_loc)
        df = df[~df['location'].str.contains(pattern_exclude_loc, case=False, na=True)]

    # Then, include locations if specified
    if include_loc:
        pattern_include_loc = '|'.join(include_loc)
        df_included = df[df['location'].str.contains(pattern_include_loc, case=False, na=False)]
        df = df_included

    # Handling empty locations
    if empty_location_option == 'Include':
        # Already handled by filling NaN with empty strings
        pass
    elif empty_location_option == 'Exclude':
        df = df[df['location'] != '']
    elif empty_location_option == 'Only':
        df = df[df['location'] == '']

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

def safe_json_loads(x):
    try:
        return json.loads(x) if isinstance(x, str) and x.strip() != '' else {}
    except json.JSONDecodeError:
        return {}