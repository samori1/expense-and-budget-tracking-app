import sqlite3


# Database connection function using context managers
def db_execute(cursor, query, params=(), fetch=False):
    """
    Executes the database connections using context managers.

    Parameters:
    - cursor: The database cursor to execute the query.
    - query: The SQL query to execute.
    - params: Parameters for the query.
    - fetch: Whether to fetch results from the query.

    Returns:
    - list: Fetched results if fetch is True, otherwise an empty list.
    """
    try:
        cursor.execute(query, params)
        if fetch:
            return cursor.fetchall()
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return


# Function to initialise tables for expenses, income, and categories
def initialise_database(cursor):
    """
    Initialise the SQLite database with tables for expenses, income, budget
    and financial goals.

    Parameters:
    - cursor: The database cursor to execute the table creation queries.

    Returns:
    - None
    """
    db_execute(cursor, '''
    CREATE TABLE IF NOT EXISTS expenses (
        id INTEGER PRIMARY KEY,
        category TEXT NOT NULL,
        amount REAL NOT NULL,
        date TEXT NOT NULL
    )
    ''')

    db_execute(cursor, '''
    CREATE TABLE IF NOT EXISTS income (
        id INTEGER PRIMARY KEY,
        category TEXT NOT NULL,
        amount REAL NOT NULL,
        date TEXT NOT NULL
    )
    ''')

    db_execute(cursor, '''
    CREATE TABLE IF NOT EXISTS budgets (
        id INTEGER PRIMARY KEY,
        category TEXT NOT NULL,
        budget_limit REAL NOT NULL
    )
    ''')

    db_execute(cursor, '''
    CREATE TABLE IF NOT EXISTS goals (
        id INTEGER PRIMARY KEY,
        goal TEXT NOT NULL,
        target_amount REAL NOT NULL,
        progress REAL DEFAULT 0
    )
    ''')


# Generic records viewing function
def view_records(cursor, table):
    """
    Retrieves and displays all records from a specified table.

    Parameters:
    - cursor: The database cursor to execute the query.
    - table: The name of the table to retrieve records from.

    Returns:
    - List of records if found, otherwise a message indicating no records found
    """
    try:
        records = db_execute(cursor, f'SELECT * FROM {table}', fetch=True)
        for record in records:
            return record
        else:
            return f"No records found in {table}"
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return


# Expense functions
def add_expense(cursor, category, amount, date):
    """
    Adds a new expense category to database.
    
    Parameters:
    - cursor: The database cursor to execute the query.
    - category: The category of the expense.
    - amount: The amount of the expense.
    - date: The date the expense was added.
    
    Returns:
    - str: Confirmation message of the added expense.
    """
    try:
        amount = float(amount)
    except ValueError:
        print("Please enter a valid number")
        return
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return
    db_execute(cursor, '''
    INSERT INTO expenses (category, amount, date)
    VALUES (?, ?, ?)
    ''', (category, amount, date))
    return f"Added expense: {category} - £{amount} on {date}"


def update_expense_amount_prompt(cursor):
    """
    Menu option to update an expense amount by either ID or category.

    Parameters:
    - cursor: The database cursor to execute the query.

    Returns:
    None
    """
    try:
        update_choice =\
        input('''Do you want to update by (1) Expense ID or (2) Category?
        Enter 1 or 2: ''')
        if update_choice == '1':
            expense_id = int(input("Pleae enter the Expense ID: "))
            new_amount = float(input("Please enter the new amount: "))
            update_expense_amount(cursor, expense_id, new_amount)

        elif update_choice == '2':
            category = input("Please enter the category name: ")
            new_amount = float(input("Please enter the new amount: "))
            update_expense_amount(cursor, category, new_amount)

        else:
            print("Please enter 1 or 2")
    except ValueError:
        print("Please enter a valid number")
        return
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return


def update_expense_amount(cursor, identifier, new_amount):
    """
    Updates the amount for a specific expense category.

    Parameters:
    - cursor: The database cursor to execute the query.
    - expense_id: The ID of the expense with the updated amount.
    - category: The category of the expense.

    Returns:
    - str: Confirmation of the updated expense.
    """
    try:
        if isinstance(identifier, int):
            db_execute("UPDATE expenses SET amount = ? WHERE id = ?",\
                (new_amount, identifier))
            if cursor.rowcount > 0:
                print(f"Expense ID {identifier} has been updated to\
                    {new_amount}")
            else:
                print(f"No expense found with ID {identifier}")
        else:
            db_execute("UPDATE expenses SET amount = ? WHERE category = ?",\
                (new_amount, identifier))
            if cursor.rowcount > 0:
                print(f"No expenses found in category '{identifier}'")
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return


# Generic category functions
def view_records_by_category(cursor, table, category):
    """
    Retrieves expenses by a specific category.
    
    Parameters:
    - cursor: The database cursor to execute the query.
    - table: The name of the table to retrieve records from.
    - category: The category name to filter expenses.
    
    Returns:
    - List of tuples containing expenses for the specified category.
    """
    try:
        records = db_execute(cursor, f'''SELECT * FROM {table} WHERE 
        category = ?''', (category,), fetch=True)
        
        if records:
            for record in records:
                print(record)
        else:
            print(f"No records found in category '{category}'")
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return


def delete_category(cursor, category, table):
    """
    Deletes a specified category from specified table.

    Parameters:
    - cursor: The database cursor to execute the query.
    - category: The category of the expense to delete.
    - table: The name of the table to retrieve records from.

    Returns:
    - str: Confirmation message of the deleted expense category.
    """
    try:
        db_execute(cursor, f"DELETE FROM {table} WHERE category = ?",\
            (category,))
        return f"Deleted category '{category}' from {table}"
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return


# Income functions
def add_income(cursor, category, amount, date):
    """
    Adds a new income entry to database.

    Parameters:
    - cursor: The database cursor to execute the query.
    - category: The category of the income.
    - amount: The amount of income.
    - date: The date the income was added.

    Returns:
    - str: Confirmation message of the added income.
    """
    try:
        db_execute(cursor, '''
        INSERT INTO income (category, amount, date)
        VALUES (?, ?, ?)
        ''', (category, amount, date))
        return f"Added income: {category} - £{amount} on {date}"
    except ValueError:
        print("Please enter a valid number")
        return
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return


# Budget functions
def set_budget(cursor, category, budget_limit):
    """
    Sets a budget limit for a specific category.

    Parameters:
    - cursor: The database cursor to execute the query.
    - category: The category for the budget.
    - budget: The budget limit.

    Returns:
    - str: Confirmation message of the set budget.
    """
    try:
        budget_limit = float(budget_limit)
        db_execute(cursor, '''
        INSERT OR REPLACE INTO budgets (category, budget_limit)
        VALUES (?, ?)
        ''', (category, budget_limit))
        return f"Set budget for {category} to £{budget_limit}"
    except ValueError:
        print("Please enter a valid number")
        return
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return


def view_budget(cursor, category):
    """
    Retrieves the budget for a specific category.

    Parameters:
    - cursor: The database cursor to execute the query.
    - category: The category for which to view the budget.

    Returns:
    - float or None: The budget amount or None if no budget is set.
    """
    try:
        budget = db_execute(cursor, 'SELECT budget_limit FROM budgets ORDER BY\
            id DESC LIMIT 1', fetch=True)
        if budget:
            print(f"Budget for category {category}: £{budget[0][0]}")
        else:
            print(f"No budget set for {category}")
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return


# Goal functions
def set_financial_goal(cursor, goal, target_amount):
    """
    Sets a financial goal with a description and target amount.

    Parameters:
    - cursor: The database cursor to execute the query.
    - goal: A brief description of the goal.
    - target_amount: The target amount for the goal.

    Returns:
    - str: Confirmation message of the set financial goal.
    """
    try:
        target_amount = float(target_amount)
        db_execute(cursor, '''
    INSERT INTO goals (goal, target_amount, progress)
    VALUES (?, ?, 0)
    ''', (goal, target_amount, 0))
    except ValueError:
        print("Please enter a valid number")
        return
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return
    return f"Set financial goal: {goal} - Target: £{target_amount}"


def view_financial_goals(cursor):
    """
    Retrieves and displays all financial goals and their progress.

    Parameters:
    - cursor: The database cursor to execute the query.

    Returns:
    - List of tuples containing goal information and progress.
    """
    try:
        goals = db_execute(cursor, 'SELECT * FROM goals', fetch=True)
        if goals:
            for goal in goals:
                return goal
        else:
            return "No financial goals set."
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return


def update_goal_progress(cursor, goal_id, progress):
    """
    Allows user to update a goal's progress.

    Parameters:
    - cursor: The database cursor to execute the query.
    - goal_id: The ID of the goal to update.
    - progress: The updated target amount for the goal.

    Returns:
    - str: Confirmation message of the updated progress.
    """
    try:
        progress = float(progress)
        db_execute(cursor, 'UPDATE goals SET progress = ? WHERE id = ?',\
            (progress, goal_id))
        return f"Updated progress for goal '{goal_id}' to £{progress}"
    except ValueError:
        print("Please enter a valid number")
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return


def delete_financial_goal(cursor, goal_id):
    """
    Deletes a specified financial goal from database.

    Parameters:
    - cursor: The database cursor to execute the query.
    - goal_id: The ID of the goal to delete.

    Returns:
    - str: Confirmation message of the deleted goal.
    """
    try:
        db_execute(cursor, "DELETE FROM goals WHERE goal = ?",\
            (goal_id,))
        return f"Deleted goal ID: '{goal_id}'"
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return


# Budget calculator
def calculate_budget(cursor):
    """
    Calculates the user's remaining budget based on total income and expenses.

    Parameters:
    - cursor: The database cursor to execute the query.

    Returns:
    - str: A summary of the user's budget, showing remaining balance or
    shortfall.
    """
    try:
        total_income = db_execute(cursor, "SELECT SUM(amount) * FROM income",\
            fetch=True)[0][0] or 0
        total_expenses = db_execute(cursor, "SELECT SUM(amount) * FROM\
            expenses", fetch=True)[0][0] or 0
        total_budget = total_income - total_expenses
        print(f"Your remaining budget is: {total_budget}")
        return total_budget
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return


# Main menu functions
def main_menu(cursor):
    """
    Displays the main menu and prompts the user to select an action.

    Parameters:
    - cursor: The database cursor to execute the query.

    Returns:
    - None
    """
    initialise_database(cursor)
    
    while True:
        print('''
        1. Add expense
        2. View expenses
        3. Update an expense amount
        4. View expenses by category
        5. Delete an expense category
        6. Add income
        7. View income
        8. View income by category
        9. Delete an income category
        10. Set budget for a category
        11. View budget for a category
        12. Set financal goals
        13. View progress towards financial goals
        14. Update goal progress
        15. Delete a financial goal
        16. Calculate budget
        17. Quit
        ''')

        choice = input("Pick an option (1-17): ")

        if choice == '1':
            category = input("Enter a new expense ID: ")
            amount = float(input("Enter an expense amount: "))
            date = input("Enter the date (DD-MM-YYYY): ")
            print(add_expense(cursor, category, amount, date))

        elif choice == '2':
            expenses = view_records(cursor, "expenses")
            for expense in expenses:
                print(expense)

        elif choice == '3':
            print(update_expense_amount_prompt(cursor))

        elif choice == '4':
            category = input("Enter a category to view expenses: ")
            expenses = (view_records_by_category(cursor, "expenses", category))

        elif choice == '5':
            category = input("Enter expense category to delete: ")
            print(delete_category(cursor, category, "expenses"))

        elif choice == '6':
            category = input("Enter an income category: ")
            amount = float(input("Enter an income amount: "))
            date = input("Enter the date (DD-MM-YYYY): ")
            print(add_income(cursor, category, amount, date))
        
        elif choice == '7':
            income = view_records(cursor, "income")
            for inc in income:
                print(inc)

        elif choice == '8':
            category = input("Enter category to filter income: ")
            income = view_records_by_category(cursor, "income", category)

        elif choice == '9':
            category = input("Enter income category to delete: ")
            print(delete_category(cursor, category, "income"))

        elif choice == '10':
            category = input("Enter a category to set budget: ")
            budget_limit = float(input("Enter budget amount: "))
            print(set_budget(cursor, category, budget_limit))

        elif choice == '11':
            category = input("Enter a category to view the budget: ")
            print(view_budget(cursor, category))

        elif choice == '12':
            description = input("Enter the goal description: ")
            target_amount = float(input("Enter the target amount: "))
            print(set_financial_goal(cursor, description, target_amount))

        elif choice == '13':
            goals = view_financial_goals(cursor)

        elif choice == '14':
            goal_id = id(input("Enter goal to update progress for: "))
            amount_saved = float(input("Enter amount saved: "))
            print(update_goal_progress(cursor, goal_id, amount_saved))

        elif choice == '15':
            goal = int(input("Enter goal ID to delete: "))
            print(delete_financial_goal(cursor, goal_id))

        elif choice == '16':
            remaining_budget = calculate_budget(cursor)
            print(f"Remaining budget: £{remaining_budget}")

        elif choice == '17':
            print("Have a nice day")
            break

        else:
            print("Invalid option, please try again")


def main():
    with sqlite3.connect('budget_tracker.db') as connect:
        cursor = connect.cursor()
        main_menu(cursor)

# Run the main menu
if __name__ == "__main__":
    main()