#!/usr/bin/env python3

import json
import pandas as pd
import numpy as np
from collections import defaultdict
import statistics

# Load the data
with open('public_cases.json', 'r') as f:
    cases = json.load(f)

# Convert to pandas DataFrame for easier analysis
data = []
for case in cases:
    inp = case['input']
    out = case['expected_output']
    data.append({
        'days': inp['trip_duration_days'],
        'miles': inp['miles_traveled'],
        'receipts': inp['total_receipts_amount'],
        'reimbursement': out
    })

df = pd.DataFrame(data)

print("=== BASIC STATISTICS ===")
print(f"Total cases: {len(df)}")
print(f"Days range: {df['days'].min()} - {df['days'].max()}")
print(f"Miles range: {df['miles'].min()} - {df['miles'].max()}")
print(f"Receipts range: ${df['receipts'].min():.2f} - ${df['receipts'].max():.2f}")
print(f"Reimbursement range: ${df['reimbursement'].min():.2f} - ${df['reimbursement'].max():.2f}")
print()

# Analyze patterns by trip duration
print("=== ANALYSIS BY TRIP DURATION ===")
by_days = df.groupby('days').agg({
    'reimbursement': ['count', 'mean', 'std', 'min', 'max'],
    'miles': 'mean',
    'receipts': 'mean'
}).round(2)
print(by_days)
print()

# Look at per-day reimbursement rates
print("=== PER-DAY REIMBURSEMENT RATES ===")
df['per_day_rate'] = df['reimbursement'] / df['days']
by_days_rate = df.groupby('days')['per_day_rate'].agg(['mean', 'std', 'min', 'max']).round(2)
print(by_days_rate)
print()

# Analyze simple cases (low receipts, low miles) to find base per diem
print("=== BASE PER DIEM ANALYSIS (Low receipts < $25, Low miles < 100) ===")
simple_cases = df[(df['receipts'] < 25) & (df['miles'] < 100)]
if len(simple_cases) > 0:
    simple_rate = simple_cases.groupby('days')['per_day_rate'].agg(['count', 'mean', 'std']).round(2)
    print(simple_rate)
    print()

# Look for 5-day bonus pattern mentioned in interviews
print("=== 5-DAY BONUS ANALYSIS ===")
five_day = df[df['days'] == 5]
four_day = df[df['days'] == 4]
six_day = df[df['days'] == 6]

if len(five_day) > 0 and len(four_day) > 0:
    print(f"5-day trips average per-day: ${five_day['per_day_rate'].mean():.2f}")
    print(f"4-day trips average per-day: ${four_day['per_day_rate'].mean():.2f}")
    if len(six_day) > 0:
        print(f"6-day trips average per-day: ${six_day['per_day_rate'].mean():.2f}")
    print()

# Analyze mileage patterns
print("=== MILEAGE ANALYSIS ===")
# Calculate apparent mileage rate
df['miles_per_day'] = df['miles'] / df['days']
df['base_estimate'] = df['days'] * 100  # Assume $100 base per day
df['remaining_after_base'] = df['reimbursement'] - df['base_estimate']
df['apparent_mile_rate'] = np.where(df['miles'] > 0, df['remaining_after_base'] / df['miles'], 0)

# Look at mileage rates by mile ranges
mile_bins = [0, 50, 100, 200, 300, 500, 1000, 2000]
df['mile_bin'] = pd.cut(df['miles'], bins=mile_bins, include_lowest=True)
mile_analysis = df.groupby('mile_bin')['apparent_mile_rate'].agg(['count', 'mean', 'std']).round(3)
print("Apparent mileage rates by mile range:")
print(mile_analysis)
print()

# Look for efficiency bonuses (high miles per day)
print("=== EFFICIENCY ANALYSIS (Miles per day) ===")
efficiency_bins = [0, 50, 100, 150, 200, 250, 300, 500]
df['efficiency_bin'] = pd.cut(df['miles_per_day'], bins=efficiency_bins, include_lowest=True)
efficiency_analysis = df.groupby('efficiency_bin')['per_day_rate'].agg(['count', 'mean', 'std']).round(2)
print("Per-day rates by miles-per-day efficiency:")
print(efficiency_analysis)
print()

# Analyze receipt patterns
print("=== RECEIPT ANALYSIS ===")
# Look at cases with very low receipts (potential penalty)
low_receipts = df[df['receipts'] < 20]
medium_receipts = df[(df['receipts'] >= 20) & (df['receipts'] < 200)]
high_receipts = df[df['receipts'] >= 200]

print(f"Low receipts (<$20) - Count: {len(low_receipts)}, Avg per-day: ${low_receipts['per_day_rate'].mean():.2f}")
print(f"Medium receipts ($20-200) - Count: {len(medium_receipts)}, Avg per-day: ${medium_receipts['per_day_rate'].mean():.2f}")
print(f"High receipts (>$200) - Count: {len(high_receipts)}, Avg per-day: ${high_receipts['per_day_rate'].mean():.2f}")
print()

# Look for specific patterns mentioned in interviews
print("=== SPECIFIC PATTERN ANALYSIS ===")
# Sweet spot combo: 5 days, 180+ miles/day, <$100/day receipts
sweet_spot = df[(df['days'] == 5) & (df['miles_per_day'] >= 180) & (df['receipts']/df['days'] < 100)]
print(f"Sweet spot combo (5 days, 180+ miles/day, <$100/day receipts): {len(sweet_spot)} cases")
if len(sweet_spot) > 0:
    print(f"Average reimbursement: ${sweet_spot['reimbursement'].mean():.2f}")
    print(f"Average per-day rate: ${sweet_spot['per_day_rate'].mean():.2f}")
print()

# Look at some specific examples for pattern recognition
print("=== SAMPLE CASES FOR PATTERN RECOGNITION ===")
print("1-day, low miles, low receipts:")
sample1 = df[(df['days'] == 1) & (df['miles'] < 100) & (df['receipts'] < 20)].head(5)
for _, row in sample1.iterrows():
    print(f"  {row['days']}d, {row['miles']}mi, ${row['receipts']:.2f} → ${row['reimbursement']:.2f}")

print("\n5-day cases:")
sample5 = df[df['days'] == 5].head(5)
for _, row in sample5.iterrows():
    print(f"  {row['days']}d, {row['miles']}mi, ${row['receipts']:.2f} → ${row['reimbursement']:.2f}")

print("\nHigh efficiency cases (>300 miles/day):")
high_eff = df[df['miles_per_day'] > 300].head(5)
for _, row in high_eff.iterrows():
    print(f"  {row['days']}d, {row['miles']}mi ({row['miles_per_day']:.1f}/day), ${row['receipts']:.2f} → ${row['reimbursement']:.2f}") 