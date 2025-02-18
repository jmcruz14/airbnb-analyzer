import os
os.sys.path.insert(0, os.getcwd())

import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
from api.AirBnB import AirBnB
from scripts.process_file import process_airbnb_file
from scripts.graphs import make_twin_graph, make_histogram

st.set_page_config(
  page_title="AirBnB Analyzer",
  layout="wide",
  initial_sidebar_state="collapsed"
)

# Initialize
if 'bnb_report' not in st.session_state:
  st.session_state['bnb_report'] = AirBnB(pd.DataFrame())

# st.write("""
#   <style>
#     .st-key-earnings-total-summary {
#       background  : #FF9CEE
#     }
#   </style>
# """, unsafe_allow_html=True)

def results_section(processed_file_output):
  pass

def main():
  st.title("AirBnB Analyzer")
  st.subheader("A working Streamlit prototype by Jay")

  st.info("""
    **Instructions:**\n
    1. Extract your AirBnB listing report by following the corresponding steps:\n
    \ta. From the host panel in the Desktop application, click 'Earnings'\n
    \tb. Click 'View All Paid'\n
    \tc. Click 'Get CSV Report'\n
    \td. For full functionality, do not tick off anything and instead Select All.\n
    2. Place the extracted report in the file uploader below and click 'Accept'.
  """, icon="ℹ️")

  file_upload = st.file_uploader("Upload file here", accept_multiple_files=False)
  process_button = st.button("Process", type="primary", disabled=not file_upload)
    
  # Create a separate button without on_click
  if file_upload is not None:
    if process_button:
      try:
        # Create an instance of AirBnB class
        bnb = AirBnB(pd.DataFrame())
        st.session_state['bnb_report'] = AirBnB(process_airbnb_file(file_upload))
      except Exception as e:
          st.error(f"Error processing file: {str(e)}")

  with st.expander('**Advanced options**', False):
    # Filter section
    st.write("""
      This section is set to include the following:\n
      - Date ranges (If selected -> pick to filter by month/year/for entire period)
        - Option to pick by Earnings year?\n
      - Filter to show ALL types of transactions (reservations, payouts, etc)\n
      - Specific filters for
        - Customers (top customers limit)
    """)

  if 'bnb_report' in st.session_state and st.session_state.bnb_report.length is not None:
    st.divider()
    st.write("#### Earnings Summary")

    # Basic Earnings
    try:
      basic_earnings = st.session_state.bnb_report.get_basic_earnings()
      summary_col1, summary_col2, summary_col3, summary_col4 = st.columns(4)
      with summary_col1:
        with st.container(border=True):
          st.metric(label="Gross earnings", value='Php {:,.0f}'.format(basic_earnings.get('gross_earnings')))
      with summary_col2:
        with st.container(border=True):
          st.metric(label="Service fees", value='Php {:,.0f}'.format(basic_earnings.get('service_fees')))
      with summary_col3:
        total_container = st.container(border=True, key='earnings-total-summary')
        with total_container:
          st.metric(label="Total", value='Php {:,.0f}'.format(basic_earnings.get('total')))
    except Exception as e:
      st.error(f"Error processing basic report: {e}")

    # Performance Stats
    st.write("#### Performance Stats")

    try:
      performance_stats = st.session_state.bnb_report.get_performance_stats()
      graph_col, performance_col1, performance_col2 = st.columns([2,1,1])
      with performance_col1:
        with st.container(border=True):
          st.metric(label="Total Nights", value='{:.0f}'.format(performance_stats.get('total_nights')))
      with performance_col2:
        with st.container(border=True):
          st.metric(label="Average Nights", value='{:.0f}'.format(performance_stats.get('average_nights')))
      # graph_col, extra_col2 = st.columns([2,2])
      with graph_col:
        bnb_df = st.session_state.bnb_report.df
        nights_reserved_dist = make_histogram(
          bnb_df,
          'Nights',
          'count',
          [1,2,3,4,5,6,7,8,9,10, float('inf')],
          bar_title="Nights Reserved",
          xlabel="Nights"
        )
        st.pyplot(nights_reserved_dist.get_figure())
    except Exception as e:
      st.error(f"Error processing performance stats: {e}")

    # Listing Stats
    st.write('#### Listing Stats')
    
    try:
      listing_df = st.session_state.bnb_report.get_listing_stats()
      st.write("**Fiscal report**")
      fiscal_listing_df = listing_df[['Amount_sum', 'Service fee_sum']]
      fiscal_listing_df['Total'] = fiscal_listing_df['Amount_sum'] - fiscal_listing_df['Service fee_sum']
      fiscal_listing_df.columns = ['Gross earnings', 'Service fees', 'Total']
      for col in fiscal_listing_df.columns:
        fiscal_listing_df[col] = fiscal_listing_df[col].apply(lambda x: "Php {:,.2f}".format(x))
      st.table(
        fiscal_listing_df
      )

      st.write("**Performance**")
      customer_night_df = listing_df[['Nights_sum', 'Nights_mean', 'Nights_max', 'Guest_nunique', 'Guest_count']]
      customer_night_df['Nights_sum'] = customer_night_df['Nights_sum'].astype(int)
      customer_night_df['Nights_max'] = customer_night_df['Nights_max'].astype(int)
      customer_night_df.columns = ['Total Nights', 'Average Nights', 'Maximum Nights Stay', 'Unique Guest Bookings', 'Total Guests']
      st.table(customer_night_df.style.format({
        'Average Nights': '{:.2f}'
      }))
    except Exception as e:
      st.error(f"Error processing listing statistics: {e}")

      st.write("#### Customers")
    try:
      earnings_df = st.session_state.bnb_report.get_customer_stats(top_customers=5)
      earnings_df['Total Nights'] = earnings_df['Total Nights'].astype(int) 
      edf_1 = earnings_df.style.format({
        'Total Gross Earnings': 'Php {:,.2f}',
        'Average Earnings per Booking': 'Php {:,.2f}'
      })

      earnings_customers_df = earnings_df.reset_index()

      cust_col1, cust_col2 = st.columns(2)
      with cust_col1:
        customers_fig = make_twin_graph(
          earnings_customers_df, 
          'Guest', 
          'Total Gross Earnings', 
          'Total Nights',
          y1_color='#404040'
        )
        st.pyplot(customers_fig)
        plt.clf()
      with cust_col2:
        st.table(edf_1) 
    except Exception as e:
      st.error(f"Error processing customer statistics: {e}")

      st.write('#### Booking Distributions')
    try:
      bookings_df = st.session_state.bnb_report.get_booking_stats()
      bookings_bins = [0,5,10,15,20,25,30,35,40,45,50, float('inf')]
      bins_labels=['0-5', '6-10', '11-15', '16-20', '21-25', '26-30', '31-35', '36-40', '41-45', '45-50', '50>']
      bookings_col1, bookings_col2 = st.columns(2)
      with bookings_col1:
        cust_fig = make_histogram(
          bookings_df, 
          'booking_to_date', 
          'count', 
          bookings_bins,
          bar_title="Booking-to-date distribution",
          xlabel="Booking-to-date"
        )
        st.pyplot(cust_fig.get_figure())
      with bookings_col2:
        st.write("##### Findings")
        binned_btd = pd.cut(bookings_df['booking_to_date'], bookings_bins, labels=bins_labels, include_lowest=True)
        # st.table(binned_btd.value_counts(sort=False).reset_index())
        binned_btd = binned_btd.value_counts(sort=False).reset_index()

        # Find all ranges with maximum frequency
        max_freq = binned_btd['count'].max()
        max_freq_ranges = binned_btd[binned_btd['count'] == max_freq]['booking_to_date'].tolist()
        
        # Find all ranges with minimum frequency
        min_freq = binned_btd['count'].min()
        min_freq_ranges = binned_btd[binned_btd['count'] == min_freq]['booking_to_date'].tolist()
        
        # Format the ranges for display
        max_ranges_str = " and ".join(max_freq_ranges) if len(max_freq_ranges) <= 2 else ", ".join(max_freq_ranges[:-1]) + f", and {max_freq_ranges[-1]}"
        min_ranges_str = " and ".join(min_freq_ranges) if len(min_freq_ranges) <= 2 else ", ".join(min_freq_ranges[:-1]) + f", and {min_freq_ranges[-1]}"

        st.write(f"""
            - Most bookings occur **{max_ranges_str} days** away from the booking with **{max_freq} bookings** each
            - Fewest bookings occur **{min_ranges_str} days** away from the booking with **{min_freq} bookings** each
        """)
    except Exception as e:
      st.error(f"Error processing bookings report: {e}")

    # dummy space
  st.divider()
  st.write("*This analyzer is an unofficial project by Jay. You may access the repo [here](https://github.com/jmcruz14/airbnb-analyzer)*")



if __name__ == '__main__':
  main()