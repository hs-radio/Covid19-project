import numpy as np
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import seaborn as sns

# present the cases and deaths correlations for different countries.
def plot_cd_correlation_vax_rate(max_lagged_corr, v_low, v_high, country_list):
    # Extract data from max_lagged_corr dictionary
    corr_values_vlow = [max_lagged_corr[c][1] for c in country_list]  # Max correlation before vaccination
    corr_values_vhigh = [max_lagged_corr[c][3] for c in country_list]  # Max correlation after vaccination
    
    # Define y positions for each country
    y_positions = np.arange(len(country_list))
    
    plt.figure(figsize=(10, 6))
    
    # Draw lines connecting the two points for each country (drawn first, so they go under scatter points)
    for i in range(len(country_list)):
        plt.plot([corr_values_vlow[i], corr_values_vhigh[i]], [y_positions[i], y_positions[i]], 
                 color='black', linestyle='-', alpha=0.5, zorder=1)
    
    # Plot max_corr_value_vlow (before vaccination) - larger circles
    plt.scatter(corr_values_vlow, y_positions, color='blue', label='Before Vaccination (v_low)', 
                s=100, edgecolors='black', zorder=2)
    
    # Plot max_corr_value_vhigh (after vaccination) - larger circles
    plt.scatter(corr_values_vhigh, y_positions, color='red', label='After Vaccination (v_high)', 
                s=100, edgecolors='black', zorder=2)
    
    # Formatting
    plt.yticks(y_positions, country_list, fontsize=12)  # Increase fontsize for country names
    plt.xlabel("Maximum correlation", fontsize=12)
    plt.title(f"Correlation between cases and deaths before {v_low*100}% (blue) and after {v_high*100}% (red) vaccinated.")
    plt.axvline(0, color='gray', linestyle='--', linewidth=0.8)  # Reference line at 0
    plt.grid(axis='x', linestyle='--', alpha=0.6)

    plt.savefig('correlation_data.png')
    plt.show()


# for the countries in country_list look at the low and high vaccination periods and find the maximum correlation between cases and deashs
def find_cd_correlations_for_vax_rate(df_cd, df_vac, v_low, v_high, max_lag, country_list):
    max_lagged_corr = {}
    
    for country in country_list:
        subset = df_vac[df_vac['country'] == country]
        vax_low_date = subset.loc[subset['people_fully_vaccinated_per_hundred'] <= v_low, 'date'].max()
        vax_high_date = subset.loc[subset['people_fully_vaccinated_per_hundred'] >= v_high, 'date'].min()
        
        # Convert base country's 'feature' (e.g., cases) into a time series
        df_cases = df_cd.pivot(index='date', columns='country', values='new_cases')
        df_deaths = df_cd.pivot(index='date', columns='country', values='new_deaths')
        
        cases_series = df_cases[country]
        deaths_series = df_deaths[country]
        
        # Define the date range
        first_date = cases_series.index.min()  # Earliest date in the dataset
        last_date = cases_series.index.max()
        
        # Restrict data to the period before and after vax_low_date
        cases_series_vlow = cases_series.loc[first_date:vax_low_date]
        deaths_series_vlow = deaths_series.loc[first_date:vax_low_date]
        
        cases_series_vhigh = cases_series.loc[vax_high_date:last_date]
        deaths_series_vhigh = deaths_series.loc[vax_high_date:last_date]
        
        lagged_corrs_vlow = {}
        lagged_corrs_vhigh = {}
        # Loop through lags and calculate correlations
        for lag in range(0, max_lag + 1):
            shifted_cases_series_vlow = cases_series_vlow.shift(lag)
            shifted_cases_series_vhigh = cases_series_vhigh.shift(lag)
        
            # Normalized correlation
            corr_value_vlow = shifted_cases_series_vlow.corr(deaths_series_vlow)
            corr_value_vhigh = shifted_cases_series_vhigh.corr(deaths_series_vhigh)
    
            # Handle NaN values
            lagged_corrs_vlow[lag] = 0 if pd.isna(corr_value_vlow) else corr_value_vlow
            lagged_corrs_vhigh[lag] = 0 if pd.isna(corr_value_vhigh) else corr_value_vhigh
        
        # Find the max correlation and corresponding lag
        max_lag_index_vlow = max(lagged_corrs_vlow, key=lagged_corrs_vlow.get)
        max_corr_value_vlow = lagged_corrs_vlow[max_lag_index_vlow]
        max_lag_index_vhigh = max(lagged_corrs_vhigh, key=lagged_corrs_vhigh.get)
        max_corr_value_vhigh = lagged_corrs_vhigh[max_lag_index_vhigh]
    
        # record maximum lags for each country
        max_lagged_corr[country] = [max_lag_index_vlow, max_corr_value_vlow, max_lag_index_vhigh, max_corr_value_vhigh]
    return max_lagged_corr




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

    plt.savefig('cd_vax.png')
    plt.show()























