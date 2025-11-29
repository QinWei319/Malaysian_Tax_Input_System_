import functions as fn
import os

# Constants
CSV_FILENAME = "tax_records.csv"

# Tax relief limits (in RM)
TAX_RELIEF_LIMITS = {
    "individual": 9000,
    "individual_disabled": 6000,
    "spouse": 4000,
    "spouse_disabled": 5000,
    "child_under_18": 2000,
    "child_over_18_diploma": 8000,
    "disabled_child": 6000,
    "disabled_child_diploma": 8000,
    "medical": 10000,
    "lifestyle": 2500,
    "education": 7000,
    "parental_medical": 8000,
    "sspn": 8000,
    "breastfeeding": 1000,
    "childcare": 3000,
}


def display_banner():
    """Display program banner."""
    print("\n" + "="*60)
    print(" "*15 + "MALAYSIAN TAX CALCULATOR")
    print("="*60)


def display_menu():
    """Display main menu options."""
    print("\n" + "-"*60)
    print("1. Register New User")
    print("2. Login")
    print("3. View All Tax Records")
    print("4. Exit")
    print("-"*60)


def register_user():
    """Handle user registration process."""
    print("\n--- USER REGISTRATION ---")
    
    # Get user ID
    user_id = input("Enter User ID: ").strip()
    if not user_id:
        print("Error: User ID cannot be empty.")
        return False
    
    # Check if user already exists
    exists, _ = fn.check_user_exists(user_id, CSV_FILENAME)
    if exists:
        print(f"Error: User ID '{user_id}' already exists. Please login instead.")
        return False
    
    # Get IC number
    while True:
        ic_number = input("Enter IC Number (12 digits): ").strip()
        if len(ic_number) == 12 and ic_number.isdigit():
            break
        else:
            print("Error: IC number must be exactly 12 digits.")
    
    # Get password (last 4 digits of IC)
    while True:
        password = input(f"Enter Password (last 4 digits of IC: {ic_number[-4:]}): ").strip()
        if fn.verify_user(ic_number, password):
            # Save registration data to CSV
            registration_data = {
                'user_id': user_id,
                'ic_number': ic_number,
                'annual_income': 0.0,
                'tax_relief': 0.0,
                'tax_payable': 0.0
            }
            
            if fn.save_to_csv(registration_data, CSV_FILENAME):
                print(f"\n✓ Registration successful! User ID: {user_id}")
                print("You can now login to calculate your tax.")
                return True
            else:
                print("Error: Failed to save registration data.")
                return False
        else:
            print("Error: Password must be the last 4 digits of your IC number.")
            retry = input("Try again? (y/n): ").lower()
            if retry != 'y':
                return False


def login_user():
    """Handle user login process."""
    print("\n--- USER LOGIN ---")
    
    # Get user ID
    user_id = input("Enter User ID: ").strip()
    
    # Check if user exists
    exists, user_data = fn.check_user_exists(user_id, CSV_FILENAME)
    if not exists:
        print(f"Error: User ID '{user_id}' not found. Please register first.")
        return None, None
    
    # Get IC number from stored data and ensure it's 12 digits with leading zeros
    stored_ic = str(user_data['ic_number']).zfill(12)
    
    # Verify password (max 3 attempts)
    for attempt in range(3):
        password = input("Enter Password (last 4 digits of IC): ").strip()
        
        if fn.verify_user(stored_ic, password):
            print(f"\n✓ Login successful! Welcome, {user_id}!")
            return user_id, stored_ic
        else:
            remaining = 2 - attempt
            if remaining > 0:
                print(f"Error: Incorrect password. {remaining} attempts remaining.")
            else:
                print("Error: Maximum login attempts exceeded.")
                return None, None
    
    return None, None


def get_tax_relief_input():
    """
    Prompt user to input various tax relief amounts with validation.
    """
    print("\n" + "="*60)
    print(" "*18 + "TAX RELIEF DETAILS")
    print("="*60)
    
    total_relief = 0.0
    relief_breakdown = {}
    
    # ===== INDIVIDUAL RELIEF =====
    print("\n--- Individual Relief ---")
    
    # Check if disabled
    while True:
        disabled = input("Are you disabled? (yes/no): ").strip().lower()
        if disabled in ['yes', 'no', 'y', 'n']:
            break
        print("Please enter 'yes' or 'no'")
    
    if disabled in ['yes', 'y']:
        # Disabled individual gets RM 6,000 additional + RM 9,000 standard
        individual_relief = TAX_RELIEF_LIMITS['individual'] + TAX_RELIEF_LIMITS['individual_disabled']
        print(f"✓ Individual Relief (Disabled): RM {individual_relief:,.2f}")
        relief_breakdown['Individual (Disabled)'] = individual_relief
    else:
        # Standard individual relief
        individual_relief = TAX_RELIEF_LIMITS['individual']
        print(f"✓ Individual Relief: RM {individual_relief:,.2f}")
        relief_breakdown['Individual'] = individual_relief
    
    total_relief += individual_relief
    
    # ===== MARITAL STATUS & SPOUSE RELIEF =====
    print("\n--- Marital Status ---")
    print("1. Single")
    print("2. Married")
    print("3. Divorced / Widow / Widower")
    
    while True:
        marital_status = input("Select your marital status (1-3): ").strip()
        if marital_status in ['1', '2', '3']:
            break
        print("Please enter 1, 2, or 3")
    
    spouse_relief = 0.0
    
    if marital_status == '2':  # Married
        print("\n--- Spouse Relief ---")
        
        # Check if spouse is disabled
        while True:
            spouse_disabled = input("Is your spouse disabled? (yes/no): ").strip().lower()
            if spouse_disabled in ['yes', 'no', 'y', 'n']:
                break
            print("Please enter 'yes' or 'no'")
        
        if spouse_disabled in ['yes', 'y']:
            spouse_relief += TAX_RELIEF_LIMITS['spouse_disabled']
            print(f"✓ Spouse Relief (Disabled): RM {TAX_RELIEF_LIMITS['spouse_disabled']:,.2f}")
            relief_breakdown['Spouse (Disabled)'] = TAX_RELIEF_LIMITS['spouse_disabled']
        
        # Check if spouse is working
        while True:
            spouse_working = input("Is your spouse working? (yes/no): ").strip().lower()
            if spouse_working in ['yes', 'no', 'y', 'n']:
                break
            print("Please enter 'yes' or 'no'")
        
        if spouse_working in ['no', 'n']:
            spouse_relief += TAX_RELIEF_LIMITS['spouse']
            print(f"✓ Spouse Relief (Not Working): RM {TAX_RELIEF_LIMITS['spouse']:,.2f}")
            relief_breakdown['Spouse (Not Working)'] = TAX_RELIEF_LIMITS['spouse']
        else:
            print("✓ Spouse is working - no additional relief")
    
    total_relief += spouse_relief
    
    # ===== CHILD RELIEF =====
    print("\n--- Child Relief ---")
    
    while True:
        has_child = input("Do you have children? (yes/no): ").strip().lower()
        if has_child in ['yes', 'no', 'y', 'n']:
            break
        print("Please enter 'yes' or 'no'")
    
    child_relief = 0.0
    
    if has_child in ['yes', 'y']:
        print("\n--- Child Details ---")
        
        # Children under 18
        while True:
            try:
                num_under_18 = int(input("Number of children under 18 years old: ").strip())
                if num_under_18 < 0:
                    print("Please enter a positive number")
                    continue
                if num_under_18 > 12:
                    print("Maximum 12 children allowed. Using 12.")
                    num_under_18 = 12
                break
            except ValueError:
                print("Please enter a valid number")
        
        if num_under_18 > 0:
            under_18_relief = num_under_18 * TAX_RELIEF_LIMITS['child_under_18']
            child_relief += under_18_relief
            print(f"✓ Child Relief (<18): {num_under_18} × RM 2,000 = RM {under_18_relief:,.2f}")
            relief_breakdown[f'Children (<18) [{num_under_18}]'] = under_18_relief
        
        # Children 18 and above with diploma or degree
        remaining_slots = 12 - num_under_18
        if remaining_slots > 0:
            while True:
                try:
                    num_over_18_diploma = int(input(f"Number of children (≥18) with diploma/degree (max {remaining_slots}): ").strip())
                    if num_over_18_diploma < 0:
                        print("Please enter a positive number")
                        continue
                    if num_over_18_diploma > remaining_slots:
                        print(f"Maximum {remaining_slots} more children allowed. Using {remaining_slots}.")
                        num_over_18_diploma = remaining_slots
                    break
                except ValueError:
                    print("Please enter a valid number")
            
            if num_over_18_diploma > 0:
                over_18_relief = num_over_18_diploma * TAX_RELIEF_LIMITS['child_over_18_diploma']
                child_relief += over_18_relief
                print(f"✓ Child Relief (≥18, Diploma+): {num_over_18_diploma} × RM 8,000 = RM {over_18_relief:,.2f}")
                relief_breakdown[f'Children (≥18, Diploma+) [{num_over_18_diploma}]'] = over_18_relief
        
        # Disabled children
        while True:
            has_disabled_child = input("\nDo you have any disabled children? (yes/no): ").strip().lower()
            if has_disabled_child in ['yes', 'no', 'y', 'n']:
                break
            print("Please enter 'yes' or 'no'")
        
        if has_disabled_child in ['yes', 'y']:
            while True:
                try:
                    num_disabled = int(input("Number of disabled children: ").strip())
                    if num_disabled < 0:
                        print("Please enter a positive number")
                        continue
                    break
                except ValueError:
                    print("Please enter a valid number")
            
            if num_disabled > 0:
                disabled_child_relief = num_disabled * TAX_RELIEF_LIMITS['disabled_child']
                child_relief += disabled_child_relief
                print(f"✓ Disabled Child Relief: {num_disabled} × RM 6,000 = RM {disabled_child_relief:,.2f}")
                relief_breakdown[f'Disabled Children [{num_disabled}]'] = disabled_child_relief
    
    total_relief += child_relief
    
    # ===== MEDICAL EXPENSES =====
    print("\n--- Medical Expenses Relief ---")
    while True:
        medical = input(f"Medical expenses for self/spouse/child [Max RM {TAX_RELIEF_LIMITS['medical']:,}]: RM ")
        is_valid, value, error = fn.validate_positive_number(medical, "Medical expenses")
        if is_valid:
            if value > TAX_RELIEF_LIMITS['medical']:
                print(f"Warning: Amount exceeds limit. Using maximum RM {TAX_RELIEF_LIMITS['medical']:,}")
                value = TAX_RELIEF_LIMITS['medical']
            if value > 0:
                print(f"✓ Medical Expenses Relief: RM {value:,.2f}")
                relief_breakdown['Medical Expenses'] = value
            total_relief += value
            break
        else:
            print(error)
    
    # ===== PARENTAL MEDICAL =====
    print("\n--- Parent Medical Expenses Relief ---")
    while True:
        parental = input(f"Medical expenses for parents [Max RM {TAX_RELIEF_LIMITS['parental_medical']:,}]: RM ")
        is_valid, value, error = fn.validate_positive_number(parental, "Parent medical expenses")
        if is_valid:
            if value > TAX_RELIEF_LIMITS['parental_medical']:
                print(f"Warning: Amount exceeds limit. Using maximum RM {TAX_RELIEF_LIMITS['parental_medical']:,}")
                value = TAX_RELIEF_LIMITS['parental_medical']
            if value > 0:
                print(f"✓ Parent Medical Relief: RM {value:,.2f}")
                relief_breakdown['Parent Medical'] = value
            total_relief += value
            break
        else:
            print(error)
    
    # ===== EDUCATION FEES =====
    print("\n--- Education Fees Relief (Self) ---")
    while True:
        education = input(f"Education fees for self [Max RM {TAX_RELIEF_LIMITS['education']:,}]: RM ")
        is_valid, value, error = fn.validate_positive_number(education, "Education fees")
        if is_valid:
            if value > TAX_RELIEF_LIMITS['education']:
                print(f"Warning: Amount exceeds limit. Using maximum RM {TAX_RELIEF_LIMITS['education']:,}")
                value = TAX_RELIEF_LIMITS['education']
            if value > 0:
                print(f"✓ Education Fees Relief: RM {value:,.2f}")
                relief_breakdown['Education Fees'] = value
            total_relief += value
            break
        else:
            print(error)
    
    # ===== LIFESTYLE =====
    print("\n--- Lifestyle Relief ---")
    print("(Books, sports equipment, computer, smartphone, internet, etc.)")
    while True:
        lifestyle = input(f"Lifestyle expenses [Max RM {TAX_RELIEF_LIMITS['lifestyle']:,}]: RM ")
        is_valid, value, error = fn.validate_positive_number(lifestyle, "Lifestyle")
        if is_valid:
            if value > TAX_RELIEF_LIMITS['lifestyle']:
                print(f"Warning: Amount exceeds limit. Using maximum RM {TAX_RELIEF_LIMITS['lifestyle']:,}")
                value = TAX_RELIEF_LIMITS['lifestyle']
            if value > 0:
                print(f"✓ Lifestyle Relief: RM {value:,.2f}")
                relief_breakdown['Lifestyle'] = value
            total_relief += value
            break
        else:
            print(error)
    
    # ===== SUMMARY =====
    print("\n" + "="*60)
    print(" "*18 + "TAX RELIEF SUMMARY")
    print("="*60)
    
    for category, amount in relief_breakdown.items():
        print(f"{category:<35} RM {amount:>12,.2f}")
    
    print("-"*60)
    print(f"{'TOTAL TAX RELIEF':<35} RM {total_relief:>12,.2f}")
    print("="*60)
    
    return total_relief


def calculate_and_save_tax(user_id, ic_number):
    """
    Main tax calculation workflow.
    
    Args:
        user_id (str): User's ID
        ic_number (str): User's IC number
    """
    print("\n" + "="*60)
    print(" "*20 + "TAX CALCULATION")
    print("="*60)
    
    # Get annual income
    while True:
        income_input = input("\nEnter Annual Income (RM): RM ")
        is_valid, income, error = fn.validate_positive_number(income_input, "Annual income")
        if is_valid:
            break
        else:
            print(error)
    
    # Get tax relief
    tax_relief = get_tax_relief_input()
    
    # Calculate tax
    tax_payable = fn.calculate_tax(income, tax_relief)
    
    # Display results
    print("\n" + "="*60)
    print(" "*20 + "TAX SUMMARY")
    print("="*60)
    print(f"Annual Income:        RM {income:,.2f}")
    print(f"Total Tax Relief:     RM {tax_relief:,.2f}")
    print(f"Chargeable Income:    RM {max(0, income - tax_relief):,.2f}")
    print(f"Tax Payable:          RM {tax_payable:,.2f}")
    print("="*60)
    
    # Update user record in CSV
    data = {
        'user_id': user_id,
        'ic_number': ic_number,
        'annual_income': income,
        'tax_relief': tax_relief,
        'tax_payable': tax_payable
    }
    
    # Remove old record and add new one
    if fn.update_user_record(user_id, data, CSV_FILENAME):
        print("\n✓ Tax record saved successfully!")
    else:
        print("\n✗ Error saving tax record.")


def view_all_records():
    """Display all tax records from CSV file."""
    print("\n" + "="*60)
    print(" "*20 + "TAX RECORDS")
    print("="*60)
    
    df = fn.read_from_csv(CSV_FILENAME)
    
    if df is None:
        print("\nNo records found. The tax records file does not exist yet.")
        return
    
    if df.empty:
        print("\nNo tax records available.")
        return
    
    # Display records in a formatted table
    print(f"\nTotal Records: {len(df)}")
    print("-"*60)
    
    for idx, row in df.iterrows():
        print(f"\nRecord #{idx + 1}")
        print(f"  User ID:          {row['user_id']}")
        print(f"  IC Number:        {row['ic_number']}")
        print(f"  Annual Income:    RM {row['annual_income']:,.2f}")
        print(f"  Tax Relief:       RM {row['tax_relief']:,.2f}")
        print(f"  Tax Payable:      RM {row['tax_payable']:,.2f}")
        print("-"*60)


def main():
    """Main program loop."""
    display_banner()
    print("Welcome to the Malaysian Tax Calculator!")
    
    while True:
        display_menu()
        choice = input("\nEnter your choice (1-4): ").strip()
        
        if choice == '1':
            # Register new user
            register_user()
            
        elif choice == '2':
            # Login and calculate tax
            user_id, ic_number = login_user()
            if user_id and ic_number:
                calculate_and_save_tax(user_id, ic_number)
            
        elif choice == '3':
            # View all records
            view_all_records()
            
        elif choice == '4':
            # Exit
            print("\nThank you for using the Malaysian Tax Calculator!")
            print("Goodbye!\n")
            break
            
        else:
            print("\n✗ Invalid choice. Please select 1-4.")
        
        # Pause before showing menu again
        if choice in ['1', '2', '3']:
            input("\nPress Enter to continue...")


if __name__ == "__main__":
    main()