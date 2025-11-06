"""
Data Cleaning Agent - Example Usage
Run this file directly: python run_example.py
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import pandas as pd
import numpy as np
from agents.simple_cleaning_agent import SimpleCleaningAgent

# Create a messy sample dataset
print("Creating messy sample dataset...")
np.random.seed(42)

data = {
    'User ID': range(1, 101),
    'First Name': ['User_' + str(i) if i % 10 != 0 else np.nan for i in range(1, 101)],
    'Age': [np.random.randint(18, 80) if i % 8 != 0 else np.nan for i in range(1, 101)],
    'Annual Salary': [np.random.randint(30000, 150000) if i % 7 != 0 else np.nan for i in range(1, 101)],
    'Department': np.random.choice(['Sales', 'Engineering', 'Marketing', 'HR'], 100),
    'Performance Score': [np.random.uniform(1, 5) if i % 6 != 0 else np.nan for i in range(1, 101)],
}

# Add some outliers
data['Annual Salary'][5] = 999999  # Unrealistic salary
data['Annual Salary'][15] = 1000   # Unrealistically low
data['Age'][10] = 150              # Impossible age

df = pd.DataFrame(data)

# Add some duplicates
df = pd.concat([df, df.iloc[[0, 1, 2]]], ignore_index=True)

print(f"\n📊 Original Dataset:")
print(f"   Shape: {df.shape}")
print(f"   Missing values: {df.isnull().sum().sum()}")
print(f"   Duplicate rows: {df.duplicated().sum()}")
print(f"\n   First few rows:")
print(df.head())

print("\n" + "="*60)
print("🔧 Starting Data Cleaning Agent...")
print("="*60 + "\n")

# Create and run the agent
agent = SimpleCleaningAgent(df)
result = agent.run()

# Extract results
cleaned_df = result['cleaned_df']
report = result['report']

print("\n" + "="*60)
print("✅ CLEANING COMPLETE!")
print("="*60)

print(f"\n📊 Cleaned Dataset:")
print(f"   Shape: {cleaned_df.shape}")
print(f"   Missing values: {cleaned_df.isnull().sum().sum()}")
print(f"   Duplicate rows: {cleaned_df.duplicated().sum()}")

print(f"\n⭐ Quality Score: {report['quality_score']}/10")
print(f"\n💬 Feedback:")
print(f"   {report['feedback']}")

print(f"\n📋 Actions Taken ({report['summary']['iterations']} steps):")
for i, action in enumerate(report['actions_taken'], 1):
    print(f"   {i}. {action}")

if report['suggestions']:
    print(f"\n💡 Suggestions:")
    for suggestion in report['suggestions']:
        print(f"   • {suggestion}")

print(f"\n📈 Summary:")
print(f"   • Rows: {report['summary']['original_shape'][0]} → {report['summary']['cleaned_shape'][0]} "
      f"({report['summary']['rows_removed']} removed)")
print(f"   • Columns: {report['summary']['original_shape'][1]} → {report['summary']['cleaned_shape'][1]}")

print(f"\n   Cleaned data preview:")
print(cleaned_df.head())

# Save cleaned data
os.makedirs('data/cleaned', exist_ok=True)
output_file = 'data/cleaned/example_cleaned.csv'
cleaned_df.to_csv(output_file, index=False)
print(f"\n💾 Cleaned data saved to: {output_file}")

print("\n" + "="*60)
print("🎉 Demo complete!")
print("="*60)
