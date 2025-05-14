import pandas as pd

# Load the raw CSV file
df = pd.read_csv('data/raw_sessions.csv')  # Adjust the path if needed

# Convert column names to lowercase
df.columns = [col.lower() for col in df.columns]

# Convert 'date' column to datetime format
df['date'] = pd.to_datetime(df['date'], format='%Y%m%d')

# Fill missing values
df['pageviews'] = df['pageviews'].fillna(0)
df['timeonsite'] = df['timeonsite'].fillna(0)

# Create a 'converted' column: 1 if a transaction occurred, 0 otherwise
df['converted'] = df['transactions'].fillna(0).astype(int)

# Normalize 'transactionrevenue' from micros to dollars
df['revenue'] = df['transactionrevenue'].fillna(0) / 1_000_000

# Create a simplified funnel_stage column based on pageviews
def classify_stage(pv):
    if pv == 0:
        return "Bounced"
    elif pv < 5:
        return "Browsed"
    elif pv < 10:
        return "Engaged"
    else:
        return "Deep Engagement"

df['funnel_stage'] = df['pageviews'].apply(classify_stage)

# Save the cleaned data to a new CSV
df.to_csv('data/cleaned_sessions.csv', index=False)

print("Cleaned data saved to 'cleaned_sessions.csv'")