#!/usr/bin/env python3

import json
import math

# Load the data
with open('public_cases.json', 'r') as f:
    cases = json.load(f)

def analyze_receipt_correlation():
    """Analyze the relationship between receipts and reimbursement"""
    print("=== RECEIPT-BASED ANALYSIS ===")
    
    # Look at receipt-to-reimbursement ratios
    ratios = []
    for case in cases[:100]:
        days = case['input']['trip_duration_days']
        miles = case['input']['miles_traveled']
        receipts = case['input']['total_receipts_amount']
        reimbursement = case['expected_output']
        
        if receipts > 0:
            ratio = reimbursement / receipts
            ratios.append((receipts, reimbursement, ratio, days, miles))
    
    # Sort by receipt amount to see patterns
    ratios.sort(key=lambda x: x[0])
    
    print("Receipt amount → Reimbursement (ratio, days, miles)")
    for receipts, reimbursement, ratio, days, miles in ratios[:30]:
        print(f"${receipts:.2f} → ${reimbursement:.2f} ({ratio:.2f}x, {days}d, {miles}mi)")

def analyze_simple_receipt_cases():
    """Look at cases with minimal other factors"""
    print("\n=== SIMPLE RECEIPT CASES ===")
    
    # Cases with very low receipts - these should show base calculation
    low_receipt_cases = []
    for case in cases:
        receipts = case['input']['total_receipts_amount']
        if receipts < 30:
            low_receipt_cases.append(case)
    
    low_receipt_cases.sort(key=lambda x: x['input']['total_receipts_amount'])
    
    print("Low receipt cases (under $30):")
    for case in low_receipt_cases[:20]:
        days = case['input']['trip_duration_days']
        miles = case['input']['miles_traveled']
        receipts = case['input']['total_receipts_amount']
        reimbursement = case['expected_output']
        
        # Calculate what the reimbursement would be without receipts
        base_estimate = reimbursement - receipts
        per_day_base = base_estimate / days if days > 0 else 0
        
        print(f"{days}d, {miles}mi, ${receipts:.2f} → ${reimbursement:.2f} (base ~${base_estimate:.2f}, ~${per_day_base:.2f}/day)")

def test_receipt_plus_mileage_hypothesis():
    """Test if it's receipts + mileage calculation"""
    print("\n=== RECEIPT + MILEAGE HYPOTHESIS ===")
    
    test_cases = cases[:30]
    total_error = 0
    
    for case in test_cases:
        days = case['input']['trip_duration_days']
        miles = case['input']['miles_traveled']
        receipts = case['input']['total_receipts_amount']
        expected = case['expected_output']
        
        # Hypothesis: reimbursement = receipts + mileage_component
        # Try to figure out mileage rate
        mileage_component = expected - receipts
        if miles > 0:
            apparent_mile_rate = mileage_component / miles
            print(f"{days}d, {miles}mi, ${receipts:.2f} → ${expected:.2f} (mileage: ${mileage_component:.2f}, ${apparent_mile_rate:.3f}/mi)")

def look_for_base_plus_receipts():
    """Test if it's base_per_day * days + receipt_multiplier * receipts"""
    print("\n=== BASE + RECEIPT MULTIPLIER HYPOTHESIS ===")
    
    # Try different base rates and receipt multipliers
    base_rates = [50, 75, 100, 125, 150]
    receipt_multipliers = [0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 1.1, 1.2]
    
    best_error = float('inf')
    best_params = None
    
    for base_rate in base_rates:
        for receipt_mult in receipt_multipliers:
            total_error = 0
            test_cases = cases[:50]
            
            for case in test_cases:
                days = case['input']['trip_duration_days']
                receipts = case['input']['total_receipts_amount']
                expected = case['expected_output']
                
                predicted = base_rate * days + receipt_mult * receipts
                error = abs(predicted - expected)
                total_error += error
            
            avg_error = total_error / len(test_cases)
            if avg_error < best_error:
                best_error = avg_error
                best_params = (base_rate, receipt_mult)
    
    print(f"Best simple formula: ${best_params[0]} * days + {best_params[1]} * receipts")
    print(f"Average error: ${best_error:.2f}")
    
    # Test this formula on a few cases
    base_rate, receipt_mult = best_params
    print(f"\nTesting formula: {base_rate} * days + {receipt_mult} * receipts")
    
    for case in cases[:10]:
        days = case['input']['trip_duration_days']
        miles = case['input']['miles_traveled']
        receipts = case['input']['total_receipts_amount']
        expected = case['expected_output']
        
        predicted = base_rate * days + receipt_mult * receipts
        error = abs(predicted - expected)
        
        print(f"{days}d, {miles}mi, ${receipts:.2f} → Expected: ${expected:.2f}, Predicted: ${predicted:.2f}, Error: ${error:.2f}")

def analyze_high_receipt_cases():
    """Look at cases with high receipts to understand caps/penalties"""
    print("\n=== HIGH RECEIPT ANALYSIS ===")
    
    high_receipt_cases = []
    for case in cases:
        receipts = case['input']['total_receipts_amount']
        if receipts > 1000:
            high_receipt_cases.append(case)
    
    high_receipt_cases.sort(key=lambda x: x['input']['total_receipts_amount'])
    
    print("High receipt cases (over $1000):")
    for case in high_receipt_cases[:15]:
        days = case['input']['trip_duration_days']
        miles = case['input']['miles_traveled']
        receipts = case['input']['total_receipts_amount']
        reimbursement = case['expected_output']
        
        ratio = reimbursement / receipts if receipts > 0 else 0
        print(f"{days}d, {miles}mi, ${receipts:.2f} → ${reimbursement:.2f} (ratio: {ratio:.2f})")

if __name__ == "__main__":
    analyze_receipt_correlation()
    analyze_simple_receipt_cases()
    test_receipt_plus_mileage_hypothesis()
    look_for_base_plus_receipts()
    analyze_high_receipt_cases() 