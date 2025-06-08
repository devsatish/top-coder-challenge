#!/usr/bin/env python3

import json
import math

# Load the data
with open('public_cases.json', 'r') as f:
    cases = json.load(f)

def find_best_linear_combination():
    """Try various linear combinations to find the best fit"""
    print("=== FINDING BEST LINEAR COMBINATION ===")
    
    best_error = float('inf')
    best_formula = None
    
    # Test different base rates per day
    for base_rate in range(50, 200, 25):
        # Test different receipt multipliers
        for receipt_mult in [0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]:
            # Test with and without mileage component
            for mile_rate in [0, 0.25, 0.5, 0.75, 1.0]:
                total_error = 0
                test_cases = cases[:100]  # Use more cases for better accuracy
                
                for case in test_cases:
                    days = case['input']['trip_duration_days']
                    miles = case['input']['miles_traveled']
                    receipts = case['input']['total_receipts_amount']
                    expected = case['expected_output']
                    
                    predicted = base_rate * days + receipt_mult * receipts + mile_rate * miles
                    error = abs(predicted - expected)
                    total_error += error
                
                avg_error = total_error / len(test_cases)
                if avg_error < best_error:
                    best_error = avg_error
                    best_formula = (base_rate, receipt_mult, mile_rate)
    
    base_rate, receipt_mult, mile_rate = best_formula
    print(f"Best linear formula: ${base_rate} * days + {receipt_mult:.2f} * receipts + {mile_rate:.2f} * miles")
    print(f"Average error: ${best_error:.2f}")
    
    return best_formula

def test_progressive_formulas():
    """Test increasingly complex formulas"""
    print("\n=== TESTING PROGRESSIVE FORMULAS ===")
    
    def formula_v1(days, miles, receipts):
        """Simple linear combination"""
        return 125 * days + 0.6 * receipts + 0.5 * miles
    
    def formula_v2(days, miles, receipts):
        """Add efficiency bonus"""
        base = 125 * days + 0.6 * receipts + 0.5 * miles
        efficiency = miles / days if days > 0 else 0
        if efficiency > 150:
            base += (efficiency - 150) * 0.5
        return base
    
    def formula_v3(days, miles, receipts):
        """Add trip length adjustments"""
        # Base per day varies by trip length
        if days == 1:
            base_per_day = 110
        elif days <= 3:
            base_per_day = 120
        elif days <= 5:
            base_per_day = 100
        else:
            base_per_day = 95
        
        base = base_per_day * days + 0.6 * receipts + 0.5 * miles
        return base
    
    def formula_v4(days, miles, receipts):
        """Add mileage tiers"""
        # Base calculation
        if days == 1:
            base_per_day = 110
        elif days <= 3:
            base_per_day = 120
        elif days <= 5:
            base_per_day = 100
        else:
            base_per_day = 95
        
        base = base_per_day * days + 0.6 * receipts
        
        # Tiered mileage
        if miles <= 100:
            mileage_component = miles * 1.0
        elif miles <= 300:
            mileage_component = 100 * 1.0 + (miles - 100) * 0.8
        else:
            mileage_component = 100 * 1.0 + 200 * 0.8 + (miles - 300) * 0.6
        
        return base + mileage_component
    
    def formula_v5(days, miles, receipts):
        """Add receipt processing tiers"""
        # Base calculation
        if days == 1:
            base_per_day = 110
        elif days <= 3:
            base_per_day = 120
        elif days <= 5:
            base_per_day = 100
        else:
            base_per_day = 95
        
        base = base_per_day * days
        
        # Tiered receipt processing
        if receipts <= 100:
            receipt_component = receipts * 0.8
        elif receipts <= 500:
            receipt_component = 100 * 0.8 + (receipts - 100) * 0.6
        else:
            receipt_component = 100 * 0.8 + 400 * 0.6 + (receipts - 500) * 0.4
        
        # Tiered mileage
        if miles <= 100:
            mileage_component = miles * 1.0
        elif miles <= 300:
            mileage_component = 100 * 1.0 + (miles - 100) * 0.8
        else:
            mileage_component = 100 * 1.0 + 200 * 0.8 + (miles - 300) * 0.6
        
        return base + receipt_component + mileage_component
    
    formulas = [
        ("Simple linear", formula_v1),
        ("With efficiency bonus", formula_v2), 
        ("With trip length adjustment", formula_v3),
        ("With mileage tiers", formula_v4),
        ("With receipt tiers", formula_v5),
    ]
    
    test_cases = cases[:100]
    
    for name, formula_func in formulas:
        total_error = 0
        within_10 = 0
        within_25 = 0
        
        for case in test_cases:
            days = case['input']['trip_duration_days']
            miles = case['input']['miles_traveled']
            receipts = case['input']['total_receipts_amount']
            expected = case['expected_output']
            
            predicted = formula_func(days, miles, receipts)
            error = abs(predicted - expected)
            total_error += error
            
            if error <= 10:
                within_10 += 1
            if error <= 25:
                within_25 += 1
        
        avg_error = total_error / len(test_cases)
        print(f"{name}: Avg error ${avg_error:.2f}, Within $10: {within_10}/{len(test_cases)}, Within $25: {within_25}/{len(test_cases)}")

def analyze_outliers_carefully():
    """Look at the biggest errors to understand what's missing"""
    print("\n=== ANALYZING OUTLIERS ===")
    
    def current_best_formula(days, miles, receipts):
        """Current best guess formula"""
        if days == 1:
            base_per_day = 110
        elif days <= 3:
            base_per_day = 120
        elif days <= 5:
            base_per_day = 100
        else:
            base_per_day = 95
        
        base = base_per_day * days
        
        # Tiered receipt processing
        if receipts <= 100:
            receipt_component = receipts * 0.8
        elif receipts <= 500:
            receipt_component = 100 * 0.8 + (receipts - 100) * 0.6
        else:
            receipt_component = 100 * 0.8 + 400 * 0.6 + (receipts - 500) * 0.4
        
        # Tiered mileage
        if miles <= 100:
            mileage_component = miles * 1.0
        elif miles <= 300:
            mileage_component = 100 * 1.0 + (miles - 100) * 0.8
        else:
            mileage_component = 100 * 1.0 + 200 * 0.8 + (miles - 300) * 0.6
        
        return base + receipt_component + mileage_component
    
    # Find cases with biggest errors
    errors = []
    for case in cases[:200]:
        days = case['input']['trip_duration_days']
        miles = case['input']['miles_traveled']
        receipts = case['input']['total_receipts_amount']
        expected = case['expected_output']
        
        predicted = current_best_formula(days, miles, receipts)
        error = abs(predicted - expected)
        errors.append((error, case, predicted))
    
    # Sort by error and look at worst cases
    errors.sort(reverse=True)
    
    print("Worst prediction errors:")
    for error, case, predicted in errors[:15]:
        days = case['input']['trip_duration_days']
        miles = case['input']['miles_traveled']
        receipts = case['input']['total_receipts_amount']
        expected = case['expected_output']
        
        print(f"{days}d, {miles}mi, ${receipts:.2f} → Expected: ${expected:.2f}, Predicted: ${predicted:.2f}, Error: ${error:.2f}")

if __name__ == "__main__":
    best_formula = find_best_linear_combination()
    test_progressive_formulas()
    analyze_outliers_carefully() 