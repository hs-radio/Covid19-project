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

# Plot a country's case and death data.
def plot_country_cd(country, df_cases, df_deaths):
    # Create figure and axis
    fig, ax2 = plt.subplots(figsize=(10, 6))  # Optional: Adjust figure size for better readability
    
    # Plot the daily cases on the left-hand side axis
    line1, = ax2.plot(df_cases[country], label="Daily new cases", color='r')  
    ax2.set_xlabel("Date")
    ax2.set_ylabel("Daily new cases", color='r')  # Label for the left-hand axis
    
    # Create a second y-axis for deaths on the right-hand side
    ax1 = ax2.twinx()
    line2, = ax1.plot(df_deaths[country], label="Daily deaths", color='b')
    ax1.set_ylabel("Daily deaths")

    # Collect line objects and labels from both axes
    lines = [line1, line2]
    labels = [line.get_label() for line in lines]

    # Add a single legend
    ax2.legend(lines, labels, loc="upper left")

    # Display the plot
    plt.show()


# plot a countries vaccination data.
def plot_country_vac(country, df_daily_vac_p100, df_ppl_vac_p100, df_boosters_p100):
    # Create figure and axis
    fig, ax2 = plt.subplots(figsize=(10, 6))  # Optional: Adjust figure size for better readability
    
    # Plot the daily vaccinations on the left-hand side axis
    line1, = ax2.plot(df_daily_vac_p100[country], label="Daily Vaccinations per 100", color='r')  
    ax2.set_xlabel("Date")
    ax2.set_ylabel("Daily Vaccinations per 100", color='r')  
    
    # Create a second y-axis for people vaccinated and boosters on the right-hand side
    ax1 = ax2.twinx()
    line2, = ax1.plot(df_ppl_vac_p100[country], label="People Vaccinated (%)", color='b')
    line3, = ax1.plot(df_boosters_p100[country], label="Boosters (%)", color='g')
    ax1.set_ylabel("Percentage of Population (%)")
    
    # Collect line objects and labels from both axes
    lines = [line1, line2, line3]
    labels = [line.get_label() for line in lines]

    # Add a single legend
    ax2.legend(lines, labels, loc="upper left")

    # Display the plot
    plt.show()





# display catalgoue information.
def disp_catalogue_info(cat):
    
    # Print headers with proper alignment
    print(f"{'Row':<5} | {'Table':<30} | {'Dataset':<30} | {'Formats':<30}")
    print('-'*90)
    
    # Loop through the columns and print the row number, table, dataset, and formats
    for index, (table, dataset, formats) in enumerate(zip(cat['table'], cat['dataset'], cat['formats'])):
        print(f"{index:<5} | {table:<30} | {dataset:<30} | {str(formats):<30}")



# plot the new cases and deaths each day, specify the country as a string, if not plot_days is given then the maximum time of data is used.
def plot_cases_deaths_by_country(tb_country_cases_deaths, country, plot_days=None):
    # Plotting parameters
    marker_size = 1
    col1 = '#6fa3f7'  # soft blue
    col2 = '#f08484'  # dark coral
    
    # Select the specified country using .loc
    country_data = tb_country_cases_deaths.loc[country]
    
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




# find the cases on each day for a country. 
# method = 0: If there are no cases check the last 7 days for a non-zero value.
def country_cases_each_day(date, tb_date, tb_country_cases_deaths, method):

    # Filter out countries with "World", "countries", or "North America" in the name
    country_cases = {
        country: cases for country, cases in zip(tb_date.index.get_level_values('country'), tb_date['new_cases'])
        if not any(exclude in country.lower() for exclude in ["world", "countries", "north america", "europe", "european", "asia", "africa"])
    }

    # Method == 0: is there a nonzero value in the last six days.
    if method == 0:
        # Convert the date to a pandas datetime object
        date = pd.to_datetime(date)

        # Iterate over all countries and check for zero cases
        for country, cases in country_cases.items():
            
            # Check if the cases are <NA>, and if so, set it to 0
            if isinstance(cases, pd._libs.missing.NAType):
                cases = 0  # Set cases to 0 if it is <NA>
            
            if cases == 0:
                found_nonzero = False
                # Check the previous six days for non-zero values
                for i in range(1, 7):  # Look at the previous 6 days
                    prev_day = date - pd.Timedelta(days=i)
                    tb_prev_day = tb_country_cases_deaths.xs(prev_day, level='date')
                    prev_day_cases = tb_prev_day.loc[tb_prev_day.index.get_level_values('country') == country, 'new_cases'].values
                    
                    if prev_day_cases.size > 0 and prev_day_cases[0] > 0:
                        country_cases[country] = prev_day_cases[0]
                        found_nonzero = True
                        break
                
                # If no non-zero case is found in the previous 6 days, leave as zero
                if not found_nonzero:
                    country_cases[country] = 0

    return country_cases
    



# Function to plot covid cases as circles on the world map, for a specific date
def plot_world_map_with_circles(fig, ax, tb_country_cases_deaths, world, date, num_show_name, show_plot = False):
    
    # Filter data for the specific date
    tb_date = tb_country_cases_deaths.xs(date, level='date')  # Use the date from the MultiIndex

    # get the formatted country cases
    method = 0
    country_cases = country_cases_each_day(date, tb_date, tb_country_cases_deaths, method)

    # # # TESTING
    # us_cases = country_cases.get("United States", None)  # Safely get cases for the US
    # if us_cases is not None:
    #     print(f"COVID-19 cases in the United States on {date}: {us_cases}")
    # else:
    #     print(f"No data available for the United States on {date}")

    # Create a GeoDataFrame for plotting the world map
    world.plot(ax=ax, color='lightgray')

    # Add circles to represent the number of cases in each country
    for country, cases in country_cases.items():
    
        try:
            # Get the centroid of the country
            if country == 'United States':
                country = 'United States of America'
            country_geom = world[world['ADMIN'] == country].geometry.iloc[0]  
            country_centroid = country_geom.centroid

            # Create a circle at the centroid location with size based on cases
            ax.scatter(country_centroid.x, country_centroid.y, s=cases / 250, color='red', alpha=0.5)

            # TESTING
            if country == "United States":
                print(cases)
                # print(country_centroid.x, country_centroid.y)

            # Add the country's name above the circle if cases exceed num_show_name
            if cases > num_show_name:
                # Adjust the y-position slightly above the circle's centroid based on its size
                circle_radius = cases / 250
                ax.text(country_centroid.x, country_centroid.y + (circle_radius / 100), country, fontsize=8, ha='center', color='black')

        except IndexError:
            continue  # In case a country is missing from the shapefile

    # Add title and show the plot
    plt.title(f'COVID-19 Cases by Country on {date}')
    plt.axis('off')
    if show_plot:
        plt.show()  # Conditionally show the plot if show_plot is True



# Create gif of cases by country on the world map each day without saving PNGs
def create_world_map_cases_animation(fig, ax, tb_country_cases_deaths, world, output_file,start_date, end_date, num_show_name):

    # dates to make gif through
    dates = pd.date_range(start=start_date, end=end_date)

    # Prepare a list to store frames
    frames = []

    # Generate frames for each date
    for date in tqdm(dates, desc="Processing dates", unit="date"):
        ax.clear()  # Clear the axis for each frame
        plot_world_map_with_circles(fig, ax, tb_country_cases_deaths, world, date, num_show_name)  # Plot the world map for the date
    
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