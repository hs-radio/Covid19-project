# import libraries
from pprint import pprint
import importlib
import matplotlib.pyplot as plt
import pandas as pd
from shapely.geometry import Point
import matplotlib.animation as animation
from datetime import timedelta
import geopandas as gpd
import matplotlib.animation as animation
from PIL import Image
import io
from datetime import datetime
import os
from tqdm import tqdm


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



# Function to plot covid cases as circles on the world map, for a specific date
def plot_world_map_with_circles(fig, ax, tb1, world, date, show_plot = False):
    
    # Filter data for the specific date
    tb_date = tb1.xs(date, level='date')  # Use the date from the MultiIndex

    # Create a dictionary of country name to number of cases for that date
    country_cases = dict(zip(tb_date.index.get_level_values('country'), tb_date['new_cases']))

    # Create a GeoDataFrame for plotting the world map
    world.plot(ax=ax, color='lightgray')

    # Add circles to represent the number of cases in each country
    for country, cases in country_cases.items():
        # Check if the cases are <NA>, and if so, set it to 0
        if isinstance(cases, pd._libs.missing.NAType):
            cases = 0  # Set cases to 0 if it is <NA>
            
        try:
            # Get the centroid of the country
            country_geom = world[world['ADMIN'] == country].geometry.iloc[0]  
            country_centroid = country_geom.centroid

            # Create a circle at the centroid location with size based on cases
            ax.scatter(country_centroid.x, country_centroid.y, s=cases / 100, color='red', alpha=0.5)
        except IndexError:
            continue  # In case a country is missing from the shapefile

    # Add title and show the plot
    plt.title(f'COVID-19 Cases by Country on {date}')
    plt.axis('off')
    if show_plot:
        plt.show()  # Conditionally show the plot if show_plot is True

# Create gif of cases by country on the world map each day without saving PNGs
def create_world_map_cases_animation(fig, ax, tb1, world, output_file):
    # Get the minimum and maximum dates from the 'date' level of the MultiIndex
    # start_date = tb1.index.get_level_values('date').min()
    # end_date = tb1.index.get_level_values('date').max() # TESTING
    start_date = pd.to_datetime('2022-01-01')
    end_date = pd.to_datetime('2022-02-1')
    dates = pd.date_range(start=start_date, end=end_date)

    # Prepare a list to store frames
    frames = []

    # Generate frames for each date
    for date in tqdm(dates, desc="Processing dates", unit="date"):
        ax.clear()  # Clear the axis for each frame
        plot_world_map_with_circles(fig, ax, tb1, world, date)  # Plot the world map for the date
    
        # Save the current frame to a BytesIO buffer
        buf = io.BytesIO()
        plt.savefig(buf, format='png', bbox_inches='tight', pad_inches=0)
        buf.seek(0)
        
        # Open the frame as an image and append it to the frames list
        frame = Image.open(buf)
        frames.append(frame)

    # Create the GIF directly from the frames
    frames[0].save(output_file, save_all=True, append_images=frames[1:], duration=500, loop=0)
    
    print(f"Animation saved as {output_file}")