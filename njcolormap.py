import geopandas as gpd
import matplotlib.pyplot as plt
import pandas as pd

# Input LP solution with new district assignments from redistrict.py
lp_solution = {
    'Atlantic': 2,
    'Bergen': 4,
    'Burlington': 1,
    'Camden': 1,
    'Cape May': 2,
    'Cumberland': 2,
    'Essex': 0,
    'Gloucester': 2,
    'Hudson': 3,
    'Hunterdon': 1,
    'Mercer': 1,
    'Middlesex': 5,
    'Monmouth': 5,
    'Morris': 0,
    'Ocean': 2,
    'Passaic': 4,
    'Salem': 2,
    'Somerset': 3,
    'Sussex': 0,
    'Union': 3,
    'Warren': 0
}

# County populations
county_data = {
    'County': [
        'Atlantic', 'Bergen', 'Burlington', 'Camden', 'Cape May', 'Cumberland', 'Essex',
        'Gloucester', 'Hudson', 'Hunterdon', 'Mercer', 'Middlesex', 'Monmouth', 'Morris',
        'Ocean', 'Passaic', 'Salem', 'Somerset', 'Sussex', 'Union', 'Warren'
    ],
    'Population': [
        275213, 975736, 469167, 527196, 94610, 152326, 851117, 308423, 705472, 130183,
        381671, 863623, 642799, 514423, 659197, 513395, 65338, 348842, 146132, 572726, 111252
    ]
}

# Convert county data to a DataFrame
county_df = pd.DataFrame(county_data)

# Calculate total population per district
county_df['District'] = county_df['County'].map(lp_solution)
district_population = county_df.groupby('District')['Population'].sum().to_dict()

# Print population by district
print("Population by district:")
for district, population in district_population.items():
    print(f"District {district}: {population} people")

# Load the shapefile of New Jersey counties
nj_map = gpd.read_file('County_Boundaries_of_NJ/County_Boundaries_of_NJ.shp')

# Create the 'County' column based on the 'COUNTY' column in the shapefile
nj_map['County'] = nj_map['COUNTY'].str.title().str.strip()

# Map district assignments and population to the GeoDataFrame
nj_map['District'] = nj_map['County'].map(lp_solution)
nj_map['District_Population'] = nj_map['District'].map(district_population)

# Check for missing district assignments
missing_counties = nj_map[nj_map['District'].isna()]['County'].unique()
if len(missing_counties) > 0:
    print(f"Warning: The following counties were not assigned a district: {missing_counties}")

# Plot the map with a gradient based on population
fig, ax = plt.subplots(1, 1, figsize=(12, 12))
nj_map.plot(column='District_Population', ax=ax, legend=True, cmap='YlOrRd', missing_kwds={'color': 'lightgrey'})

# Add a title and display the map
plt.title('New Jersey Congressional Districts (Population-Weighted Gradient)')
plt.axis('off')

# Save the map to a file in the top-level directory
output_path = 'nj_congressional_districts_map.png'
plt.savefig(output_path, dpi=300, bbox_inches='tight')
print(f"Map saved to {output_path}")

# Show the plot
plt.show()
