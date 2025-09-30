"""
Test script for SmartAlly extraction functions
"""

import sys
sys.path.insert(0, '/home/runner/work/Yitro-Smartally/Yitro-Smartally')

from smartally import (
    extract_annual_expenses,
    extract_net_expenses,
    extract_minimum_investment_aip,
    extract_initial_investment,
    extract_cdsc,
    extract_redemption_fee
)

# Test data
test_text = """
FEES AND EXPENSES

Annual Fund Operating Expenses (expenses that you pay each year as a percentage of the value of your investment)

                                Class A    Class C    Class I    Class F
Management Fees                  0.65%      0.65%      0.65%      0.65%
Distribution (12b-1) Fees        0.25%      1.00%      0.00%      0.00%
Other Expenses                   0.29%      0.29%      0.27%      0.18%
Total Annual Fund Operating      1.19%      1.94%      0.92%      0.83%
Expenses

Net Expenses (after fee waiver/expense reimbursement)
                                Class A    Class C    Class I    Class F
Net Expenses                     1.10%      1.85%      0.85%      0.75%

MINIMUM INVESTMENT

Class A Shares
  Initial Investment: $2,500
  Subsequent Investment: $100
  Automatic Investment Plans
    Subsequent Investment: $50

Class C Shares
  Initial Investment: No minimum
  Subsequent Investment: $100
  Automatic Investment Plans
    Subsequent Investment: $50

Class I Shares
  Initial Investment: $1,000,000
  Subsequent Investment: $100
  Automatic Investment Plans
    Subsequent Investment: $100

Class R Shares
  Initial Investment: No minimum
  Subsequent Investment: $100
  Automatic Investment Plans
    Subsequent Investment: $25

CONTINGENT DEFERRED SALES CHARGE (CDSC)

Class C: 1 year at 1.00%, 0% after first year
Class Z: No CDSC

REDEMPTION FEES

Class Z: 2% redemption fee on shares held less than 60 days
Class A: No redemption fee
"""

# Test tables
test_tables = [
    [
        ['', 'Class A', 'Class C', 'Class I', 'Class F'],
        ['Total Annual Fund Operating Expenses', '1.19%', '1.94%', '0.92%', '0.83%'],
        ['Net Expenses', '1.10%', '1.85%', '0.85%', '0.75%']
    ]
]

def test_extraction():
    print("Testing SmartAlly Extraction Functions\n")
    print("=" * 60)
    
    # Test 1: Total Annual Fund Operating Expenses
    print("\n1. Testing TOTAL_ANNUAL_FUND_OPERATING_EXPENSES")
    for class_name in ['Class A', 'Class I', 'Class C', 'Class F']:
        value, location = extract_annual_expenses(test_text, test_tables, [class_name], 'percentage')
        print(f"   {class_name}: {value} (found in: {location})")
    
    # Test 2: Net Expenses
    print("\n2. Testing NET_EXPENSES")
    for class_name in ['Class A', 'Class I', 'Class F']:
        value, location = extract_net_expenses(test_text, test_tables, [class_name], 'percentage')
        print(f"   {class_name}: {value} (found in: {location})")
    
    # Test 3: Minimum Subsequent Investment AIP
    print("\n3. Testing MINIMUM_SUBSEQUENT_INVESTMENT_AIP")
    for class_name in ['Class A', 'Class I', 'Class R']:
        value, location = extract_minimum_investment_aip(test_text, [class_name], 'currency')
        print(f"   {class_name}: {value} (found in: {location})")
    
    # Test 4: Initial Investment
    print("\n4. Testing INITIAL_INVESTMENT")
    for class_name in ['Class A', 'Class C', 'Class I']:
        value, location = extract_initial_investment(test_text, [class_name], 'currency_or_text')
        print(f"   {class_name}: {value} (found in: {location})")
    
    # Test 5: CDSC
    print("\n5. Testing CDSC")
    for class_name in ['Class C', 'Class Z']:
        value, location = extract_cdsc(test_text, test_tables, [class_name], 'cdsc_special')
        print(f"   {class_name}: {value} (found in: {location})")
    
    # Test 6: Redemption Fee
    print("\n6. Testing REDEMPTION_FEE")
    for class_name in ['Class Z', 'Class A']:
        value, location = extract_redemption_fee(test_text, [class_name], 'text')
        print(f"   {class_name}: {value} (found in: {location})")
    
    print("\n" + "=" * 60)
    print("✅ All tests completed!")

if __name__ == "__main__":
    test_extraction()
