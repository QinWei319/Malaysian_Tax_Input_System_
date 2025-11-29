import pandas as pd
import os

def verify_user(ic_number, password):
    """
    Verify user credentials by checking IC number format and password match.
    
    Args:
        ic_number (str): User's IC number (should be 12 digits)
        password (str): Password (should be last 4 digits of IC)
    
    Returns:
        bool: True if credentials are valid, False otherwise
    """
    # Check if IC number is exactly 12 digits
    if len(ic_number) != 12 or not ic_number.isdigit():
        return False
    
    # Check if password matches last 4 digits of IC number
    if password == ic_number[-4:]:
        return True
    
    return False


def calculate_tax(income, tax_relief):
    """
    Calculate tax payable based on Malaysian tax rates (Latest 2024/2025).
    
    Tax Brackets:
    Category A: RM 0 - 5,000 @ 0% = RM 0
    Category B: RM 5,001 - 20,000 @ 1% = RM 150
    Category C: RM 20,001 - 35,000 @ 3% = RM 450
    Category D: RM 35,001 - 50,000 @ 6% = RM 900
    Category E: RM 50,001 - 70,000 @ 11% = RM 2,200
    Category F: RM 70,001 - 100,000 @ 19% = RM 5,700
    Category G: RM 100,001 - 400,000 @ 25% = RM 75,000
    Category H: RM 400,001 - 600,000 @ 26% = RM 52,000
    Category I: RM 600,001 - 2,000,000 @ 28% = RM 392,000
    Category J: Exceeding RM 2,000,000 @ 30%
    """
    # Calculate chargeable income
    chargeable_income = income - tax_relief
    
    # If chargeable income is 0 or negative, no tax payable
    if chargeable_income <= 0:
        return 0.0
    
    # Progressive tax calculation based on latest rates
    tax = 0.0
    
    if chargeable_income <= 5000:
        # Category A: 0% on first RM 5,000
        tax = 0
    elif chargeable_income <= 20000:
        # Category B: 1% on next RM 15,000
        tax = 0 + (chargeable_income - 5000) * 0.01
    elif chargeable_income <= 35000:
        # Category C: 3% on next RM 15,000
        tax = 150 + (chargeable_income - 20000) * 0.03
    elif chargeable_income <= 50000:
        # Category D: 6% on next RM 15,000
        tax = 150 + 450 + (chargeable_income - 35000) * 0.06
    elif chargeable_income <= 70000:
        # Category E: 11% on next RM 20,000
        tax = 150 + 450 + 900 + (chargeable_income - 50000) * 0.11
    elif chargeable_income <= 100000:
        # Category F: 19% on next RM 30,000
        tax = 150 + 450 + 900 + 2200 + (chargeable_income - 70000) * 0.19
    elif chargeable_income <= 400000:
        # Category G: 25% on next RM 300,000
        tax = 150 + 450 + 900 + 2200 + 5700 + (chargeable_income - 100000) * 0.25
    elif chargeable_income <= 600000:
        # Category H: 26% on next RM 200,000
        tax = 150 + 450 + 900 + 2200 + 5700 + 75000 + (chargeable_income - 400000) * 0.26
    elif chargeable_income <= 2000000:
        # Category I: 28% on next RM 1,400,000
        tax = 150 + 450 + 900 + 2200 + 5700 + 75000 + 52000 + (chargeable_income - 600000) * 0.28
    else:
        # Category J: 30% on amount exceeding RM 2,000,000
        tax = 150 + 450 + 900 + 2200 + 5700 + 75000 + 52000 + 392000 + (chargeable_income - 2000000) * 0.30
    
    return round(tax, 2)


def save_to_csv(data, filename):
    """
    Save user data to CSV file. Creates new file with header if doesn't exist,
    otherwise appends data to existing file.
    """
    try:
        # Create DataFrame from data
        df = pd.DataFrame([data])
        
        # Check if file exists
        if os.path.exists(filename):
            # Append to existing file without header
            df.to_csv(filename, mode='a', header=False, index=False)
        else:
            # Create new file with header
            df.to_csv(filename, mode='w', header=True, index=False)
        
        return True
    except Exception as e:
        print(f"Error saving to CSV: {e}")
        return False


def read_from_csv(filename):
    """
    Read data from CSV file and return as pandas DataFrame.
    """
    try:
        if os.path.exists(filename):
            # Read ic_number as string to preserve leading zeros
            df = pd.read_csv(filename, dtype={'ic_number': str})
            return df
        else:
            return None
    except Exception as e:
        print(f"Error reading CSV: {e}")
        return None


def check_user_exists(user_id, filename):

    df = read_from_csv(filename)
    
    if df is None or df.empty:
        return False, None
    
    # Check if user_id exists
    user_row = df[df['user_id'] == user_id]
    
    if not user_row.empty:
        user_data = user_row.iloc[0].to_dict()
        return True, user_data
    
    return False, None


def update_user_record(user_id, new_data, filename):
    """
    Update an existing user's record in the CSV file.
    
    Args:
        user_id (str): User ID to update
        new_data (dict): New data to save
        filename (str): Name of CSV file
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        df = read_from_csv(filename)
        
        if df is None:
            # File doesn't exist, create new
            return save_to_csv(new_data, filename)
        
        # Find the user's row
        user_index = df[df['user_id'] == user_id].index
        
        if len(user_index) > 0:
            # Update existing record
            for key, value in new_data.items():
                df.at[user_index[0], key] = value
        else:
            # User not found, this shouldn't happen but handle it
            new_df = pd.DataFrame([new_data])
            df = pd.concat([df, new_df], ignore_index=True)
        
        # Save back to CSV
        df.to_csv(filename, index=False)
        return True
        
    except Exception as e:
        print(f"Error updating CSV: {e}")
        return False


def validate_positive_number(value, field_name):
    """
    Validate that a value is a positive number.
    
    Args:
        value: Value to validate
        field_name (str): Name of the field for error messages
    
    Returns:
        tuple: (is_valid: bool, converted_value: float or None, error_message: str)
    """
    try:
        num_value = float(value)
        if num_value < 0:
            return False, None, f"{field_name} cannot be negative."
        return True, num_value, ""
    except ValueError:
        return False, None, f"{field_name} must be a valid number."