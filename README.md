# Introduction

This project offers a set of functions designed to help visualize and analyze COVID-19 data. The functions allow for plotting daily new cases and deaths by country, visualizing the global spread of COVID-19 on a world map, and creating an animated world map that shows the progression of cases over time. The data used in these analyses can be easily loaded from a catalog, and the results can be generated as high-quality visualizations that can either be displayed or saved. Below are some example use cases of the available functions, which demonstrate how to load data, generate plots, and create animations.

There is also a set of functions that account for a ML model that predicts how many infections one would expect.

*** things to add
- data comes from many sources, I need to select relevant parts and combine others.
- remove not correct data e.g. country = "upper midl incomd country"
- lots of NA when vax or boosters have not been administered. some need to be set zero, others need to be set to their last value
- govs dont post any booster data and then all at once.

## Variables

- `tb1 = cat.iloc[1].load()`:  
  This variable loads the first dataset from the catalog, which is commonly used in the functions.


## Functions in "transform_data.py"
- `specific_corrections(df_ppl_vac_p100, df_boosters_p100)`  
  Corrects anomalous non-zero values in vaccination and booster data, such as periods with non-zero values before any vaccines were administered. It checks for decreases in the vaccination and booster data and sets the preceding values to zero.  
  Example: `specific_corrections(df_ppl_vac_p100, df_boosters_p100)`

- `process_data_by_country(tb, features)`  
  Processes raw data into a usable form by pivoting it into time series for each feature. It handles missing data by forward filling and removes non-country data points (e.g., continents, regions). Returns separate DataFrames for each feature.  
  Example: `process_data_by_country(tb, ['daily_vac', 'people_vac', 'boosters'])`

- `non_countries`  
  A list of non-country entities (e.g., regions, continents, and special territories) to be excluded from the data processing.  
  Example: Excludes entities like 'Africa', 'Asia', 'World', etc.

  

## Functions in "plot_data.py"

- `disp_catalogue_info(cat)`:  
  Displays information about the datasets available in the catalog, including the names and formats of each dataset.

- `plot_cases_deaths_by_country(tb1, country, None)`:  
  Plots the daily new COVID-19 cases and deaths over time for the specified country. If no specific number of days is provided, it defaults to using the maximum available range.  
  Example: `country = 'Austria'`

- `world_fig = plot_world_map_with_circles(fig, ax, tb1, world, date, num_show_name, show_plot = False)`:  
  Plots a world map with circles representing COVID-19 cases for a specific date.
  `num_show_name` is the number of cases a country must have for its name to be printed above it circle. 
  Example: `date = "2022-01-01"`

- `create_world_map_cases_animation(tb1, world, output_file)`:  
  Generates an animated GIF showing the progression of COVID-19 cases around the world over time and saves the animation to the specified output file.  
  Example: `output_file = 'covid_cases_animation.gif'`

- `country_cases_each_day(date)`:  
  Many countries would only report their cases each week. This function provides methods for estimating the cases each day.
  Method == 0: looks at the last six days and sets a country's cases to the first non-zero value found. This assumes that the cases were reported weekly.

  - `plot_country_cd(country, df_cases, df_deaths)`  
  Plots daily new cases (left axis) and daily deaths (right axis) for a specified country, with a combined legend.  
  Example: `plot_country_cd('Brazil', df_cases, df_deaths)`

- `plot_country_vac(country, df_daily_vac_p100, df_ppl_vac_p100, df_boosters_p100)`  
  Plots daily vaccinations, percentage of people vaccinated, and boosters for a specified country. Daily vaccinations are on the left axis, while percentages of people vaccinated and boosters are on the right.  
  Example: `plot_country_vac('India', df_daily_vac_p100, df_ppl_vac_p100, df_boosters_p100)`
