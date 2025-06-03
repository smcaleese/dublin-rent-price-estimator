import pandas as pd
import numpy as np
from pathlib import Path

def merge_datasets():
    """
    Merge the daft_dublin_rent_data.csv and data_sharing.csv datasets
    according to the specified plan.
    """
    
    # Load the datasets
    script_dir = Path(__file__).parent
    daft_data_path = script_dir / "daft_scraper" / "daft_dublin_rent_data.csv"
    sharing_data_path = script_dir / "daft_scraper" / "data_sharing.csv"
    
    print("Loading datasets...")
    daft_df = pd.read_csv(daft_data_path)
    sharing_df = pd.read_csv(sharing_data_path)
    
    print(f"Daft dataset shape: {daft_df.shape}")
    print(f"Sharing dataset shape: {sharing_df.shape}")
    
    # Process daft_dublin_rent_data.csv (Whole Properties)
    print("\nProcessing daft dataset...")
    daft_processed = daft_df.copy()
    
    # Add is_shared column (0 for whole properties)
    daft_processed['is_shared'] = 0
    
    # Add room_type columns (all 0 for whole properties)
    daft_processed['room_type_single'] = 0
    daft_processed['room_type_double'] = 0
    daft_processed['room_type_twin'] = 0
    daft_processed['room_type_shared'] = 0
    
    # Process data_sharing.csv (Shared Rooms)
    print("Processing sharing dataset...")
    sharing_processed = sharing_df.copy()
    
    # Add is_shared column (1 for shared properties)
    sharing_processed['is_shared'] = 1
    
    # Handle baths column - fill empty values with 0
    sharing_processed['baths'] = sharing_processed['baths'].fillna(0)
    sharing_processed['baths'] = pd.to_numeric(sharing_processed['baths'], errors='coerce').fillna(0)
    
    # Handle beds column - create room_type one-hot encoding
    print("Creating room_type one-hot encoding...")
    
    # Initialize room_type columns
    sharing_processed['room_type_single'] = 0
    sharing_processed['room_type_double'] = 0
    sharing_processed['room_type_twin'] = 0
    sharing_processed['room_type_shared'] = 0
    
    # Map beds values to room_type columns
    beds_mapping = {
        'single': 'room_type_single',
        'double': 'room_type_double', 
        'twin': 'room_type_twin',
        'shared': 'room_type_shared'
    }
    
    for idx, row in sharing_processed.iterrows():
        beds_value = str(row['beds']).lower().strip()
        
        # Handle empty/nan beds values (like Niche Living studios)
        if pd.isna(row['beds']) or beds_value == 'nan' or beds_value == '':
            # Treat as single occupancy studio
            sharing_processed.loc[idx, 'room_type_single'] = 1
        else:
            # Map to appropriate room_type
            for key, col in beds_mapping.items():
                if key in beds_value:
                    sharing_processed.loc[idx, col] = 1
                    break
            else:
                # If no match found, default to single
                sharing_processed.loc[idx, 'room_type_single'] = 1
    
    # Convert beds column to numeric for shared properties
    # For shared rooms, set beds to 1 (representing 1 room being rented)
    # For studios/single occupancy, set to 0
    sharing_processed['beds_numeric'] = 1  # Default to 1 room
    
    # For entries that are more like studios (empty beds, or certain prop_types)
    studio_mask = (
        (sharing_processed['beds'].isna()) | 
        (sharing_processed['beds'] == '') |
        (sharing_processed['prop_type'].str.contains('Studio', case=False, na=False))
    )
    sharing_processed.loc[studio_mask, 'beds_numeric'] = 0
    
    # Replace the original beds column with the numeric version
    sharing_processed['beds'] = sharing_processed['beds_numeric']
    sharing_processed.drop('beds_numeric', axis=1, inplace=True)
    
    # Ensure both dataframes have the same columns in the same order
    expected_columns = ['price', 'beds', 'baths', 'prop_type', 'address', 'link', 
                       'is_shared', 'room_type_single', 'room_type_double', 
                       'room_type_twin', 'room_type_shared']
    
    # Reorder columns
    daft_processed = daft_processed[expected_columns]
    sharing_processed = sharing_processed[expected_columns]
    
    # Clean price data - remove rows with N/A or invalid prices
    print("Cleaning price data...")
    
    def clean_price_column(df):
        # Convert price to numeric, coercing errors to NaN
        df['price'] = pd.to_numeric(df['price'], errors='coerce')
        # Remove rows with NaN prices
        df = df.dropna(subset=['price'])
        # Remove rows with price <= 0
        df = df[df['price'] > 0]
        return df
    
    daft_processed = clean_price_column(daft_processed)
    sharing_processed = clean_price_column(sharing_processed)
    
    print(f"After cleaning - Daft dataset shape: {daft_processed.shape}")
    print(f"After cleaning - Sharing dataset shape: {sharing_processed.shape}")
    
    # Merge the datasets
    print("Merging datasets...")
    merged_df = pd.concat([daft_processed, sharing_processed], ignore_index=True)
    
    print(f"Final merged dataset shape: {merged_df.shape}")
    
    # Display some statistics
    print("\nDataset statistics:")
    print(f"Total entries: {len(merged_df)}")
    print(f"Shared properties: {len(merged_df[merged_df['is_shared'] == 1])}")
    print(f"Whole properties: {len(merged_df[merged_df['is_shared'] == 0])}")
    print(f"Price range: €{merged_df['price'].min():.0f} - €{merged_df['price'].max():.0f}")
    
    print("\nRoom type distribution (for shared properties):")
    shared_df = merged_df[merged_df['is_shared'] == 1]
    for col in ['room_type_single', 'room_type_double', 'room_type_twin', 'room_type_shared']:
        count = shared_df[col].sum()
        print(f"{col}: {count}")
    
    # Save the merged dataset
    output_path = script_dir / "train.csv"
    print(f"\nSaving merged dataset to {output_path}...")
    merged_df.to_csv(output_path, index=False)
    
    print("Dataset merge completed successfully!")
    return merged_df

if __name__ == "__main__":
    merge_datasets()
