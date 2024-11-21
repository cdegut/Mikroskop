import pandas as pd
file_path = 'S:\\microscope_data\\accuracy_test-BacklashNut-Bearing\\data.txt'
done_reapeat = 50
pixel_size = 0.56
um_per_steps = 1.25
def self_tune():
    data = pd.read_csv(file_path, sep='\t')
    df_sliced = data.loc[done_reapeat - 50: done_reapeat]
    median_X_positive = df_sliced[df_sliced['X distance'] > 0]['X error(first image)'].median() * pixel_size /um_per_steps
    median_X_negative = df_sliced[df_sliced['X distance'] < 0]['X error(first image)'].median() * pixel_size /um_per_steps
    median_Y_positive = df_sliced[df_sliced['Y distance'] > 0]['Y error(first image)'].median() * pixel_size /um_per_steps
    median_Y_negative = df_sliced[df_sliced['Y distance'] < 0]['Y error(first image)'].median() * pixel_size /um_per_steps

    print(f"Medians of errors in steps X+ {median_X_positive:.2f}, X- {median_X_negative:.2f}, Y+ {median_Y_positive:.2f}, Y- {median_Y_negative:.2f},")
    
    

    
if done_reapeat%50  == 0:
    self_tune()