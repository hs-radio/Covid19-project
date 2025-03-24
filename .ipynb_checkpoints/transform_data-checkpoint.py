import pandas as pd
import numpy as np

# there are clear errors in the data, this function fixes.
# anomalous non-zeros: when the vaccinations or boosters have periods of non-zero values before any vaccines were administered.
def specific_corrections(df_ppl_vac_p100, df_boosters_p100):

    # anomalous non-zeros.
    for country in df_ppl_vac_p100.columns:
        # Handle people vaccinated corrections
        decreasing_mask_ppl = df_ppl_vac_p100[country] < df_ppl_vac_p100[country].cummax()
        if decreasing_mask_ppl.any():  # Check if any decrease occurs
            first_decrease_index_ppl = decreasing_mask_ppl.idxmax()  # Get first decrease (timestamp)
            df_ppl_vac_p100.loc[:first_decrease_index_ppl, country] = 0  # Use .loc to modify by timestamp

        # Handle boosters corrections
        decreasing_mask_boosters = df_boosters_p100[country] < df_boosters_p100[country].cummax()
        if decreasing_mask_boosters.any():  # Check if any decrease occurs
            first_decrease_index_boosters = decreasing_mask_boosters.idxmax()  # Get first decrease (timestamp)
            df_boosters_p100.loc[:first_decrease_index_boosters, country] = 0  # Use .loc to modify by timestamp

    return df_ppl_vac_p100, df_boosters_p100


    


# process data into a useable form.
def process_data_by_country(tb, features):
    
    # Convert indexes to columns
    df = tb[features].reset_index()

    # Create a dictionary to store pivoted data for each feature
    pivoted_data = {}

    # Convert to pivot for time series
    for feature in features:            
        df[feature] = df[feature].ffill()
        
        # Pivot the data for each feature and store it in the dictionary
        pivoted_data[feature] = df.pivot_table(index="date", columns="country", values=feature, observed=False).ffill()
        
        # Drop non-countries from the pivoted data
        pivoted_data[feature] = pivoted_data[feature].drop(columns=non_countries, errors='ignore')

        # # change the datetime to the pandas formate
        # pivoted_data[feature]['date'] = pd.to_datetime(pivoted_data[feature]["date"])
    
    # Return each feature's DataFrame as a separate variable
    return tuple(pivoted_data[feature] for feature in features)




# List of non-countries that appear in data.
non_countries = [
    "Africa", "Asia", "Asia excl. China", "European Union (27)", 
    "High-income countries", "Low-income countries", "Lower-middle-income countries", 
    "North America", "Oceania", "South America", "World", "Upper-middle-income countries",
    "Falkland Islands", "Faroe Islands", "French Guiana", "French Polynesia", 
    "Guadeloupe", "Guam", "Isle of Man", "Jersey", "Liechtenstein", 
    "Macao", "Mayotte", "Micronesia (country)", "Montserrat", "New Caledonia", "Niue", 
    "Northern Mariana Islands", "Pitcairn", "Puerto Rico", "Reunion", 
    "Saint Barthelemy", "Saint Helena", "Saint Kitts and Nevis", "Saint Lucia", 
    "Saint Martin (French part)", "Saint Pierre and Miquelon", "Sint Maarten (Dutch part)", 
    "South America", "Tokelau", 
    'Marshall Islands', 'American Samoa', 'World excl. China, South Korea, Japan and Singapore', 'Palau', 'Vatican', 
    'Martinique', 'World excl. China and South Korea', 'United States Virgin Islands', 'World excl. China',
    'Anguilla', 'Bonaire Sint Eustatius and Saba', 'British Virgin Islands', 'Europe',
]