import pandas as pd
import numpy as np

# process data into a useable form.
def basic_processing(tb, features, correct_a_nz = False):
    
    # Select certain features, convert the indexes into rows, ffill the NAs
    df = tb[features].reset_index().ffill()
    
    # Remove rows where 'country' is in the list 'non_countries'
    df = df[~df['country'].isin(non_countries)]

    # Return each feature's DataFrame as a separate variable
    return df


# pre-process cases, deaths and vaccination data
def process_covid_data(tb_country_cases_deaths, tb_country_vac):

    # Cases and deaths data.
    #--------------------------------
    features_cd = ["new_cases", "new_deaths"]
    df_cd = basic_processing(tb_country_cases_deaths, features_cd)
    df_cd = correct_weekly_reporting_in_daily(df_cd)  # correct weekly reporting in the daily column.
    df_cd = correct_anomalous_spike(df_cd) # remove anomalous spike
    
    # Vaccination data.
    #--------------------------------
    features_vac = ["daily_people_vaccinated_smoothed_per_hundred", 
            "people_fully_vaccinated_per_hundred", 
            "total_boosters_per_hundred"]
    df_vac = basic_processing(tb_country_vac, features_vac, True)
    df_vac = correct_anomalous_nonzeros(df_vac) # correct the anomalous-zero error in the vaccination data

    # return processed data.
    return df_cd, df_vac 

def correct_anomalous_spike(df):
    # Get list of unique countries
    country_list = df['country'].unique()
    
    for country in country_list:
        # Select rows corresponding to the current country
        df_country = df[df['country'] == country].copy()  # Avoid modifying a slice of df

        # Correct 'people_fully_vaccinated_per_hundred'
        df_cases = df_country['new_cases']
        df_deaths = df_country['new_deaths']

        # Get the 10 largest values and calculate their mean
        top_10_cases_mean = round(df_cases.nlargest(10).mean())
        top_10_deaths_mean = round(df_deaths.nlargest(10).mean())

        # Identify values that are more than 10 times the mean of the top 10 largest values
        scalar = 5
        high_cases = df_cases > scalar * top_10_cases_mean
        high_deaths = df_deaths > scalar * top_10_deaths_mean

        # Correct the values by setting them to the mean of the top 10 largest values
        df_country.loc[high_cases, 'new_cases'] = top_10_cases_mean
        df_country.loc[high_deaths, 'new_deaths'] = top_10_deaths_mean

        # Reassign the corrected values back to the original dataframe
        df.loc[df['country'] == country, 'new_cases'] = df_country['new_cases']
        df.loc[df['country'] == country, 'new_deaths'] = df_country['new_deaths']

    return df
    

# anomalous non-zeros: when the vaccinations or boosters have periods of non-zero values before any vaccines were administered.
def correct_anomalous_nonzeros(df):
    # Get list of unique countries
    country_list = df['country'].unique()
    
    for country in country_list:
        # Select rows corresponding to the current country
        df_vac_country = df[df['country'] == country].copy()  # Avoid modifying a slice of df

        # Correct 'people_fully_vaccinated_per_hundred'
        df_vac_p100 = df_vac_country['people_fully_vaccinated_per_hundred']
        decreasing_mask_vac = df_vac_p100 < df_vac_p100.cummax()
        if decreasing_mask_vac.any(): 
        
            # Get the two indices between which values will be set to zero
            first_decrease_index_vac = decreasing_mask_vac.idxmax()
            first_country_ind = df.loc[df['country'] == country].index[0]  # Get first index for country
        
            # Set 'people_fully_vaccinated_per_hundred' to 0 for indices from first_country_ind to first_decrease_index_vac
            df.loc[(first_country_ind <= df.index) & (df.index < first_decrease_index_vac), 'people_fully_vaccinated_per_hundred'] = 0


        # Correct 'total_boosters_per_hundred'
        df_boosters_p100 = df_vac_country['total_boosters_per_hundred']
        decreasing_mask_boost = df_boosters_p100 < df_boosters_p100.cummax()
        if decreasing_mask_boost.any(): 

            # get the two index between which values will be set to zero.
            first_decrease_index_boost = decreasing_mask_boost.idxmax()
            first_country_ind = df.loc[df['country'] == country].index[0]  # Get first index for 'India'

            # Set 'total_boosters_per_hundred' to 0 for indices from ind to ind + 99
            df.loc[(first_country_ind <= df.index) & (df.index < first_decrease_index_boost), 'total_boosters_per_hundred'] = 0

    return df


# Sometimes countries will post the cumulative days data on one day of the week.
# mean method in use.
def correct_weekly_reporting_in_daily(df):
    # Get list of unique countries
    country_list = df['country'].unique()

    # Go through country list
    for country in country_list:
        df_country = df[df['country'] == country].copy()
        
        # Cases and deaths data
        df_country_cases = df_country['new_cases']
        df_country_deaths = df_country['new_deaths']
        
        # Create a boolean mask for six consecutive zeros followed by a non-zero value for 'new_cases'
        mask_cases = (df_country_cases.shift(1) == 0) & (df_country_cases.shift(2) == 0) & (df_country_cases.shift(3) == 0) & \
                     (df_country_cases.shift(4) == 0) & (df_country_cases.shift(5) == 0) & \
                     (df_country_cases.shift(6) == 0) & (df_country_cases != 0)
        
        # Create a boolean mask for six consecutive zeros followed by a non-zero value for 'new_deaths'
        mask_deaths = (df_country_deaths.shift(1) == 0) & (df_country_deaths.shift(2) == 0) & (df_country_deaths.shift(3) == 0) & \
                      (df_country_deaths.shift(4) == 0) & (df_country_deaths.shift(5) == 0) & \
                      (df_country_deaths.shift(6) == 0) & (df_country_deaths != 0)

        
        # Get the indices where the pattern matches for cases and deaths
        indices_cases = mask_cases.index[mask_cases].tolist() - df_country_cases.index[0]
        indices_deaths = mask_deaths.index[mask_deaths].tolist() - df_country_deaths.index[0]

        # cases
        # For each index in cases, modify the `new_cases` values in the range j to j+5
        new_cases_col = df_country_cases.copy()
        for j in indices_cases:
            if j + 6 < len(df_country_cases):  # Ensure j+6 is within bounds
                new_cases_col.iloc[j:j+6] = round(np.mean(df_country_cases.iloc[j:j+6]))
        
        # Now assign the new_cases_col to the original DataFrame
        df.loc[(df['country'] == country), 'new_cases'] = new_cases_col

        
        # deaths
        # For each index in deaths, modify the `new_deaths` values in the range j to j+5
        new_deaths_col = df_country_deaths.copy()
        for j in indices_deaths:
            if j + 6 < len(df_country_deaths):  # Ensure j+6 is within bounds
                new_deaths_col.iloc[j:j+6] = round(np.mean(df_country_deaths.iloc[j:j+6]))

        # Now assign the new_deaths_col to the original DataFrame
        df.loc[(df['country'] == country), 'new_deaths'] = new_deaths_col

    return df




        





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