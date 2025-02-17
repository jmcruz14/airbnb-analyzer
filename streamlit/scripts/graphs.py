import streamlit as st
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

def make_twin_graph(
  bnb_df: pd.DataFrame,
  x_col,
  y1_col,
  y2_col,
  y1_color: str = 'black',
  y2_color: str = 'blue',
  bar_width = 0.3,
  # title
) -> plt.figure:
  fig, ax1 = plt.subplots(figsize=(12,12))

  # Set bar width and positions
  x = np.arange(len(bnb_df[x_col]))

  # Create the first axis for earnings
  ax1.bar(x - bar_width/2, bnb_df[y1_col], 
      width=bar_width, color=y1_color, label='Total Earnings')
  ax1.set_xlabel('Guests')
  ax1.set_ylabel('Total Earnings (Php)', color=y1_color)
  ax1.tick_params(axis='y', labelcolor=y1_color)

  # Set x-ticks and rotate labels
  ax1.set_xticks(x)
  ax1.set_xticklabels(bnb_df[x_col], rotation=45, ha='right')

  # Create the second axis for nights
  ax2 = ax1.twinx()
  ax2.bar(x + bar_width/2, bnb_df[y2_col], 
      width=bar_width, color=y2_color, alpha=0.4, label='Number of Nights')
  ax2.set_ylabel('Number of Nights', color=y2_color)
  ax2.tick_params(axis='y', labelcolor=y2_color)

  # Add value labels on top of bars
  for i, v in enumerate(bnb_df[y1_col]):
    ax1.text(i - bar_width/2, v + 1, f'{v:.0f}', ha='center', va='bottom', color=y1_color, rotation=45)
  for i, v in enumerate(bnb_df[y2_col]):
    ax2.text(i + bar_width/2, v + 0.1, str(int(v)), ha='center', va='bottom', color=y2_color)

  # Add title and adjust legend
  plt.title('Repeat Guest Earnings and Nights')
  lines1, labels1 = ax1.get_legend_handles_labels()
  lines2, labels2 = ax2.get_legend_handles_labels()
  ax2.legend(lines1 + lines2, labels1 + labels2, loc='upper right')
  
  return fig

def make_histogram(
  bnb_df,
  x,
  stat_y: str,
  bins,
  bar_title,
  xlabel,
  bar_color: str = 'black'
):
  try:
    # fig, ax = plt.subplots()
    g = sns.histplot(bnb_df[x], stat=stat_y, bins=bins, color=bar_color)
    g.set_title(bar_title)
    g.set(xlabel=xlabel)
    return g
  except Exception as e:
    st.error(f"An error occurred while processing: {e}")
    return None