"""
Analysis utilities for the expense tracking system.
This module provides functions for analyzing expense data.
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from collections import defaultdict


def expenses_to_dataframe(expenses, categories_dict=None):
    """
    Convert a list of Expense objects to a pandas DataFrame.
    
    Args:
        expenses (list): List of Expense objects.
        categories_dict (dict, optional): Dictionary mapping category IDs to Category objects.
        
    Returns:
        pd.DataFrame: DataFrame containing the expense data.
    """
    if not expenses:
        return pd.DataFrame()
    
    # Extract data from expenses
    data = []
    for expense in expenses:
        # Get category name if dictionary provided
        category_name = "Unknown"
        parent_category = "Unknown"
        
        if categories_dict and expense.category_id in categories_dict:
            category = categories_dict[expense.category_id]
            category_name = category.name
            
            # Get parent category if it exists
            if category.parent_id and category.parent_id in categories_dict:
                parent_category = categories_dict[category.parent_id].name
            elif category.parent_id is None:
                parent_category = category_name  # This is a main category
        
        # Adjust amount sign (negative for expenses, positive for income)
        amount = expense.amount
        if not expense.is_income:
            amount = -amount
        
        # Convert date string to datetime object
        try:
            date_obj = datetime.strptime(expense.date, "%Y-%m-%d")
        except ValueError:
            # If date parsing fails, use the current date
            date_obj = datetime.now()
        
        data.append({
            'expense_id': expense.expense_id,
            'date': date_obj,
            'amount': amount,
            'category_id': expense.category_id,
            'category': category_name,
            'parent_category': parent_category,
            'description': expense.description,
            'payment_method': expense.payment_method,
            'tags': expense.tags,
            'is_income': expense.is_income,
            'year': date_obj.year,
            'month': date_obj.month,
            'day': date_obj.day,
            'weekday': date_obj.weekday(),
            'week': date_obj.isocalendar()[1]  # ISO week number
        })
    
    # Create dataframe
    df = pd.DataFrame(data)
    
    return df


def get_monthly_summary(expenses, categories_dict=None):
    """
    Generate a monthly summary of expenses.
    
    Args:
        expenses (list): List of Expense objects.
        categories_dict (dict, optional): Dictionary mapping category IDs to Category objects.
        
    Returns:
        dict: Dictionary containing monthly summary data.
    """
    # Convert to dataframe
    df = expenses_to_dataframe(expenses, categories_dict)
    
    if df.empty:
        return {
            'total_income': 0,
            'total_expenses': 0,
            'net': 0,
            'by_category': {},
            'by_month': {},
            'by_day': {}
        }
    
    # Calculate totals
    total_income = df[df['amount'] > 0]['amount'].sum()
    total_expenses = abs(df[df['amount'] < 0]['amount'].sum())
    net = total_income - total_expenses
    
    # Group by category
    category_data = df.groupby('category')['amount'].sum().to_dict()
    category_counts = df.groupby('category').size().to_dict()
    
    # Create category summary with both amount and count
    by_category = {}
    for category, amount in category_data.items():
        by_category[category] = {
            'amount': amount,
            'count': category_counts.get(category, 0)
        }
    
    # Group by month
    df['month_year'] = df['date'].dt.strftime('%Y-%m')
    monthly_data = df.groupby('month_year').agg({
        'amount': ['sum', 'mean', 'count']
    })
    monthly_data.columns = ['total', 'average', 'count']
    by_month = monthly_data.to_dict()
    
    # Group by day of week for current month
    current_month = datetime.now().strftime('%Y-%m')
    current_month_data = df[df['date'].dt.strftime('%Y-%m') == current_month]
    
    if not current_month_data.empty:
        # Map weekday number to name
        day_names = {
            0: 'Monday',
            1: 'Tuesday',
            2: 'Wednesday',
            3: 'Thursday',
            4: 'Friday',
            5: 'Saturday',
            6: 'Sunday'
        }
        
        current_month_data['weekday_name'] = current_month_data['weekday'].map(day_names)
        daily_data = current_month_data.groupby('weekday_name').agg({
            'amount': ['sum', 'mean', 'count']
        })
        daily_data.columns = ['total', 'average', 'count']
        by_day = daily_data.to_dict()
    else:
        by_day = {}
    
    return {
        'total_income': float(total_income),
        'total_expenses': float(total_expenses),
        'net': float(net),
        'by_category': by_category,
        'by_month': by_month,
        'by_day': by_day
    }


def detect_spending_anomalies(expenses, categories_dict=None, threshold_factor=2.0):
    """
    Detect anomalies in spending patterns.
    
    Args:
        expenses (list): List of Expense objects.
        categories_dict (dict, optional): Dictionary mapping category IDs to Category objects.
        threshold_factor (float): Factor to determine what's considered an anomaly.
        
    Returns:
        list: List of anomalies found.
    """
    # Convert to dataframe
    df = expenses_to_dataframe(expenses, categories_dict)
    
    if df.empty:
        return []
    
    anomalies = []
    
    # Check for unusually large transactions
    # Group expenses by category
    category_stats = df.groupby('category')['amount'].agg(['mean', 'std'])
    
    # For each category, find expenses that deviate significantly from the mean
    for category, stats in category_stats.iterrows():
        mean_amount = stats['mean']
        std_amount = stats['std']
        
        # If std is NaN (only one expense in category) or 0, use the mean
        if pd.isna(std_amount) or std_amount == 0:
            threshold = abs(mean_amount) * threshold_factor
        else:
            threshold = abs(mean_amount) + (std_amount * threshold_factor)
        
        # Get expenses in this category that exceed the threshold
        category_expenses = df[df['category'] == category]
        outliers = category_expenses[abs(category_expenses['amount']) > threshold]
        
        for _, row in outliers.iterrows():
            anomalies.append({
                'expense_id': row['expense_id'],
                'date': row['date'].strftime('%Y-%m-%d'),
                'amount': float(row['amount']),
                'category': category,
                'description': row['description'],
                'anomaly_type': 'large_transaction',
                'threshold': float(threshold),
                'average': float(mean_amount)
            })
    
    # Check for unusual spending frequency
    # Calculate the average number of transactions per day
    df['date_str'] = df['date'].dt.strftime('%Y-%m-%d')
    transactions_per_day = df.groupby('date_str').size()
    
    mean_transactions = transactions_per_day.mean()
    std_transactions = transactions_per_day.std()
    
    # If std is NaN or 0, use the mean
    if pd.isna(std_transactions) or std_transactions == 0:
        freq_threshold = mean_transactions * threshold_factor
    else:
        freq_threshold = mean_transactions + (std_transactions * threshold_factor)
    
    # Find days with unusual transaction frequency
    unusual_days = transactions_per_day[transactions_per_day > freq_threshold]
    
    for day, count in unusual_days.items():
        anomalies.append({
            'date': day,
            'count': int(count),
            'anomaly_type': 'high_frequency',
            'threshold': float(freq_threshold),
            'average': float(mean_transactions)
        })
    
    return anomalies


def compare_time_periods(expenses, categories_dict=None, period_type='month', 
                         current_period=None, previous_period=None):
    """
    Compare expenses between two time periods.
    
    Args:
        expenses (list): List of Expense objects.
        categories_dict (dict, optional): Dictionary mapping category IDs to Category objects.
        period_type (str): Type of period to compare ('day', 'week', 'month', 'year').
        current_period (str, optional): Current period in format appropriate for period_type.
                                       If None, uses the current period.
        previous_period (str, optional): Previous period in format appropriate for period_type.
                                        If None, uses the period before current_period.
        
    Returns:
        dict: Dictionary containing comparison data.
    """
    # Convert to dataframe
    df = expenses_to_dataframe(expenses, categories_dict)
    
    if df.empty:
        return {
            'current_period': {},
            'previous_period': {},
            'change': {},
            'percent_change': {}
        }
    
    # Determine current and previous periods if not provided
    now = datetime.now()
    
    if period_type == 'day':
        if not current_period:
            current_period = now.strftime('%Y-%m-%d')
        
        if not previous_period:
            prev_day = now - timedelta(days=1)
            previous_period = prev_day.strftime('%Y-%m-%d')
        
        # Filter data for the specified days
        current_df = df[df['date'].dt.strftime('%Y-%m-%d') == current_period]
        previous_df = df[df['date'].dt.strftime('%Y-%m-%d') == previous_period]
        
        period_name = 'day'
    
    elif period_type == 'week':
        if not current_period:
            current_week = now.isocalendar()[1]
            current_year = now.year
            current_period = f"{current_year}-W{current_week:02d}"
        else:
            # Parse "YYYY-WNN" format
            parts = current_period.split('-W')
            current_year = int(parts[0])
            current_week = int(parts[1])
        
        if not previous_period:
            # Calculate previous week
            prev_date = now - timedelta(weeks=1)
            prev_week = prev_date.isocalendar()[1]
            prev_year = prev_date.year
            previous_period = f"{prev_year}-W{prev_week:02d}"
        else:
            # Parse "YYYY-WNN" format
            parts = previous_period.split('-W')
            prev_year = int(parts[0])
            prev_week = int(parts[1])
        
        # Filter data for the specified weeks
        current_df = df[(df['year'] == current_year) & (df['week'] == current_week)]
        previous_df = df[(df['year'] == prev_year) & (df['week'] == prev_week)]
        
        period_name = 'week'
    
    elif period_type == 'year':
        if not current_period:
            current_period = str(now.year)
        
        if not previous_period:
            previous_period = str(int(current_period) - 1)
        
        # Filter data for the specified years
        current_df = df[df['year'] == int(current_period)]
        previous_df = df[df['year'] == int(previous_period)]
        
        period_name = 'year'
    
    else:  # Default to month
        if not current_period:
            current_period = now.strftime('%Y-%m')
        
        if not previous_period:
            if now.month == 1:
                prev_month = 12
                prev_year = now.year - 1
            else:
                prev_month = now.month - 1
                prev_year = now.year
            previous_period = f"{prev_year}-{prev_month:02d}"
        
        # Filter data for the specified months
        current_df = df[df['date'].dt.strftime('%Y-%m') == current_period]
        previous_df = df[df['date'].dt.strftime('%Y-%m') == previous_period]
        
        period_name = 'month'
    
    # Calculate total income and expenses for each period
    current_income = current_df[current_df['amount'] > 0]['amount'].sum() if not current_df.empty else 0
    current_expenses = abs(current_df[current_df['amount'] < 0]['amount'].sum()) if not current_df.empty else 0
    current_net = current_income - current_expenses
    
    previous_income = previous_df[previous_df['amount'] > 0]['amount'].sum() if not previous_df.empty else 0
    previous_expenses = abs(previous_df[previous_df['amount'] < 0]['amount'].sum()) if not previous_df.empty else 0
    previous_net = previous_income - previous_expenses
    
    # Calculate changes
    income_change = current_income - previous_income
    expense_change = current_expenses - previous_expenses
    net_change = current_net - previous_net
    
    # Calculate percent changes (avoid division by zero)
    income_percent = (income_change / previous_income * 100) if previous_income != 0 else float('inf')
    expense_percent = (expense_change / previous_expenses * 100) if previous_expenses != 0 else float('inf')
    net_percent = (net_change / abs(previous_net) * 100) if previous_net != 0 else float('inf')
    
    # Compare spending by category
    current_by_category = current_df.groupby('category')['amount'].sum().to_dict() if not current_df.empty else {}
    previous_by_category = previous_df.groupby('category')['amount'].sum().to_dict() if not previous_df.empty else {}
    
    # Combine all categories from both periods
    all_categories = set(current_by_category.keys()) | set(previous_by_category.keys())
    
    category_comparison = {}
    for category in all_categories:
        current_amount = current_by_category.get(category, 0)
        previous_amount = previous_by_category.get(category, 0)
        
        change = current_amount - previous_amount
        percent = (change / abs(previous_amount) * 100) if previous_amount != 0 else float('inf')
        
        category_comparison[category] = {
            'current': float(current_amount),
            'previous': float(previous_amount),
            'change': float(change),
            'percent_change': float(percent)
        }
    
    return {
        'period_type': period_name,
        'current_period': {
            'label': current_period,
            'income': float(current_income),
            'expenses': float(current_expenses),
            'net': float(current_net),
            'by_category': current_by_category
        },
        'previous_period': {
            'label': previous_period,
            'income': float(previous_income),
            'expenses': float(previous_expenses),
            'net': float(previous_net),
            'by_category': previous_by_category
        },
        'change': {
            'income': float(income_change),
            'expenses': float(expense_change),
            'net': float(net_change)
        },
        'percent_change': {
            'income': float(income_percent) if not pd.isna(income_percent) else 0,
            'expenses': float(expense_percent) if not pd.isna(expense_percent) else 0,
            'net': float(net_percent) if not pd.isna(net_percent) else 0
        },
        'categories': category_comparison
    }


def predict_monthly_expenses(expenses, categories_dict=None, months_to_predict=3):
    """
    Predict future monthly expenses based on historical data.
    
    Args:
        expenses (list): List of Expense objects.
        categories_dict (dict, optional): Dictionary mapping category IDs to Category objects.
        months_to_predict (int): Number of months to predict.
        
    Returns:
        dict: Dictionary containing prediction data.
    """
    # Convert to dataframe
    df = expenses_to_dataframe(expenses, categories_dict)
    
    if df.empty:
        return {
            'predictions': {},
            'confidence': 'low',
            'message': 'Not enough data for prediction'
        }
    
    # Group by month and calculate total expenses (negative amounts only)
    df['month_year'] = df['date'].dt.strftime('%Y-%m')
    monthly_expenses = df[df['amount'] < 0].groupby('month_year')['amount'].sum().abs()
    
    # Need at least 3 months of data for a meaningful prediction
    if len(monthly_expenses) < 3:
        return {
            'predictions': {},
            'confidence': 'low',
            'message': 'Need at least 3 months of data for prediction'
        }
    
    # Convert the Series to a DataFrame for easier manipulation
    monthly_df = monthly_expenses.reset_index()
    monthly_df.columns = ['month_year', 'expenses']
    
    # Add a numeric month index for regression
    monthly_df['month_index'] = range(len(monthly_df))
    
    # Simple linear regression
    x = monthly_df['month_index'].values.reshape(-1, 1)
    y = monthly_df['expenses'].values
    
    # Calculate slope and intercept manually
    x_mean = np.mean(x)
    y_mean = np.mean(y)
    
    # Calculate the slope (m)
    numerator = np.sum((x - x_mean) * (y - y_mean))
    denominator = np.sum((x - x_mean) ** 2)
    
    if denominator == 0:
        # If all x values are the same, use the mean as prediction
        slope = 0
        intercept = y_mean
    else:
        slope = numerator / denominator
        # Calculate the y-intercept (b)
        intercept = y_mean - (slope * x_mean)
    
    # Generate predictions for future months
    predictions = {}
    confidence = 'medium'  # Default confidence level
    
    # Get the last month in the data
    last_month_str = monthly_df['month_year'].iloc[-1]
    last_year, last_month = map(int, last_month_str.split('-'))
    
    # Calculate R-squared to determine prediction confidence
    y_pred = intercept + slope * x
    ss_total = np.sum((y - y_mean) ** 2)
    ss_residual = np.sum((y - y_pred) ** 2)
    
    if ss_total == 0:
        r_squared = 0
    else:
        r_squared = 1 - (ss_residual / ss_total)
    
    # Set confidence based on R-squared
    if r_squared > 0.7:
        confidence = 'high'
    elif r_squared < 0.3:
        confidence = 'low'
    
    # Generate predictions for future months
    for i in range(1, months_to_predict + 1):
        # Calculate next month and year
        next_month = last_month + i
        next_year = last_year
        
        while next_month > 12:
            next_month -= 12
            next_year += 1
        
        # Format month-year string
        next_month_str = f"{next_year}-{next_month:02d}"
        
        # Predict expenses for this month
        next_index = monthly_df['month_index'].iloc[-1] + i
        predicted_expense = intercept + (slope * next_index)
        
        # Ensure predicted amount is positive
        predicted_expense = max(0, predicted_expense)
        
        predictions[next_month_str] = float(predicted_expense)
    
    # Also predict by category if there's enough data
    category_predictions = {}
    
    if len(monthly_df) >= 3:
        # Group by category and month
        category_monthly = df[df['amount'] < 0].groupby(['category', 'month_year'])['amount'].sum().abs()
        
        # Get list of categories with at least 3 data points
        category_counts = category_monthly.groupby('category').count()
        valid_categories = category_counts[category_counts >= 3].index.tolist()
        
        for category in valid_categories:
            # Get monthly data for this category
            cat_monthly = category_monthly[category].reset_index()
            cat_monthly.columns = ['month_year', 'expenses']
            
            # Add month index
            cat_monthly['month_index'] = range(len(cat_monthly))
            
            # Simple linear regression
            cat_x = cat_monthly['month_index'].values.reshape(-1, 1)
            cat_y = cat_monthly['expenses'].values
            
            # Calculate slope and intercept
            cat_x_mean = np.mean(cat_x)
            cat_y_mean = np.mean(cat_y)
            
            cat_numerator = np.sum((cat_x - cat_x_mean) * (cat_y - cat_y_mean))
            cat_denominator = np.sum((cat_x - cat_x_mean) ** 2)
            
            if cat_denominator == 0:
                cat_slope = 0
                cat_intercept = cat_y_mean
            else:
                cat_slope = cat_numerator / cat_denominator
                cat_intercept = cat_y_mean - (cat_slope * cat_x_mean)
            
            # Generate predictions
            cat_predictions = {}
            for i in range(1, months_to_predict + 1):
                next_month = last_month + i
                next_year = last_year
                
                while next_month > 12:
                    next_month -= 12
                    next_year += 1
                
                next_month_str = f"{next_year}-{next_month:02d}"
                next_index = cat_monthly['month_index'].iloc[-1] + i
                predicted_expense = cat_intercept + (cat_slope * next_index)
                
                # Ensure predicted amount is positive
                predicted_expense = max(0, predicted_expense)
                
                cat_predictions[next_month_str] = float(predicted_expense)
            
            category_predictions[category] = cat_predictions
    
    return {
        'predictions': predictions,
        'by_category': category_predictions,
        'confidence': confidence,
        'r_squared': float(r_squared),
        'trend': 'increasing' if slope > 0 else ('stable' if slope == 0 else 'decreasing'),
        'months_analyzed': len(monthly_df)
    }


def get_spending_suggestions(expenses, categories_dict=None, budget_dict=None):
    """
    Generate spending suggestions based on expense data and budgets.
    
    Args:
        expenses (list): List of Expense objects.
        categories_dict (dict, optional): Dictionary mapping category IDs to Category objects.
        budget_dict (dict, optional): Dictionary mapping category IDs to budget amounts.
        
    Returns:
        list: List of spending suggestions.
    """
    # Convert to dataframe
    df = expenses_to_dataframe(expenses, categories_dict)
    
    if df.empty:
        return []
    
    suggestions = []
    
    # Get current month expenses
    current_month = datetime.now().strftime('%Y-%m')
    current_month_data = df[df['date'].dt.strftime('%Y-%m') == current_month]
    
    # If no data for current month, return empty suggestions
    if current_month_data.empty:
        return []
    
    # Check budget compliance if budget_dict is provided
    if budget_dict:
        # Get expenses by category for current month (only expenses, not income)
        expenses_by_category = current_month_data[current_month_data['amount'] < 0].groupby('category')['amount'].sum().abs()
        
        for category, amount in expenses_by_category.items():
            # Find category ID
            category_id = None
            for cid, cat in categories_dict.items():
                if cat.name == category:
                    category_id = cid
                    break
            
            if category_id and category_id in budget_dict:
                budget = budget_dict[category_id]
                
                if budget > 0:  # Only check if budget is set
                    percent_used = (amount / budget) * 100
                    
                    if percent_used > 90:
                        suggestions.append({
                            'type': 'budget_warning',
                            'category': category,
                            'amount_spent': float(amount),
                            'budget': float(budget),
                            'percent_used': float(percent_used),
                            'message': f"You've used {percent_used:.1f}% of your {category} budget for this month."
                        })
    
    # Check for categories with high spending growth
    # Need at least 2 months of data
    if len(df['month_year'].unique()) >= 2:
        # Get the last complete month
        last_month = (datetime.now().replace(day=1) - timedelta(days=1)).strftime('%Y-%m')
        last_month_data = df[df['date'].dt.strftime('%Y-%m') == last_month]
        
        if not last_month_data.empty and not current_month_data.empty:
            # Compare spending by category
            last_expenses = last_month_data[last_month_data['amount'] < 0].groupby('category')['amount'].sum().abs()
            current_expenses = current_month_data[current_month_data['amount'] < 0].groupby('category')['amount'].sum().abs()
            
            # Find categories with significant increase
            for category in current_expenses.index:
                if category in last_expenses.index:
                    last_amount = last_expenses[category]
                    current_amount = current_expenses[category]
                    
                    # Check if spending increased by more than 30%
                    if current_amount > last_amount * 1.3 and current_amount > 50:  # Only consider significant amounts
                        suggestions.append({
                            'type': 'spending_increase',
                            'category': category,
                            'last_month': float(last_amount),
                            'current_month': float(current_amount),
                            'percent_increase': float((current_amount / last_amount - 1) * 100),
                            'message': f"Your spending in {category} has increased by {(current_amount / last_amount - 1) * 100:.1f}% compared to last month."
                        })
    
    # Check for recurring expenses that might be subscriptions
    recurring_payments = defaultdict(list)
    
    # Group expenses by description and find those with similar amounts
    for _, row in df.iterrows():
        if row['amount'] < 0:  # Only consider expenses, not income
            # Normalize description by removing dates and numbers
            desc = ''.join([c for c in row['description'].lower() if not c.isdigit() and c.isalnum() or c.isspace()]).strip()
            
            if desc:
                recurring_payments[desc].append({
                    'date': row['date'],
                    'amount': abs(row['amount']),
                    'category': row['category']
                })
    
    # Find potential subscriptions
    for desc, payments in recurring_payments.items():
        if len(payments) >= 3:  # At least 3 occurrences
            # Check if amounts are similar
            amounts = [p['amount'] for p in payments]
            mean_amount = np.mean(amounts)
            
            # If amounts are within 5% of each other
            if all(abs(a - mean_amount) / mean_amount < 0.05 for a in amounts):
                # Sort by date
                sorted_payments = sorted(payments, key=lambda x: x['date'])
                
                # Check if dates are roughly monthly
                dates = [p['date'] for p in sorted_payments]
                
                if len(dates) >= 3:
                    # Calculate average number of days between payments
                    intervals = [(dates[i+1] - dates[i]).days for i in range(len(dates)-1)]
                    avg_interval = np.mean(intervals)
                    
                    # If average interval is between 25 and 35 days (roughly monthly)
                    if 25 <= avg_interval <= 35:
                        suggestions.append({
                            'type': 'potential_subscription',
                            'description': desc,
                            'average_amount': float(mean_amount),
                            'occurrences': len(payments),
                            'category': payments[0]['category'],
                            'message': f"You may have a monthly subscription to '{desc}' for approximately ${mean_amount:.2f}."
                        })
    
    # Suggest categories that may need a budget
    categories_without_budget = []
    
    if budget_dict and categories_dict:
        for cid, category in categories_dict.items():
            # Skip categories that already have a budget
            if cid in budget_dict and budget_dict[cid] > 0:
                continue
            
            # Check if this category has significant spending
            category_spending = current_month_data[
                (current_month_data['category'] == category.name) & 
                (current_month_data['amount'] < 0)
            ]['amount'].sum().abs()
            
            if category_spending > 100:  # Only suggest for categories with significant spending
                categories_without_budget.append({
                    'category': category.name,
                    'amount': float(category_spending),
                    'message': f"Consider setting a budget for '{category.name}' based on your spending of ${category_spending:.2f} this month."
                })
    
    if categories_without_budget:
        suggestions.append({
            'type': 'missing_budgets',
            'categories': categories_without_budget
        })
    
    return suggestions
