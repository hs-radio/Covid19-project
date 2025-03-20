from pprint import pprint
import importlib
import matplotlib.pyplot as plt
import pandas as pd

# display catalgoue information.
def disp_catalogue_info(cat):
    
    # Print headers with proper alignment
    print(f"{'Row':<5} | {'Table':<30} | {'Dataset':<30} | {'Formats':<30}")
    print('-'*90)
    
    # Loop through the columns and print the row number, table, dataset, and formats
    for index, (table, dataset, formats) in enumerate(zip(cat['table'], cat['dataset'], cat['formats'])):
        print(f"{index:<5} | {table:<30} | {dataset:<30} | {str(formats):<30}")

# plot the new cases and deaths each day, specify the country as a string, if not plot_days is given then the maximum time of data is used.
def plot_cases_deaths_by_country(tb1, country, plot_days=None):
    # Plotting parameters
    marker_size = 1
    col1 = '#6fa3f7'  # soft blue
    col2 = '#f08484'  # dark coral
    
    # Select the specified country using .loc
    country_data = tb1.loc[country]
    
    # Extract date, new_cases, and new_deaths
    dates = country_data.index
    new_cases = country_data['new_cases']
    new_deaths = country_data['new_deaths']
    
    # Set plot_days to maximum if not provided
    if plot_days is None:
        plot_days = len(country_data)
    
    # Filter data for the last 'plot_days' days
    end_date = dates[-1]  # Get the last date in the dataset
    start_date = pd.to_datetime(end_date) - pd.Timedelta(days=plot_days)
    
    # Filter the data for the last 'plot_days' days
    filtered_data = country_data[country_data.index >= start_date]
    
    # Create the figure and the first axis (for new cases)
    fig, ax1 = plt.subplots(figsize=(12, 6))
    
    # Plot new cases on the left y-axis
    ax1.plot(filtered_data.index, filtered_data['new_cases'], marker='o', linestyle='-', markersize=marker_size, color=col1, label="New Cases")
    ax1.set_xlabel('Date')
    ax1.set_ylabel('New Cases', color=col1)
    ax1.tick_params(axis='y', labelcolor=col1)
    
    # Create a second y-axis (for new deaths)
    ax2 = ax1.twinx()
    
    # Plot new deaths on the right y-axis
    ax2.plot(filtered_data.index, filtered_data['new_deaths'], marker='o', linestyle='-', markersize=marker_size, color=col2, label="New Deaths")
    ax2.set_ylabel('New Deaths', color=col2)
    ax2.tick_params(axis='y', labelcolor=col2)
    
    # Formatting
    plt.title(f'COVID-19 New Cases and Deaths in {country} Over the Last {plot_days} Days')
    plt.xticks(rotation=45)
    ax1.grid(True, linestyle='--', alpha=0.6)
    
    plt.show()
