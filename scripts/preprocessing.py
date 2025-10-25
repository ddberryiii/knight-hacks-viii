import pandas as pd
import numpy as np
import re
import pickle

# Load raw data from pickle into a dataframe
df = pd.read_pickle('../data/raw_data.pkl')

# Remove useless columns: anime_url, image_url, scored_by, favorites, rank
columns_to_drop = [
    'anime_url',
    'image_url',
    'scored_by',
    'favorites',
    'rank',
]
df = df.drop(columns=columns_to_drop, axis=1)

# Remove Special Characters
def clean_text(text):
    if pd.isna(text):
        return ''
    text = text.lower()
    text = re.sub(r'[^a-z0-9\s]', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text


for col in df.select_dtypes(include='object').columns:
    if col == 'synopsis':
        continue
    df[col] = df[col].astype(str).apply(clean_text)

# Change premiered to just year
def extract_year(premiered):
    if pd.isna(premiered):
        return np.nan
    match = re.search(r'(19|20)\d{2}', str(premiered))
    return int(match.group(0)) if match else np.nan


df['premiered'] = df['premiered'].apply(extract_year)

# Change duration to an integer of total minutes
def parse_duration(duration):
    if pd.isna(duration):
        return np.nan
    duration = duration.lower()

    hours = re.search(r'(\d+)\s*hr', duration)
    mins = re.search(r'(\d+)\s*min', duration)

    total_minutes = 0
    if hours:
        total_minutes += int(hours.group(1)) * 60
    if mins:
        total_minutes += int(mins.group(1))

    return total_minutes if total_minutes > 0 else np.nan


df['duration'] = df['duration'].apply(parse_duration)

# Make numbers integers
df['score'] = pd.to_numeric(df['score'], errors='coerce')
df['episodes'] = pd.to_numeric(df['episodes'], errors='coerce')

# Clipping data at the 99th percentile to stop outliers
cols_to_clip = ['members', 'popularity', 'episodes']

for col in cols_to_clip:
    upper = df[col].quantile(0.99)
    lower = df[col].quantile(0.01)
    df[col] = df[col].clip(lower=lower, upper=upper)

# Fill missing data with blanks
df = df.fillna({
    'english_name': '',
    'japanese_names': '',
    'genres': '',
    'themes': '',
    'demographics': '',
    'duration': df['duration'].median(),
    'synopsis': '',
    'episodes': df['episodes'].median(),
    'studios': '',
    'source': '',
    'producers': '',
    'premiered': 0,
    'type': '',
    'rating': '',
})

# Drop useless, almost blank animes
df = df.dropna(subset=['name', 'score'])
df = df[(df['genres'] != '') | (df['synopsis'] != '')]

# Drop duplicate anime entries based on anime_id
df = df.drop_duplicates(subset='anime_id', keep='first').reset_index(drop=True)

# Cleaning up spacing and formatting of some data
# Making commas spaced evenly, forcing all to lowercase
def clean_list_column(text):
    if pd.isna(text):
        return ''
    return ', '.join([x.strip().lower() for x in str(text).split(',')])


# Applying formatting rules to necessary areas
for col in ['genres', 'themes', 'demographics', 'studios']:
    df[col] = df[col].apply(clean_list_column)

# Saving Cleaned Data
df.to_pickle('../data/cleaned_data.pkl')
df.to_parquet("../data/cleaned_data.parquet", engine='pyarrow', compression='snappy')