import pandas as pd
import streamlit as st
from typing import Optional
from io import BytesIO

class StreamlitFileProcessingError(Exception):
    """Exception raised for errors during file processing in Streamlit"""
    pass

def process_airbnb_file(file_upload) -> Optional[pd.DataFrame]:
    """
    Process an AirBnB CSV file uploaded through Streamlit and return a DataFrame of reservations.
    
    Args:
        file_upload: Streamlit's UploadedFile object
            
    Returns:
        DataFrame containing processed reservation data or None if processing fails
    """
    try:
        if file_upload is None:
            st.error('No file uploaded')
            return None
            
        if not file_upload.name.endswith('.csv'):
            st.error('Please upload a CSV file')
            return None

        # Read the uploaded file
        date_columns = ['Date', 'Arriving by date', 'Booking date', 
                       'Start date', 'Earnings year']
        
        bnb_df = pd.read_csv(
            BytesIO(file_upload.getvalue()), 
            parse_dates=date_columns
        )
        
        # Validate required columns
        required_columns = date_columns + ['Type']
        missing_columns = [col for col in required_columns if col not in bnb_df.columns]
        
        if missing_columns:
            st.error(f'CSV file is missing required columns: {", ".join(missing_columns)}')
            return None

        # Process the data
        bnb_df['Earnings year'] = bnb_df['Earnings year'].dt.year
        reservations_bnb = bnb_df[bnb_df['Type'] == 'Reservation']
        
        # Update session state
        st.session_state['bnb_report'] = reservations_bnb
        return reservations_bnb
        
    except pd.errors.EmptyDataError:
        st.error('The uploaded CSV file is empty')
        return None
    except pd.errors.ParserError:
        st.error('Unable to parse the CSV file. Please ensure it is properly formatted')
        return None
    except Exception as e:
        st.error(f'An error occurred while processing the file: {str(e)}')
        return None