import pandas as pd
import streamlit as st

class AirBnB:
  def __init__(self, df: pd.DataFrame):
    self.df = df if len(df) > 0 else None
    self.filtered_df = None
    self.length = len(df) if len(df) > 0 else None
    self.columns = df.columns if len(df) > 0 else None
  
  def get_basic_earnings(self) -> dict:
    try:
      df = self.df
      gross_earnings = df['Gross earnings'].sum()
      adjustments = 0 # columns to be decided
      service_fees = df['Service fee'].sum()
      tax_withheld = df['Occupancy taxes'].sum()
      total = gross_earnings + adjustments + service_fees + tax_withheld

      return {
        'gross_earnings': gross_earnings,
        'adjustments': adjustments,
        'service_fees': service_fees,
        'tax_withheld': tax_withheld,
        'total': total
      }
    except AttributeError:
       st.error("Columns not found")
    except Exception as e:
       st.error(f"An error occurred while processing: {e}")
  
  def get_performance_stats(self) -> dict:
    try:
      df = self.df
      total_nights = df['Nights'].sum()
      average_nights = df['Nights'].mean()
      return {
        'total_nights': total_nights,
        'average_nights': average_nights
      }
    except Exception as e:
      st.error(f"An error occurred while processing: {e}")
  
  def get_listing_stats(self) -> pd.DataFrame:
    try:
      # 
      units_df = self.df[['Listing', 'Nights', 'Amount', 'Paid out',
        'Service fee', 'Fast pay fee', 'Cleaning fee',
        'Occupancy taxes', 'Guest']].groupby(by="Listing").agg({
        'Nights': ['sum', 'mean', 'max'],
        'Amount': ['sum', 'mean', 'max'],
        'Paid out': ['sum'],
        'Service fee': ['sum'],
        'Fast pay fee': ['sum'],
        'Cleaning fee': ['sum'],
        'Occupancy taxes': ['sum'],
        'Guest': ['nunique', 'count']
      })
      units_columns = [x[0] + '_' + x[1] for x in units_df.columns]
      units_df.columns = units_columns
      # units_df = units_df.reset_index()

      return units_df
    except Exception as e:
      st.error(f"An error occurred while processing: {e}")
  
  def get_customer_stats(self, top_customers = int | None) -> pd.DataFrame:
    try:
      # customer_df = self.filtered_df if self.filtered_df is not None else self.df
      df = self.df
      repeat_counts = df['Guest'].value_counts()
      repeat_counts = repeat_counts[repeat_counts > 1].index
      customers_df = df[df['Guest'].isin(repeat_counts)]
      customers_df = customers_df.groupby('Guest').agg({
        'Gross earnings': ['sum', 'mean'],
        'Confirmation code': 'count',
        'Nights': 'sum'
      })

      customers_df.columns = ['Total Gross Earnings', 'Average Earnings per Booking',
      'Bookings Executed', 'Total Nights']
      customers_df = customers_df.sort_values(by="Total Gross Earnings", axis=0, ascending=False)
      # customers_df.sort_values(by="Total Gross Earnings", axis=1, inplace=True)

      if top_customers and type(top_customers) == int:
        customers_df = customers_df.head(top_customers)

      return customers_df
    except Exception as e:
      st.error(f"An error occurred while processing: {e}")
      return None

  def get_booking_stats(self) -> pd.DataFrame:
    try:
      df = self.df
      time_diff = df['Start date'] - df['Booking date']
      df['booking_to_date'] = time_diff / pd.Timedelta('1 days')
      return df
    except Exception as e:
      st.error(f"An error occurred while processing: {e}")

  @staticmethod
  def process_file(file) -> pd.DataFrame:
    try:
        # Check if file has a valid CSV extension
        if not file.name.endswith('.csv'):
            st.error('Please upload a CSV file')
            return pd.DataFrame()
            
        # Read the file directly - no need for getvalue() since pd.read_csv can handle BytesIO objects
        bnb_df = pd.read_csv(
            file, 
            parse_dates=['Date', 'Arriving by date', 'Booking date', 'Start date', 'Earnings year']
        )
        
        # Basic validation of required columns
        required_columns = ['Date', 'Arriving by date', 'Booking date', 'Start date', 'Earnings year', 'Type']
        missing_columns = [col for col in required_columns if col not in bnb_df.columns]
        
        if missing_columns:
          st.error(f'CSV file is missing required columns: {", ".join(missing_columns)}')
          return pd.DataFrame()
            
        # Process the data
        bnb_df['Earnings year'] = bnb_df['Earnings year'].dt.year
        reservations_bnb = bnb_df[bnb_df['Type'] == 'Reservation']
        
        # Update session state and display
        st.session_state['bnb_report'] = reservations_bnb
        return reservations_bnb
        
    except pd.errors.EmptyDataError:
        st.error('The uploaded CSV file is empty')
        return pd.DataFrame()
    except pd.errors.ParserError:
        st.error('Unable to parse the CSV file. Please ensure it is properly formatted')
        return pd.DataFrame()
    except Exception as e:
        st.error(f'An error occurred while processing the file: {str(e)}')
        return pd.DataFrame()
