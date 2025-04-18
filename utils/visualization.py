"""
Visualization utilities for the expense tracking system.
This module provides functions for creating visual reports and charts.
"""
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from datetime import datetime
import numpy as np
import io
from matplotlib.figure import Figure
from matplotlib.backends.backend_agg import FigureCanvasAgg
import matplotlib.dates as mdates


def create_expense_pie_chart(expenses, categories_dict=None, title="Expense Distribution by Category", 
                             figsize=(10, 6), save_path=None):
    """
    Create a pie chart showing expense distribution by category.
    
    Args:
        expenses (list): List of Expense objects.
        categories_dict (dict, optional): Dictionary mapping category IDs to Category objects.
        title (str): Chart title.
        figsize (tuple): Figure size (width, height) in inches.
        save_path (str, optional): Path to save the chart. If None, chart will be displayed.
        
    Returns:
        matplotlib.figure.Figure: The created figure.
    """
    # Create dataframe
    from .analysis import expenses_to_dataframe
    df = expenses_to_dataframe(expenses, categories_dict)
    
    if df.empty:
        # Create empty figure with a message
        fig, ax = plt.subplots(figsize=figsize)
        ax.text(0.5, 0.5, "No expense data available", ha='center', va='center', fontsize=14)
        ax.axis('off')
        
        if save_path:
            fig.savefig(save_path, bbox_inches='tight')
        
        return fig
    
    # Filter expenses (negative amounts)
    expense_df = df[df['amount'] < 0].copy()
    
    if expense_df.empty:
        # Create empty figure with a message
        fig, ax = plt.subplots(figsize=figsize)
        ax.text(0.5, 0.5, "No expense data available", ha='center', va='center', fontsize=14)
        ax.axis('off')
        
        if save_path:
            fig.savefig(save_path, bbox_inches='tight')
        
        return fig
    
    # Convert amounts to absolute values
    expense_df['amount'] = expense_df['amount'].abs()
    
    # Group by category
    category_expenses = expense_df.groupby('parent_category')['amount'].sum()
    
    # Get colors from categories if available
    colors = []
    if categories_dict:
        for category in category_expenses.index:
            # Find category in the dictionary
            color = "#3498db"  # Default color
            for cat_id, cat in categories_dict.items():
                if cat.name == category:
                    color = cat.color
                    break
            colors.append(color)
    
    # Create pie chart
    fig, ax = plt.subplots(figsize=figsize)
    
    # Only show wedge labels for categories that are at least 5% of total
    total = category_expenses.sum()
    threshold = total * 0.05
    
    # Create the pie chart
    wedges, texts, autotexts = ax.pie(
        category_expenses,
        labels=None,
        autopct=lambda pct: f'{pct:.1f}%' if pct * total / 100 >= threshold else '',
        startangle=90,
        colors=colors if colors else None
    )
    
    # Set font properties for the percentage labels
    for autotext in autotexts:
        autotext.set_fontsize(10)
        autotext.set_weight('bold')
    
    # Add legend with category names and amounts
    legend_labels = [
        f"{category} (${amount:.2f})" 
        for category, amount in category_expenses.items()
    ]
    ax.legend(wedges, legend_labels, loc="center left", bbox_to_anchor=(1, 0, 0.5, 1))
    
    ax.set_title(title, fontsize=14, pad=20)
    
    plt.tight_layout()
    
    if save_path:
        fig.savefig(save_path, bbox_inches='tight')
    
    return fig


def create_monthly_trend_chart(expenses, categories_dict=None, months=6, 
                               figsize=(12, 6), save_path=None):
    """
    Create a line chart showing expense trends over the past months.
    
    Args:
        expenses (list): List of Expense objects.
        categories_dict (dict, optional): Dictionary mapping category IDs to Category objects.
        months (int): Number of months to include in the chart.
        figsize (tuple): Figure size (width, height) in inches.
        save_path (str, optional): Path to save the chart. If None, chart will be displayed.
        
    Returns:
        matplotlib.figure.Figure: The created figure.
    """
    # Create dataframe
    from .analysis import expenses_to_dataframe
    df = expenses_to_dataframe(expenses, categories_dict)
    
    if df.empty:
        # Create empty figure with a message
        fig, ax = plt.subplots(figsize=figsize)
        ax.text(0.5, 0.5, "No expense data available", ha='center', va='center', fontsize=14)
        ax.axis('off')
        
        if save_path:
            fig.savefig(save_path, bbox_inches='tight')
        
        return fig
    
    # Create month-year column
    df['month_year'] = df['date'].dt.strftime('%Y-%m')
    
    # Get list of recent months
    unique_months = sorted(df['month_year'].unique())
    if len(unique_months) > months:
        unique_months = unique_months[-months:]
    
    # Filter dataframe to recent months
    filtered_df = df[df['month_year'].isin(unique_months)]
    
    # Separate income and expenses
    income_df = filtered_df[filtered_df['amount'] > 0]
    expense_df = filtered_df[filtered_df['amount'] < 0]
    
    # Group by month
    monthly_income = income_df.groupby('month_year')['amount'].sum()
    monthly_expenses = expense_df.groupby('month_year')['amount'].sum().abs()
    
    # Calculate net (income - expenses)
    monthly_net = monthly_income.subtract(monthly_expenses, fill_value=0)
    
    # Create the plot
    fig, ax = plt.subplots(figsize=figsize)
    
    # Get formatted month labels
    month_labels = []
    for month_str in unique_months:
        year, month = month_str.split('-')
        month_dt = datetime(int(year), int(month), 1)
        month_labels.append(month_dt.strftime('%b %Y'))
    
    # X-axis values
    x = range(len(unique_months))
    
    # Plot lines
    ax.plot(x, monthly_income, 'go-', linewidth=2, label='Income')
    ax.plot(x, monthly_expenses, 'ro-', linewidth=2, label='Expenses')
    ax.plot(x, monthly_net, 'bo-', linewidth=2, label='Net')
    
    # Add data labels
    for i, v in enumerate(monthly_income):
        ax.text(i, v + 50, f'${v:.0f}', ha='center', fontsize=9)
    
    for i, v in enumerate(monthly_expenses):
        ax.text(i, v + 50, f'${v:.0f}', ha='center', fontsize=9)
    
    # Set labels and title
    ax.set_xlabel('Month', fontsize=12)
    ax.set_ylabel('Amount ($)', fontsize=12)
    ax.set_title('Monthly Income vs Expenses', fontsize=14, pad=20)
    
    # Set x-axis ticks and labels
    ax.set_xticks(x)
    ax.set_xticklabels(month_labels, rotation=45)
    
    # Add grid
    ax.grid(True, linestyle='--', alpha=0.7)
    
    # Add legend
    ax.legend()
    
    plt.tight_layout()
    
    if save_path:
        fig.savefig(save_path, bbox_inches='tight')
    
    return fig


def create_category_comparison_chart(expenses, comparison_period='last_month', 
                                     categories_dict=None, top_n=5, figsize=(12, 6), 
                                     save_path=None):
    """
    Create a bar chart comparing expenses between two periods by category.
    
    Args:
        expenses (list): List of Expense objects.
        comparison_period (str): Period to compare with ('last_month', 'last_year').
        categories_dict (dict, optional): Dictionary mapping category IDs to Category objects.
        top_n (int): Number of top categories to show.
        figsize (tuple): Figure size (width, height) in inches.
        save_path (str, optional): Path to save the chart. If None, chart will be displayed.
        
    Returns:
        matplotlib.figure.Figure: The created figure.
    """
    # Create dataframe
    from .analysis import expenses_to_dataframe
    df = expenses_to_dataframe(expenses, categories_dict)
    
    if df.empty:
        # Create empty figure with a message
        fig, ax = plt.subplots(figsize=figsize)
        ax.text(0.5, 0.5, "No expense data available", ha='center', va='center', fontsize=14)
        ax.axis('off')
        
        if save_path:
            fig.savefig(save_path, bbox_inches='tight')
        
        return fig
    
    # Filter expenses (negative amounts)
    expense_df = df[df['amount'] < 0].copy()
    expense_df['amount'] = expense_df['amount'].abs()
    
    # Get current month and comparison month
    current_date = datetime.now()
    current_month = current_date.strftime('%Y-%m')
    
    if comparison_period == 'last_year':
        comparison_month = f"{current_date.year - 1}-{current_date.month:02d}"
    else:  # default to last month
        if current_date.month == 1:
            comparison_month = f"{current_date.year - 1}-12"
        else:
            comparison_month = f"{current_date.year}-{current_date.month - 1:02d}"
    
    # Filter data for current and comparison months
    current_df = expense_df[expense_df['date'].dt.strftime('%Y-%m') == current_month]
    comparison_df = expense_df[expense_df['date'].dt.strftime('%Y-%m') == comparison_month]
    
    # Check if there's enough data
    if current_df.empty and comparison_df.empty:
        # Create empty figure with a message
        fig, ax = plt.subplots(figsize=figsize)
        ax.text(0.5, 0.5, "No expense data available for comparison", ha='center', va='center', fontsize=14)
        ax.axis('off')
        
        if save_path:
            fig.savefig(save_path, bbox_inches='tight')
        
        return fig
    
    # Group by category
    current_by_category = current_df.groupby('category')['amount'].sum()
    comparison_by_category = comparison_df.groupby('category')['amount'].sum()
    
    # Find top categories by combining both periods
    all_categories = set(current_by_category.index) | set(comparison_by_category.index)
    combined_totals = {}
    
    for category in all_categories:
        current_amount = current_by_category.get(category, 0)
        comparison_amount = comparison_by_category.get(category, 0)
        combined_totals[category] = current_amount + comparison_amount
    
    # Get top N categories
    top_categories = sorted(combined_totals.items(), key=lambda x: x[1], reverse=True)[:top_n]
    top_category_names = [c[0] for c in top_categories]
    
    # Create arrays for plotting
    current_amounts = [float(current_by_category.get(cat, 0)) for cat in top_category_names]
    comparison_amounts = [float(comparison_by_category.get(cat, 0)) for cat in top_category_names]
    
    # Create plot
    fig, ax = plt.subplots(figsize=figsize)
    
    # Set bar width
    width = 0.35
    x = np.arange(len(top_category_names))
    
    # Plot bars
    bars1 = ax.bar(x - width/2, current_amounts, width, label=f'Current ({current_month})')
    bars2 = ax.bar(x + width/2, comparison_amounts, width, label=f'Previous ({comparison_month})')
    
    # Add data labels
    def add_labels(bars):
        for bar in bars:
            height = bar.get_height()
            if height > 0:
                ax.text(bar.get_x() + bar.get_width()/2., height + 20,
                        f'${height:.0f}', ha='center', va='bottom', fontsize=9)
    
    add_labels(bars1)
    add_labels(bars2)
    
    # Add labels and title
    ax.set_xlabel('Category', fontsize=12)
    ax.set_ylabel('Amount ($)', fontsize=12)
    ax.set_title(f'Category Comparison: {current_month} vs {comparison_month}', fontsize=14, pad=20)
    
    # Set x-axis ticks and labels
    ax.set_xticks(x)
    ax.set_xticklabels(top_category_names, rotation=45, ha='right')
    
    # Add grid
    ax.grid(True, axis='y', linestyle='--', alpha=0.7)
    
    # Add legend
    ax.legend()
    
    plt.tight_layout()
    
    if save_path:
        fig.savefig(save_path, bbox_inches='tight')
    
    return fig


def create_spending_heatmap(expenses, categories_dict=None, figsize=(12, 8), save_path=None):
    """
    Create a heatmap showing spending patterns by day of week and hour.
    
    Args:
        expenses (list): List of Expense objects.
        categories_dict (dict, optional): Dictionary mapping category IDs to Category objects.
        figsize (tuple): Figure size (width, height) in inches.
        save_path (str, optional): Path to save the chart. If None, chart will be displayed.
        
    Returns:
        matplotlib.figure.Figure: The created figure.
    """
    # Create dataframe
    from .analysis import expenses_to_dataframe
    df = expenses_to_dataframe(expenses, categories_dict)
    
    if df.empty:
        # Create empty figure with a message
        fig, ax = plt.subplots(figsize=figsize)
        ax.text(0.5, 0.5, "No expense data available", ha='center', va='center', fontsize=14)
        ax.axis('off')
        
        if save_path:
            fig.savefig(save_path, bbox_inches='tight')
        
        return fig
    
    # Filter expenses (negative amounts)
    expense_df = df[df['amount'] < 0].copy()
    expense_df['amount'] = expense_df['amount'].abs()
    
    # Check if dataframe has the necessary information
    if expense_df.empty:
        # Create empty figure with a message
        fig, ax = plt.subplots(figsize=figsize)
        ax.text(0.5, 0.5, "No expense data available", ha='center', va='center', fontsize=14)
        ax.axis('off')
        
        if save_path:
            fig.savefig(save_path, bbox_inches='tight')
        
        return fig
    
    # Extract hour information if available, otherwise set to morning/afternoon/evening
    if 'hour' not in expense_df.columns:
        # Group by time of day instead
        expense_df['hour_group'] = expense_df['weekday'].map(str)  # Just use weekday
    
    # Create the heatmap data
    if 'hour' in expense_df.columns:
        # Group by weekday and hour
        heatmap_data = expense_df.groupby(['weekday', 'hour'])['amount'].sum().unstack(fill_value=0)
    else:
        # Group by weekday only
        heatmap_data = expense_df.groupby('weekday')['amount'].sum().to_frame()
    
    # Set day names
    day_names = {
        0: 'Monday',
        1: 'Tuesday',
        2: 'Wednesday',
        3: 'Thursday',
        4: 'Friday',
        5: 'Saturday',
        6: 'Sunday'
    }
    
    # Create figure
    fig, ax = plt.subplots(figsize=figsize)
    
    if 'hour' in expense_df.columns:
        # Create heatmap
        sns.heatmap(heatmap_data, ax=ax, cmap='YlOrRd', annot=True, fmt='.0f',
                    linewidths=0.5, cbar_kws={'label': 'Expense Amount ($)'})
        
        # Set labels
        ax.set_ylabel('Day of Week')
        ax.set_xlabel('Hour of Day')
        ax.set_yticklabels([day_names[d] for d in heatmap_data.index])
    else:
        # Create a simple bar chart instead
        days_in_order = sorted(expense_df['weekday'].unique())
        day_expenses = expense_df.groupby('weekday')['amount'].sum()
        
        day_labels = [day_names.get(d, f"Day {d}") for d in days_in_order]
        day_values = [day_expenses.get(d, 0) for d in days_in_order]
        
        ax.bar(day_labels, day_values, color=sns.color_palette("YlOrRd", len(day_labels)))
        
        # Add data labels
        for i, v in enumerate(day_values):
            ax.text(i, v + 10, f'${v:.0f}', ha='center')
        
        ax.set_ylabel('Expense Amount ($)')
        ax.set_xlabel('Day of Week')
        plt.xticks(rotation=45)
        ax.grid(axis='y', linestyle='--', alpha=0.7)
    
    # Set title
    ax.set_title('Spending Patterns by Day of Week', fontsize=14, pad=20)
    
    plt.tight_layout()
    
    if save_path:
        fig.savefig(save_path, bbox_inches='tight')
    
    return fig


def create_budget_progress_chart(expenses, categories_dict, budget_dict, 
                                figsize=(12, 6), save_path=None):
    """
    Create a chart showing budget usage progress for categories.
    
    Args:
        expenses (list): List of Expense objects.
        categories_dict (dict): Dictionary mapping category IDs to Category objects.
        budget_dict (dict): Dictionary mapping category IDs to budget amounts.
        figsize (tuple): Figure size (width, height) in inches.
        save_path (str, optional): Path to save the chart. If None, chart will be displayed.
        
    Returns:
        matplotlib.figure.Figure: The created figure.
    """
    # Create dataframe
    from .analysis import expenses_to_dataframe
    df = expenses_to_dataframe(expenses, categories_dict)
    
    if df.empty or not budget_dict:
        # Create empty figure with a message
        fig, ax = plt.subplots(figsize=figsize)
        ax.text(0.5, 0.5, "No expense data or budget information available", ha='center', va='center', fontsize=14)
        ax.axis('off')
        
        if save_path:
            fig.savefig(save_path, bbox_inches='tight')
        
        return fig
    
    # Filter to current month expenses
    current_month = datetime.now().strftime('%Y-%m')
    current_df = df[(df['date'].dt.strftime('%Y-%m') == current_month) & (df['amount'] < 0)].copy()
    current_df['amount'] = current_df['amount'].abs()
    
    if current_df.empty:
        # Create empty figure with a message
        fig, ax = plt.subplots(figsize=figsize)
        ax.text(0.5, 0.5, "No expense data for the current month", ha='center', va='center', fontsize=14)
        ax.axis('off')
        
        if save_path:
            fig.savefig(save_path, bbox_inches='tight')
        
        return fig
    
    # Get expenses by category
    category_expenses = current_df.groupby('category')['amount'].sum()
    
    # Create data for categories with budgets
    categories = []
    spent_values = []
    budget_values = []
    percent_values = []
    colors = []
    
    for cat_id, budget in budget_dict.items():
        if budget <= 0:
            continue  # Skip categories with no budget
        
        category = categories_dict.get(cat_id)
        if not category:
            continue
        
        # Get amount spent
        spent = category_expenses.get(category.name, 0)
        
        # Calculate percentage
        if budget > 0:
            percent = min(100, (spent / budget) * 100)
        else:
            percent = 0
        
        # Add to lists
        categories.append(category.name)
        spent_values.append(float(spent))
        budget_values.append(float(budget))
        percent_values.append(float(percent))
        
        # Determine color based on percentage
        if percent < 75:
            colors.append('#2ecc71')  # Green
        elif percent < 90:
            colors.append('#f39c12')  # Orange
        else:
            colors.append('#e74c3c')  # Red
    
    # Sort by percentage
    sorted_indices = np.argsort(percent_values)[::-1]
    categories = [categories[i] for i in sorted_indices]
    spent_values = [spent_values[i] for i in sorted_indices]
    budget_values = [budget_values[i] for i in sorted_indices]
    percent_values = [percent_values[i] for i in sorted_indices]
    colors = [colors[i] for i in sorted_indices]
    
    # Create figure
    fig, ax = plt.subplots(figsize=figsize)
    
    if not categories:
        ax.text(0.5, 0.5, "No categories with budget information", ha='center', va='center', fontsize=14)
        ax.axis('off')
    else:
        # Set up x-axis
        x = np.arange(len(categories))
        width = 0.35
        
        # Plot bars
        ax.bar(x, budget_values, width, label='Budget', color='#3498db', alpha=0.3)
        bars = ax.bar(x, spent_values, width, label='Spent', color=colors)
        
        # Add data labels
        for i, (bar, spent, budget, percent) in enumerate(zip(bars, spent_values, budget_values, percent_values)):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + 50,
                    f'${spent:.0f} / ${budget:.0f}\n({percent:.0f}%)',
                    ha='center', va='bottom', fontsize=9)
        
        # Set labels
        ax.set_ylabel('Amount ($)', fontsize=12)
        ax.set_title(f'Budget Progress for {current_month}', fontsize=14, pad=20)
        
        # Set x-axis
        ax.set_xticks(x)
        ax.set_xticklabels(categories, rotation=45, ha='right')
        
        # Add grid
        ax.grid(True, axis='y', linestyle='--', alpha=0.7)
        
        # Add legend
        ax.legend()
    
    plt.tight_layout()
    
    if save_path:
        fig.savefig(save_path, bbox_inches='tight')
    
    return fig


def create_expense_calendar(expenses, categories_dict=None, month=None, year=None,
                           figsize=(12, 8), save_path=None):
    """
    Create a calendar visualization of expenses.
    
    Args:
        expenses (list): List of Expense objects.
        categories_dict (dict, optional): Dictionary mapping category IDs to Category objects.
        month (int, optional): Month to visualize. If None, use current month.
        year (int, optional): Year to visualize. If None, use current year.
        figsize (tuple): Figure size (width, height) in inches.
        save_path (str, optional): Path to save the chart. If None, chart will be displayed.
        
    Returns:
        matplotlib.figure.Figure: The created figure.
    """
    # Create dataframe
    from .analysis import expenses_to_dataframe
    df = expenses_to_dataframe(expenses, categories_dict)
    
    if df.empty:
        # Create empty figure with a message
        fig, ax = plt.subplots(figsize=figsize)
        ax.text(0.5, 0.5, "No expense data available", ha='center', va='center', fontsize=14)
        ax.axis('off')
        
        if save_path:
            fig.savefig(save_path, bbox_inches='tight')
        
        return fig
    
    # Get current month and year if not specified
    if month is None or year is None:
        current_date = datetime.now()
        month = month or current_date.month
        year = year or current_date.year
    
    # Filter expenses for the specified month and year
    filtered_df = df[(df['year'] == year) & (df['month'] == month)]
    
    if filtered_df.empty:
        # Create empty figure with a message
        fig, ax = plt.subplots(figsize=figsize)
        month_name = datetime(year, month, 1).strftime('%B %Y')
        ax.text(0.5, 0.5, f"No expense data for {month_name}", ha='center', va='center', fontsize=14)
        ax.axis('off')
        
        if save_path:
            fig.savefig(save_path, bbox_inches='tight')
        
        return fig
    
    # Create a dict with daily spending
    day_spending = {}
    day_income = {}
    
    for _, row in filtered_df.iterrows():
        day = row['day']
        amount = row['amount']
        
        if amount < 0:  # Expense
            if day not in day_spending:
                day_spending[day] = 0
            day_spending[day] += abs(amount)
        else:  # Income
            if day not in day_income:
                day_income[day] = 0
            day_income[day] += amount
    
    # Create calendar figure
    import calendar
    
    # Get the calendar for the month
    cal = calendar.monthcalendar(year, month)
    
    # Create figure with subplot for each week
    fig, axes = plt.subplots(len(cal), 1, figsize=figsize)
    if len(cal) == 1:
        axes = [axes]
    
    # Get the month name
    month_name = datetime(year, month, 1).strftime('%B %Y')
    
    # Day labels
    day_labels = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
    
    # Find the maximum spending for color scaling
    max_spending = max(day_spending.values()) if day_spending else 100
    
    # Set the title for the entire figure
    fig.suptitle(f'Daily Expenses for {month_name}', fontsize=16, y=0.98)
    
    # Plot each week
    for week_idx, week in enumerate(cal):
        ax = axes[week_idx]
        
        # Create a bar for each day
        day_positions = np.arange(7)
        day_values = []
        
        for day in week:
            if day == 0:  # Day is outside the month
                day_values.append(0)
            else:
                day_values.append(day_spending.get(day, 0))
        
        # Plot the bars
        bars = ax.bar(day_positions, day_values, width=0.7, 
                      color=[plt.cm.YlOrRd(min(1, v / max_spending)) if v > 0 else '#f0f0f0' for v in day_values])
        
        # Add day labels and spending amounts
        for i, (day, value) in enumerate(zip(week, day_values)):
            if day != 0:  # Show only days within the month
                # Day number
                ax.text(i, -max_spending * 0.1, str(day), ha='center', va='top', fontsize=10, fontweight='bold')
                
                # Spending amount
                if value > 0:
                    ax.text(i, value + max_spending * 0.05, f'${value:.0f}', ha='center', va='bottom', fontsize=9)
                
                # Income indicator
                if day in day_income:
                    income = day_income[day]
                    ax.text(i, value + max_spending * 0.15, f'↑${income:.0f}', ha='center', va='bottom', 
                            fontsize=9, color='green')
        
        # Set x-axis labels and ticks
        ax.set_xticks(day_positions)
        ax.set_xticklabels(day_labels)
        
        # Remove y-axis and spines
        ax.set_yticks([])
        for spine in ax.spines.values():
            spine.set_visible(False)
        
        # Set y-axis limit to include space for labels
        ax.set_ylim(-max_spending * 0.2, max_spending * 1.3)
    
    plt.tight_layout(rect=[0, 0, 1, 0.95])
    
    if save_path:
        fig.savefig(save_path, bbox_inches='tight')
    
    return fig


def figure_to_image(fig):
    """
    Convert a matplotlib figure to a bytes object for embedding in tkinter.
    
    Args:
        fig (matplotlib.figure.Figure): The figure to convert.
        
    Returns:
        bytes: The figure as a PNG image in bytes format.
    """
    buf = io.BytesIO()
    fig.savefig(buf, format='png', bbox_inches='tight')
    buf.seek(0)
    return buf.getvalue()
