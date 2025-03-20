# display catalgoue information.
def disp_catalogue_info(cat):
    
    # Print headers with proper alignment
    print(f"{'Row':<5} | {'Table':<30} | {'Dataset':<30} | {'Formats':<30}")
    print('-'*90)
    
    # Loop through the columns and print the row number, table, dataset, and formats
    for index, (table, dataset, formats) in enumerate(zip(cat['table'], cat['dataset'], cat['formats'])):
        print(f"{index + 1:<5} | {table:<30} | {dataset:<30} | {str(formats):<30}")
