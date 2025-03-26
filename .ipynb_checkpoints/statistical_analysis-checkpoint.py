import numpy as np
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt


# get a correlation of the cases between countries
def get_country_correlation(df, feature):
    df_wide = df.pivot(index='date', columns='country', values=feature)    
    df_corr = df_wide.corr()
    return df_corr

# Function to calculate lagged correlation between base_country and compare_country_list
def get_lagged_cases_correlation(df, base_country, compare_country_list, max_lag=14):
    # Convert base country's 'feature' (e.g., cases) into a time series
    df_wide = df.pivot(index='date', columns='country', values='new_cases')
    base_series = df_wide[base_country]

    # Initialize the dictionary to store correlation values
    lagged_corrs = {country: {} for country in compare_country_list}
    
    # Loop through lags and countries to calculate correlations
    for lag in range(-max_lag, max_lag + 1):
        shifted_base_series = base_series.shift(lag)
        
        for country in compare_country_list:
            country_series = df_wide[country]
            corr_value = shifted_base_series.corr(country_series)
            corr_value = 0 if pd.isna(corr_value) else corr_value
            lagged_corrs[country][lag] = corr_value
    
    # Convert the dictionary to a DataFrame
    return pd.DataFrame(lagged_corrs)

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


# Function to create and plot the network graph
def plot_network(corrs, country_list, max_lag_disp):
    G = nx.DiGraph()  # Directed graph to represent arrows

    # Add nodes (countries)
    for country in country_list:
        G.add_node(country)
    
    # Add edges based on correlation and lag
    lags = {}
    for country1 in corrs:  # Iterate over the countries in the 'corrs' dictionary
        for country2 in corrs[country1]:  # Iterate over the countries in the inner dictionary
            lag = corrs[country1][country2]['lag']  # Access the lag value

            # Only add positive correlations with lag less than max_lag_disp
            if lag > 0 and lag <= max_lag_disp:  
                # Use lag as the weight
                G.add_edge(country1, country2, weight=lag, lag = lag)
                
                # Ensure the country1 exists in the lags dictionary, then record the lag
                if country1 not in lags:
                    lags[country1] = {}
                lags[country1][country2] = lag


    # normalise weights
    max_lag = max([max(lag_dict.values()) for lag_dict in lags.values()])     # get max lag
    min_weight = 1
    for u, v in G.edges():
        # Apply the formula to the edge weight
        new_weight = 1 - G[u][v]['weight']/max_lag
        min_weight = min(min_weight, new_weight)
        
        # Update the edge with the new weight
        G[u][v]['weight'] = new_weight

    # Set node positions for better layout 
    # pos = nx.spring_layout(G, weight='weight', seed=2)
    # pos = nx.circular_layout(G)
    # pos = nx.kamada_kawai_layout(G)
    # pos = nx.spectral_layout(G)
    country_positions = {
    "Argentina": {"lat": -38.4161, "lon": -63.6167},
    "Bolivia": {"lat": -16.2902, "lon": -63.5887},
    "Brazil": {"lat": -14.2350, "lon": -51.9253},
    "Chile": {"lat": -35.6751, "lon": -71.5430},
    "Colombia": {"lat": 4.5709, "lon": -74.2973},
    "Uruguay": {"lat": -32.5228, "lon": -55.7658},
    "Germany": {"lat": 51.1657, "lon": 10.4515},
    "Indonesia": {"lat": -0.7893, "lon": 113.9213},
}
    pos = {country: (data["lon"], data["lat"]) for country, data in country_positions.items()}



    # Draw the network with edge weights and arrows
    plt.figure(figsize=(10, 8))
    
    # Use the 'lag' as the edge width, not the correlation
    a_scalar = 25
    arrow_widths = [a_scalar * G[u][v]['weight'] for u, v in G.edges()]  # Use absolute lag value for edge width
    edge_labels = {(u, v): f'{G[u][v]["lag"]} days' for u, v in G.edges()}
    
    # Draw nodes, edges, and labels
    ns = 2000
    nx.draw_networkx_nodes(G, pos, node_size=ns, node_color='white', edgecolors='black', alpha=0.7)
    nx.draw_networkx_labels(G, pos, font_size=10, font_weight='bold')
    nx.draw_networkx_edges(G, pos, node_size=ns, edge_color='gray', alpha=0.7, arrows=True, arrowsize = a_scalar, arrowstyle='-|>') # 
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=8)
    
    # Show plot
    plt.title("Country Network of Lagged Correlations")
    plt.axis('off')  # Hide axes
    plt.show()

