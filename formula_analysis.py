#!/usr/bin/env python3

import json
import math

# Load the data
with open('public_cases.json', 'r') as f:
    cases = json.load(f)

def analyze_simple_cases():
    """Analyze simple cases to understand base per diem"""
    print("=== SIMPLE CASE ANALYSIS ===")
    simple_cases = []
    for case in cases:
        days = case['input']['trip_duration_days']
        miles = case['input']['miles_traveled']  
        receipts = case['input']['total_receipts_amount']
        reimbursement = case['expected_output']
        
        # Look for very simple cases
        if receipts < 25 and miles < 100:
            simple_cases.append((days, miles, receipts, reimbursement))
    
    simple_cases.sort()
    for days, miles, receipts, reimbursement in simple_cases[:15]:
        per_day = reimbursement / days
        print(f"{days}d, {miles}mi, ${receipts:.2f} → ${reimbursement:.2f} (${per_day:.2f}/day)")
    
    return simple_cases

def analyze_mileage_rates():
    """Analyze mileage component by looking at cases with similar other factors"""
    print("\n=== MILEAGE RATE ANALYSIS ===")
    
    # Group by trip length and look at mileage patterns
    by_days = {}
    for case in cases:
        days = case['input']['trip_duration_days']
        miles = case['input']['miles_traveled']
        receipts = case['input']['total_receipts_amount']
        reimbursement = case['expected_output']
        
        if days not in by_days:
            by_days[days] = []
        by_days[days].append((miles, receipts, reimbursement))
    
    # Analyze 1-day trips to isolate mileage effect
    print("1-day trips (to isolate mileage effect):")
    one_day = sorted(by_days[1], key=lambda x: x[0])  # Sort by miles
    
    for miles, receipts, reimbursement in one_day[:20]:
        # Estimate base without mileage
        estimated_base = 100  # Rough base per diem
        mileage_component = reimbursement - estimated_base
        if miles > 0:
            rate_per_mile = mileage_component / miles
            print(f"{miles}mi, ${receipts:.2f} → ${reimbursement:.2f} (est ${rate_per_mile:.3f}/mi)")

def test_formula_hypothesis(days, miles, receipts):
    """Test a hypothesis formula"""
    
    # Base per diem - appears to be inversely related to trip length
    if days == 1:
        base_per_day = 100
    elif days == 2:
        base_per_day = 100
    elif days == 3:
        base_per_day = 105
    elif days == 4:
        base_per_day = 105
    elif days == 5:
        base_per_day = 100  # 5-day doesn't actually get bonus based on data
    else:
        base_per_day = 100
    
    base_amount = days * base_per_day
    
    # Mileage component - tiered rates
    mileage_amount = 0
    remaining_miles = miles
    
    # Tier 1: First 100 miles at higher rate
    if remaining_miles > 0:
        tier1_miles = min(remaining_miles, 100)
        mileage_amount += tier1_miles * 0.58  # Standard federal rate
        remaining_miles -= tier1_miles
    
    # Tier 2: Next 200 miles at reduced rate
    if remaining_miles > 0:
        tier2_miles = min(remaining_miles, 200)
        mileage_amount += tier2_miles * 0.50
        remaining_miles -= tier2_miles
    
    # Tier 3: Remaining miles at further reduced rate
    if remaining_miles > 0:
        mileage_amount += remaining_miles * 0.40
    
    # Receipt component - diminishing returns
    if receipts <= 200:
        receipt_amount = receipts * 0.8
    elif receipts <= 500:
        receipt_amount = 200 * 0.8 + (receipts - 200) * 0.6
    else:
        receipt_amount = 200 * 0.8 + 300 * 0.6 + (receipts - 500) * 0.4
    
    # Efficiency bonus - miles per day
    miles_per_day = miles / days if days > 0 else 0
    efficiency_bonus = 0
    
    if miles_per_day > 200:
        efficiency_bonus = (miles_per_day - 200) * 0.5
    elif miles_per_day > 150:
        efficiency_bonus = (miles_per_day - 150) * 0.3
    
    total = base_amount + mileage_amount + receipt_amount + efficiency_bonus
    return round(total, 2)

def test_formula_accuracy():
    """Test the formula hypothesis against actual data"""
    print("\n=== FORMULA TESTING ===")
    
    correct_within_1 = 0
    correct_within_5 = 0
    total_error = 0
    
    test_cases = cases[:50]  # Test first 50 cases
    
    for case in test_cases:
        days = case['input']['trip_duration_days']
        miles = case['input']['miles_traveled']
        receipts = case['input']['total_receipts_amount']
        expected = case['expected_output']
        
        predicted = test_formula_hypothesis(days, miles, receipts)
        error = abs(predicted - expected)
        total_error += error
        
        if error <= 1:
            correct_within_1 += 1
        if error <= 5:
            correct_within_5 += 1
        
        if len(str(case)) < 10 or error > 20:  # Show some examples
            print(f"{days}d, {miles}mi, ${receipts:.2f} → Expected: ${expected:.2f}, Predicted: ${predicted:.2f}, Error: ${error:.2f}")
    
    print(f"\nAccuracy within $1: {correct_within_1}/{len(test_cases)} ({100*correct_within_1/len(test_cases):.1f}%)")
    print(f"Accuracy within $5: {correct_within_5}/{len(test_cases)} ({100*correct_within_5/len(test_cases):.1f}%)")
    print(f"Average error: ${total_error/len(test_cases):.2f}")

def find_patterns_in_outliers():
    """Look for patterns in cases where simple formulas don't work"""
    print("\n=== OUTLIER PATTERN ANALYSIS ===")
    
    # Look for specific number patterns mentioned in interviews
    rounding_patterns = {}
    
    for case in cases[:100]:
        receipts = case['input']['total_receipts_amount']
        reimbursement = case['expected_output']
        
        # Check if receipts end in .49 or .99 (rounding bug theory)
        cents = round((receipts % 1) * 100)
        if cents in [49, 99]:
            print(f"Receipts ${receipts:.2f} (ends in {cents}) → ${reimbursement:.2f}")

if __name__ == "__main__":
    analyze_simple_cases()
    analyze_mileage_rates()
    test_formula_accuracy()
    find_patterns_in_outliers() 