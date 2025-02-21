import pandas as pd
# import streamlit as st

class AirBnBError(Exception):
    """Base exception class for AirBnB related errors"""
    pass

class DataFrameError(AirBnBError):
    """Exception raised for errors in DataFrame operations"""
    pass

class FileProcessingError(AirBnBError):
    """Exception raised for errors during file processing"""
    pass


class AirBnB:
  def __init__(self, df: pd.DataFrame):
    if not isinstance(df, pd.DataFrame):
      raise TypeError("Input must be a pandas DataFrame")
    
    self.df = df if len(df) > 0 else None
    self.filtered_df = None
    self.length = len(df) if len(df) > 0 else None
    self.columns = df.columns if len(df) > 0 else None
  
  def get_basic_earnings(self) -> dict:
    """
    Calculate basic earnings statistics from the AirBnB dataset

    Returns:
      dict: earnings brekadown

    Raises:
      DataFrameError: required columns missing or calculation fails
    """

    try:
      if self.df is None:
         raise DataFrameError("No data available")
      
      required_columns = ['Gross earnings', 'Service fee', 'Occupancy taxes']
      missing_columns = [col for col in required_columns if col not in self.df.columns]

      if missing_columns:
        raise DataFrameError(f"Missing required columns: {', '.join(missing_columns)}")

      df = self.df
      gross_earnings = df['Gross earnings'].sum()
      adjustments = 0 # columns to be decided
      service_fees = df['Service fee'].sum()
      tax_withheld = df['Occupancy taxes'].sum()
      total = gross_earnings + adjustments - service_fees - tax_withheld

      return {
        'gross_earnings': gross_earnings,
        'adjustments': adjustments,
        'service_fees': service_fees,
        'tax_withheld': tax_withheld,
        'total': total
      }
    except Exception as e:
      raise DataFrameError(f"An error occurred while processing: {e}")
  
  def get_performance_stats(self) -> dict[str, float]:
    """
    Calculate simple performance statistics from the DataFrame.
   
    Returns:
      dict: performance metrics

    Raise:
      DataFrameError
    """

    try:
      if self.df is None:
        raise DataFrameError("NO data available")
      
      if 'Nights' not in self.df.columns:
        raise DataFrameError("Missing required column: Nights")
      
      df = self.df
      total_nights = df['Nights'].sum()
      average_nights = df['Nights'].mean()
      return {
        'total_nights': total_nights,
        'average_nights': average_nights
      }
    except Exception as e:
      raise DataFrameError(f"Error calculating performance stats: {str(e)}")
  
  def get_listing_stats(self) -> pd.DataFrame:
    """
    Calculate listing statistics from the DataFrame.

    Returns:
      dataframe: listing statistics

    Raises:
      DataFrameError
    """

    try:
      if self.df is None:
        raise DataFrameError("No data available")

      required_columns = ['Listing', 'Nights', 'Amount', 'Paid out',
      'Service fee', 'Fast pay fee', 'Cleaning fee',
      'Occupancy taxes', 'Guest']
      missing_columns = [col for col in required_columns if col not in self.df.columns]
      
      if missing_columns:
          raise DataFrameError(f"Missing required columns: {', '.join(missing_columns)}")

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
      units_df.columns = [x[0] + '_' + x[1] for x in units_df.columns]
      return units_df
    except Exception as e:
      raise DataFrameError(f"Error calculating listing stats: {str(e)}")
  
  def get_customer_stats(self, top_customers = int | None) -> pd.DataFrame:
    """
    Calculate customer statistics from the DataFrame.

    Args:
      top_customers: Optional limit for number of top customers to return
    
    Returns:
      DataFrame containing customer statistics

    Raises:
      DataFrameError
    """

    try:
      if self.df is None:
        raise DataFrameError("No data available")
      
      required_columns = ['Guest', 'Gross earnings', 'Confirmation code', 'Nights']
      missing_columns = [col for col in required_columns if col not in self.df.columns]
      
      if missing_columns:
          raise DataFrameError(f"Missing required columns: {', '.join(missing_columns)}")

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

      if top_customers and isinstance(top_customers, int):
        customers_df = customers_df.head(top_customers)

      return customers_df
    except Exception as e:
      raise DataFrameError(f"Error calculating customer stats: {str(e)}")

  def get_booking_stats(self) -> pd.DataFrame:
    try:
      df = self.df
      time_diff = df['Start date'] - df['Booking date']
      df['booking_to_date'] = time_diff / pd.Timedelta('1 days')
      return df
    except Exception as e:
      raise DataFrameError(f"Error calculating booking stats: {str(e)}")

  # @staticmethod
  # def process_file(file) -> pd.DataFrame:
  #   try:
  #       # Check if file has a valid CSV extension
  #       if not file.name.endswith('.csv'):
  #           st.error('Please upload a CSV file')
  #           return pd.DataFrame()
            
  #       # Read the file directly - no need for getvalue() since pd.read_csv can handle BytesIO objects
  #       bnb_df = pd.read_csv(
  #           file, 
  #           parse_dates=['Date', 'Arriving by date', 'Booking date', 'Start date', 'Earnings year']
  #       )
        
  #       # Basic validation of required columns
  #       required_columns = ['Date', 'Arriving by date', 'Booking date', 'Start date', 'Earnings year', 'Type']
  #       missing_columns = [col for col in required_columns if col not in bnb_df.columns]
        
  #       if missing_columns:
  #         st.error(f'CSV file is missing required columns: {", ".join(missing_columns)}')
  #         return pd.DataFrame()
            
  #       # Process the data
  #       bnb_df['Earnings year'] = bnb_df['Earnings year'].dt.year
  #       reservations_bnb = bnb_df[bnb_df['Type'] == 'Reservation']
        
  #       # Update session state and display
  #       st.session_state['bnb_report'] = reservations_bnb
  #       return reservations_bnb
        
  #   except pd.errors.EmptyDataError:
  #       st.error('The uploaded CSV file is empty')
  #       return pd.DataFrame()
  #   except pd.errors.ParserError:
  #       st.error('Unable to parse the CSV file. Please ensure it is properly formatted')
  #       return pd.DataFrame()
  #   except Exception as e:
  #       st.error(f'An error occurred while processing the file: {str(e)}')
  #       return pd.DataFrame()
