import numpy as np
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import seaborn as sns


def vax_vs_total_deaths(df_cd, df_vac, country_list):
    total_deaths_vax80_date_dict = {}
    for country in country_list:
        subset = df_vac[df_vac['country'] == country]
        vax80_date = subset.loc[subset['people_fully_vaccinated_per_hundred'] > 0.8, 'date'].min()
    
        # check country reached 80%
        if pd.notna(vax80_date):  # Ensure valid date
            vax80_date = str(vax80_date)  # Convert to string if needed
        
        total_deaths_pM = df_cd[df_cd['country'] == country]['total_deaths_per_million'].max(skipna=True)
    
        total_deaths_vax80_date_dict[country] = [vax80_date, total_deaths_pM]  

    # Plotting
    #--------------------------
    df_plot = pd.DataFrame.from_dict(total_deaths_vax80_date_dict, orient='index', columns=['vax80_date', 'total_deaths_per_million'])
    
    # Drop rows where vax80_date is NaN
    df_plot = df_plot.dropna()
    
    # Convert dates to datetime format
    df_plot['vax80_date'] = pd.to_datetime(df_plot['vax80_date'])
    
    # Plot scatter plot
    plt.figure(figsize=(12, 6))
    plt.scatter(df_plot['vax80_date'], df_plot['total_deaths_per_million'], alpha=0.7)
    
    # Annotate each point with the country name
    for country, row in df_plot.iterrows():
        plt.annotate(country, (row['vax80_date'], row['total_deaths_per_million']), fontsize=9, alpha=0.7)
    
    # Labels and title
    plt.xlabel("Date of 80% Vaccination")
    plt.ylabel("Total Deaths per Million")
    plt.title("Total Deaths per Million vs. Date of 80% Vaccination")
    plt.xticks(rotation=45)
    plt.grid(True)
    
    plt.show()






def plot_cd_corr_heatmap(lags, corr_dict, country_list):

    # Create correlation matrix (rows = countries, cols = lag days)
    correlation_matrix = np.array([corr_dict[country] for country in country_list])
    print
    
    # Plot heatmap
    fig, ax = plt.subplots(figsize=(12, len(country_list) * 0.6))  # Adjust height based on the number of countries
    sns.heatmap(correlation_matrix, cmap="coolwarm", annot=False, xticklabels=lags, yticklabels=country_list, ax=ax)
    
    # Labels and title
    ax.set_xlabel("Lag (days)")
    ax.set_ylabel("Country")
    ax.set_title("Heatmap of Cases & Deaths Correlation Over Lag Days")
    
    plt.show()


# Plot cases & death correlations for multiple countries in 3D
def plot_cd_corr_3d(lags, corr_dict, country_list, y_step, polar):
    fig = plt.figure(figsize=(10, 7))
    ax = fig.add_subplot(111, projection='3d')

    y_init = 0
    y_offset = y_init  # Starting Z-axis offset

    lags_7th = lags[::7]
    y_max = 0
    for i, country in enumerate(country_list):
        correlations = corr_dict[country]

        # Every 7th data point
        correlations_7th = correlations[::7]
        ec = np.interp(lags, lags_7th, correlations_7th) # extrapolated corrlations

        # Plot main curve
        # ax.plot(lags, correlations, zs=z_offset, zdir='y', label=f"{country}", alpha=1, color='black')
        ax.plot(lags_7th, correlations_7th, 'o-', zs = y_offset, zdir='y', color='black', markersize = 2)

        # Plot each data point as a vertical line to zero
        for j in range(len(lags)):
            ax.plot([lags[j], lags[j]], [y_offset, y_offset], [0, ec[j]], alpha = 0.25, color='black', lw=2)
        
        # change view angle
        ax.view_init(elev=polar, azim=-90)  # Adjust angles here
        
        # Increment Z position
        y_offset += y_step

        # get max value
        y_max = max(y_max, max(correlations))
        print(y_offset)

    # Labels and title
    ax.set_xlabel("Lag (days)")
    ax.set_zlabel("Correlation")
    ax.set_title("Lagged Correlation of Cases & Deaths")

    # Set y-axis ticks with country names
    y_ticks = np.arange(y_init, y_init + y_step * len(country_list), y_step) / np.sin(polar/180*np.pi)
    ax.set_yticks(y_ticks) # Changed from range to np.arange for consistent tick positioning
    ax.set_yticklabels(country_list) 

    ax.grid(False)  # Keep grid only on the x-axis


    # Get the current axis limits
    ylim = ax.get_ylim()
    # print(y_step)
    ax.set_ylim(0, 1 - y_step)
    plt.show()


# plot the cases and death correlations for a country.
def plot_country_cd_corr(lags, correlations, max_lag, max_corr, country):

    # every 7th data point
    correlations_7th = correlations[::7]
    lags_7th = lags[::7]  # Subset lags to match

    # Plot the lagged correlations
    plt.figure(figsize=(8, 5))
    plt.plot(lags, correlations, marker='o', linestyle='-', color='gray', alpha=0.5, label="Correlation")
    plt.plot(lags_7th, correlations_7th, marker='o', linestyle='-', color='b', label="Every 7th data point       correlation")
    plt.axvline(max_lag, color='r', linestyle='--', label=f"Maximum correlation: {max_corr:.3f} at {max_lag}     days lag.")
    
    plt.xlabel("Lag (days)")
    plt.ylabel("Correlation")
    plt.title(f"Lagged correlation of cases & deaths in {country}")
    plt.legend()
    plt.grid(True)
    plt.show()


# extract the key data from a countries lagged cases and deaths data. 
def get_lag_cd_corr_data(lagged_corr):
    window_size = 7  # Adjust for more/less smoothing
    
    # Get data out and smooth
    lags = list(lagged_corr.keys())
    correlations = np.array(list(lagged_corr.values()))
    
    # Find lag with max correlation (after smoothing)
    max_lag = lags[np.nanargmax(correlations)]  # Handle NaNs safely
    max_corr = correlations[np.nanargmax(correlations)]

    return lags, correlations, max_lag, max_corr


# Function to calculate lagged correlation between base_country and compare_country_list
def get_country_cd_lag_correlation(df_cases, df_deaths, country, max_lag):
    
    # Convert country cases into a time series
    cases_series = df_cases[country]
    deaths_series = df_deaths[country]

    # Initialize the dictionary to store correlation values
    lagged_corr = {}
    
    # Loop through lags to calculate correlations.
    for lag_shift in range(0, max_lag + 1):
        shifted_cases_series = cases_series.shift(lag_shift) 
        corr_value = shifted_cases_series.corr(deaths_series)
        corr_value = 0 if pd.isna(corr_value) else corr_value 
        lagged_corr[lag_shift] = corr_value
  
    # Convert the dictionary to a DataFrame
    return lagged_corr














# Function to calculate lagged correlation between base_country and compare_country_list
def get_cd_correlation(df, country_list, max_lag=14):
    # Convert base country's 'feature' (e.g., cases) into a time series
    df_cases = df.pivot(index='date', columns='country', values='new_cases')
    df_deaths = df.pivot(index='date', columns='country', values='new_deaths')
    base_series = df_wide[base_country]

    # Initialize the dictionary to store correlation values
    lagged_corrs = {country: {} for country in compare_country_list}
    
    # Loop through lags and countries to calculate correlations
    for lag in range(0, max_lag + 1):
        shifted_base_series = base_series.shift(lag)
        
        for country in compare_country_list:
            country_series = df_wide[country]
            corr_value = shifted_base_series.corr(country_series)
            corr_value = 0 if pd.isna(corr_value) else corr_value
            lagged_corrs[country][lag] = corr_value
    
    # Convert the dictionary to a DataFrame
    return pd.DataFrame(lagged_corrs)









# get a correlation of the cases between countries
def get_country_correlation(df, feature):
    df_wide = df.pivot(index='date', columns='country', values=feature)    
    df_corr = df_wide.corr()
    return df_corr


# Function to get max correlation and lag for one country compared to others
def get_max_corr_country(base_country, lagged_corr):
    max_corr = {}
    
    # Compute maximum correlations and the lag at which that occurs for each country
    for country in lagged_corr.columns:
        # Don't look at correlation with same country
        if country != base_country:
            max_corr_country = lagged_corr[country].max()  # Max correlation
            lag = lagged_corr[country].idxmax()  # Lag for that correlation
            
            # Store the max correlation and corresponding lag in the dictionary
            max_corr[country] = {'max_corr': round(max_corr_country, 3), 'lag': lag}
    
    # Sort max_corr by lag (ascending order)
    sorted_max_corr = dict(sorted(max_corr.items(), key=lambda item: item[1]['lag']))
    
    # Return the sorted dictionary instead of printing
    return sorted_max_corr

# Function to get max correlation and lag for everyone in a list
def get_max_corr_list(df, country_list, lag_max):
    corrs = {}
    
    for country in country_list:
        # Get lagged correlations for each country
        lagged_corr = get_lagged_cases_correlation(df, country, country_list, lag_max)
        
        # Get max correlation and lag for each country
        max_corr = get_max_corr_country(country, lagged_corr)
        
        # Store the result in the corrs dictionary
        corrs[country] = max_corr
    
    # Return the final dictionary containing results for all countries
    return corrs



