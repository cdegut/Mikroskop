import pandas as pd
import matplotlib.pyplot as plt

step_per_mm = 800
pixel_size = 0.56
autotune_repeat = 50

def plot_colum(axis, data: pd.DataFrame, column):
    x_data = data[data.columns[0]]
    y_data = data[column] * pixel_size
    axis.scatter(x_data, y_data, label=column)  # Use scatter for points only
    axis.axhline(y=0, color='gray', linestyle='--', linewidth=1)  # Add dashed line for y=0
    for start in range(0, len(x_data), autotune_repeat):
        end = start + autotune_repeat
        block_x = x_data[start:end]
        block_y = y_data[start:end]
        std_dev = block_y.std()
        mean_x = block_x.mean()
        
        # Plot standard deviation as a horizontal line for the block
        axis.hlines(y=block_y.mean(), xmin=block_x.min(), xmax=block_x.max(), color='red', linestyle='--', linewidth=1, label='Std Dev' if start == 0 else "")

        axis.fill_betweenx([block_y.mean() - std_dev, block_y.mean() + std_dev], block_x.min(), block_x.max(), color='red', alpha=0.2)
        
        axis.axvline(x=start, color='firebrick', linestyle='--', linewidth=0.5)  # Add vertical line every 50 units

    axis.set_xlabel(f'{data.columns[0]}')
    axis.set_ylabel(f'{column} (μm)')
    axis.set_title(f'{column} as a function of {data.columns[0]}')
    axis.legend()

# Load the tab-separated file into a DataFrame
#file_path = 'S:\\microscope_data\\accuracy_test-241116_1059\\data.txt'  # Replace with your actual file path

#file_path = 'S:\\microscope_data\\accuracy_test-BacklashNut-Bearing\\data.txt'

#file_path = 'S:\\microscope_data\\accuracy_test-BacklashNut-NoBearing\\data.txt'

file_path = 'S:\\microscope_data\\accuracy_test-241117_2310\\data.txt'

data = pd.read_csv(file_path, sep='\t')

# Display the first few rows to understand the data structure
print(data.head())


# Number of columns to plot (excluding the first one)
num_columns = len(data.columns) - 1

# Create subplots for columns as a function of the first column
fig, axes = plt.subplots(4, 1, figsize=(8, 12))
fig.tight_layout(pad=4.0)

plot_colum(axis=axes[0], data=data, column="X error(first image)")
plot_colum(axis=axes[1], data=data, column="Y error(first image)")
plot_colum(axis=axes[2], data=data, column="X variability(last image)")
plot_colum(axis=axes[3], data=data, column="Y variability(last image)")


if len(data) > autotune_repeat:
    # Create subplots for column 2 vs column 4 and column 5 vs column 7 in blocks of 50 data points
    num_blocks = (len(data) //autotune_repeat) + (1 if len(data) % autotune_repeat != 0 else 0)
    fig2, axes2 = plt.subplots(num_blocks, 2, figsize=(16, 4 * num_blocks))
    fig2.tight_layout(pad=4.0)


    for i, start in enumerate(range(0, len(data), autotune_repeat)):
        block_data = data[start:start + 50]

        # Plot column 2 as a function of column 4 for the current block
        axes2[i, 0].scatter(block_data[data.columns[3]] / 800, block_data[data.columns[1]] * 0.56, label=f'{data.columns[1]} vs {data.columns[3]}')
        axes2[i, 0].axhline(y=0, color='gray', linestyle='--', linewidth=1)
        axes2[i, 0].set_xlabel(f'{data.columns[3]} (mm)')
        axes2[i, 0].set_ylabel(f'{data.columns[1]} (μm)')
        axes2[i, 0].set_title(f'{data.columns[1]} as a function of {data.columns[3]} (Block {i + 1})')
        axes2[i, 0].legend()

        # Plot column 5 as a function of column 7 for the current block
        axes2[i, 1].scatter(block_data[data.columns[6]] / 800, block_data[data.columns[4]] * 0.56, label=f'{data.columns[4]} vs {data.columns[6]}')
        axes2[i, 1].axhline(y=0, color='gray', linestyle='--', linewidth=1)
        axes2[i, 1].set_xlabel(f'{data.columns[6]} (mm)')
        axes2[i, 1].set_ylabel(f'{data.columns[4]} (μm)')
        axes2[i, 1].set_title(f'{data.columns[4]} as a function of {data.columns[6]} (Block {i + 1})')
        axes2[i, 1].legend()

    # Show all the plots
else:
    # Create a second set of plots for specific column pairs
    fig2, axes2 = plt.subplots(2, 1, figsize=(8, 8))
    fig2.tight_layout(pad=4.0)

    # Plot column 2 as a function of column 4
    axes2[0].scatter(data[data.columns[3]] / 800, data[data.columns[1]] * 0.56, label=f'{data.columns[1]} vs {data.columns[3]}')  # Use scatter for points only
    axes2[0].axhline(y=0, color='gray', linestyle='--', linewidth=1)
    axes2[0].set_xlabel(f'{data.columns[3]} (mm)')
    axes2[0].set_ylabel(f'{data.columns[1]} (μm)')
    axes2[0].set_title(f'{data.columns[1]} as a function of {data.columns[3]}')
    axes2[0].legend()

    # Plot column 5 as a function of column 7
    axes2[1].scatter(data[data.columns[6]] / 800, data[data.columns[4]] * 0.56, label=f'{data.columns[4]} vs {data.columns[6]}')  # Use scatter for points only
    axes2[1].axhline(y=0, color='gray', linestyle='--', linewidth=1)
    axes2[1].set_xlabel(f'{data.columns[6]} (mm)')
    axes2[1].set_ylabel(f'{data.columns[4]} (μm)')
    axes2[1].set_title(f'{data.columns[4]} as a function of {data.columns[6]}')
    axes2[1].legend()

plt.show()