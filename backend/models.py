# -*- coding: utf-8 -*-
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()

class User(db.Model, UserMixin):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    total_points = db.Column(db.Integer, default=0)
    total_studied = db.Column(db.Integer, default=0)
    streak = db.Column(db.Integer, default=0)
    last_study_date = db.Column(db.String(20))
    unlocked_decks = db.Column(db.Integer, default=999)
    stars = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def get_id(self):
        return str(self.id)

class Deck(db.Model):
    __tablename__ = "decks"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    subject = db.Column(db.String(100))
    difficulty = db.Column(db.String(20))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    cards = db.relationship("Card", backref="deck", lazy=True, cascade="all, delete-orphan")

class Card(db.Model):
    __tablename__ = "cards"
    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.Text, nullable=False)
    answer = db.Column(db.Text, nullable=False)
    deck_id = db.Column(db.Integer, db.ForeignKey("decks.id"), nullable=False)
    algorithm = db.Column(db.String(10), default="SM2")
    last_review = db.Column(db.DateTime)
    next_review = db.Column(db.DateTime)
    review_count = db.Column(db.Integer, default=0)
    avg_time = db.Column(db.Float, default=0.0)
    is_mastered = db.Column(db.Boolean, default=False)
    e_factor = db.Column(db.Float, default=2.5)
    interval = db.Column(db.Integer, default=1)
    stability = db.Column(db.Float, default=2.0)
    difficulty = db.Column(db.Float, default=5.0)

class QuizResult(db.Model):
    __tablename__ = "quiz_results"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    deck_id = db.Column(db.Integer, db.ForeignKey("decks.id"), nullable=False)
    score = db.Column(db.Integer, default=0)
    total_questions = db.Column(db.Integer, default=0)
    percentage = db.Column(db.Float, default=0.0)
    time_taken = db.Column(db.Float, default=0.0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user = db.relationship("User", backref="quiz_results")
    deck = db.relationship("Deck", backref="quiz_results")

class LearningProgress(db.Model):
    __tablename__ = "learning_progress"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    deck_id = db.Column(db.Integer, db.ForeignKey("decks.id"), nullable=False)
    completed = db.Column(db.Boolean, default=False)
    last_accessed = db.Column(db.DateTime, default=datetime.utcnow)
    progress_percent = db.Column(db.Float, default=0.0)
    user = db.relationship("User", backref="learning_progress")
    deck = db.relationship("Deck", backref="learning_progress")

class CardReview(db.Model):
    __tablename__ = "card_reviews"
    id = db.Column(db.Integer, primary_key=True)
    card_id = db.Column(db.Integer, db.ForeignKey("cards.id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    response_time = db.Column(db.Float, default=0.0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    card = db.relationship("Card", backref="reviews")
    user = db.relationship("User", backref="card_reviews")
    
    @property
    def is_correct(self):
        return self.rating >= 3
    
    @property
    def rating_text(self):
        return {1: "Again", 2: "Hard", 3: "Good", 4: "Easy"}.get(self.rating, "Unknown")

# ============================================================
# COMPLETE 20 DECKS WITH 25 UNIQUE QUESTIONS EACH = 500 CARDS
# ============================================================

def create_decks_for_new_user(user_id):
    """Create 20 decks with 25 UNIQUE questions each - 500 total different questions"""
    
    # DECK 1: Python Basics (25 unique questions)
    deck1 = [
        ("1. What is Python?", "A high-level, interpreted programming language created by Guido van Rossum."),
        ("2. Who created Python?", "Guido van Rossum"),
        ("3. When was Python created?", "1991"),
        ("4. What is PEP 8?", "Python's style guide for writing clean, readable code"),
        ("5. Is Python compiled or interpreted?", "Interpreted (though it compiles to bytecode)"),
        ("6. What are the key features of Python?", "Simple, readable, interpreted, object-oriented, dynamic typing"),
        ("7. What is dynamic typing?", "Variables can change type at runtime"),
        ("8. Is Python case-sensitive?", "Yes, 'Variable' and 'variable' are different"),
        ("9. What is indentation used for?", "Defines code blocks instead of braces"),
        ("10. What is a comment in Python?", "Text ignored by interpreter, starts with #"),
        ("11. How to write multi-line comments?", "Using triple quotes ''' or \"\"\""),
        ("12. What is the Zen of Python?", "Collection of 19 guiding principles for Python design"),
        ("13. How to import modules?", "Using 'import module_name'"),
        ("14. What is PIP?", "Package installer for Python"),
        ("15. How to install a package?", "pip install package_name"),
        ("16. What is a virtual environment?", "Isolated Python environment for projects"),
        ("17. How to create a virtual environment?", "python -m venv env_name"),
        ("18. What is PyPI?", "Python Package Index - repository of Python packages"),
        ("19. What is Anaconda?", "Python distribution for data science and machine learning"),
        ("20. What is a statement?", "A single line of code that performs an action"),
        ("21. What is an expression?", "Code that produces a value"),
        ("22. What is IDLE?", "Python's Integrated Development and Learning Environment"),
        ("23. What is the correct file extension for Python?", ".py"),
        ("24. How to check Python version?", "python --version or import sys; print(sys.version)"),
        ("25. Difference between Python 2 and 3?", "Python 3 has better Unicode support, print is function, improved syntax")
    ]
    
    # DECK 2: Variables & Data Types (25 unique questions)
    deck2 = [
        ("1. What is a variable?", "Container for storing data values"),
        ("2. How to create a variable?", "variable_name = value"),
        ("3. Rules for variable names?", "Start with letter/_, no spaces, case-sensitive"),
        ("4. What is dynamic typing?", "Variables can change type during execution"),
        ("5. What is type() function?", "Returns the type of an object"),
        ("6. Basic data types?", "int, float, str, bool, list, tuple, dict, set"),
        ("7. What is an integer?", "Whole numbers without decimal point"),
        ("8. What is a float?", "Numbers with decimal points"),
        ("9. What is a string?", "Sequence of characters in quotes"),
        ("10. What is a boolean?", "True or False values"),
        ("11. What is None?", "Represents absence of value"),
        ("12. How to check variable type?", "isinstance() or type() function"),
        ("13. What is type conversion?", "Converting one data type to another"),
        ("14. How to convert string to int?", "int('123')"),
        ("15. How to convert int to string?", "str(123)"),
        ("16. What is implicit conversion?", "Automatic type conversion by Python"),
        ("17. What is explicit conversion?", "Manual type conversion using functions"),
        ("18. What is a constant?", "Variable that shouldn't change (convention: UPPER_CASE)"),
        ("19. How to delete a variable?", "del variable_name"),
        ("20. What is variable scope?", "Where a variable is accessible (local vs global)"),
        ("21. What is a global variable?", "Variable defined outside functions"),
        ("22. What is a local variable?", "Variable defined inside a function"),
        ("23. How to modify global variable?", "Use 'global' keyword"),
        ("24. What is multiple assignment?", "Assign multiple variables: a, b = 1, 2"),
        ("25. What is variable swapping?", "Exchange values: a, b = b, a")
    ]
    
    # DECK 3: Lists (25 unique questions)
    deck3 = [
        ("1. What is a list?", "Ordered, mutable collection of items"),
        ("2. How to create a list?", "my_list = [1, 2, 3] or list()"),
        ("3. How to access list elements?", "Using index: my_list[0]"),
        ("4. What is negative indexing?", "Access from end: my_list[-1] is last element"),
        ("5. How to slice a list?", "my_list[start:end:step]"),
        ("6. How to add item to end?", "append() method"),
        ("7. How to insert at position?", "insert(index, item) method"),
        ("8. How to add multiple items?", "extend() method or + operator"),
        ("9. How to remove by value?", "remove() method"),
        ("10. How to remove by index?", "pop() method or del statement"),
        ("11. How to clear all items?", "clear() method"),
        ("12. What is list comprehension?", "Concise creation: [x**2 for x in range(10)]"),
        ("13. How to sort a list?", "sort() method or sorted() function"),
        ("14. How to reverse a list?", "reverse() method or [::-1]"),
        ("15. How to check if item exists?", "'item' in list"),
        ("16. How to get list length?", "len(list)"),
        ("17. What is list unpacking?", "Assign elements: a, b = [1, 2]"),
        ("18. What is nested list?", "List containing other lists"),
        ("19. How to copy a list?", "copy() method or list[:]"),
        ("20. Shallow vs deep copy?", "Shallow copies references, deep copies objects"),
        ("21. How to count occurrences?", "count() method"),
        ("22. How to find index?", "index() method"),
        ("23. How to loop through list?", "for item in list:"),
        ("24. What is enumerate()?", "Returns index and value during iteration"),
        ("25. What is zip() with lists?", "Combines multiple lists element-wise")
    ]
    
    # DECK 4: Tuples (25 unique questions)
    deck4 = [
        ("1. What is a tuple?", "Ordered, immutable collection"),
        ("2. How to create a tuple?", "my_tuple = (1, 2, 3) or tuple()"),
        ("3. Single-element tuple syntax?", "(1,) - comma is required"),
        ("4. Why use tuples over lists?", "Immutable, faster, memory efficient, hashable"),
        ("5. Can you modify a tuple?", "No, it's immutable"),
        ("6. What is tuple unpacking?", "Assign tuple elements to variables"),
        ("7. How to access tuple elements?", "Using index: my_tuple[0]"),
        ("8. What is tuple slicing?", "my_tuple[start:end:step]"),
        ("9. How to check if item exists?", "'item' in tuple"),
        ("10. What is tuple concatenation?", "Join tuples with + operator"),
        ("11. What is tuple repetition?", "my_tuple * 3"),
        ("12. How to get tuple length?", "len(tuple)"),
        ("13. What are tuple methods?", "count() and index() only"),
        ("14. Can tuple contain mutable objects?", "Yes, but tuple itself immutable"),
        ("15. What is namedtuple?", "Tuple subclass with named fields"),
        ("16. When to use tuple vs list?", "Tuple for fixed data, list for changing"),
        ("17. What is tuple packing?", "Creating tuple: a = 1, 2, 3"),
        ("18. How to convert list to tuple?", "tuple(list)"),
        ("19. How to convert tuple to list?", "list(tuple)"),
        ("20. Are tuples hashable?", "Yes, if all elements hashable"),
        ("21. Can tuple be dictionary key?", "Yes, unlike lists"),
        ("22. Performance difference?", "Tuples slightly faster than lists"),
        ("23. Memory difference?", "Tuples use less memory than lists"),
        ("24. How to sort a tuple?", "Convert to list, sort, convert back"),
        ("25. Empty tuple use?", "Placeholder or representing no data")
    ]
    
    # DECK 5: Dictionaries (25 unique questions)
    deck5 = [
        ("1. What is a dictionary?", "Key-value pair collection"),
        ("2. How to create a dictionary?", "my_dict = {'key': 'value'} or dict()"),
        ("3. How to access values?", "my_dict['key'] or get() method"),
        ("4. How to add/update items?", "my_dict['new_key'] = value"),
        ("5. How to remove items?", "pop(), popitem(), del, clear()"),
        ("6. What can be dictionary keys?", "Immutable types (strings, numbers, tuples)"),
        ("7. What can be dictionary values?", "Any type, can be duplicate"),
        ("8. How to get all keys?", "keys() method"),
        ("9. How to get all values?", "values() method"),
        ("10. How to get all items?", "items() method"),
        ("11. How to check if key exists?", "'key' in dictionary"),
        ("12. What is dictionary comprehension?", "{key: value for item in iterable}"),
        ("13. How to merge dictionaries?", "update() method or | operator"),
        ("14. What is get() method?", "Returns value or default if key missing"),
        ("15. What is setdefault()?", "Returns value, inserts if key missing"),
        ("16. What is defaultdict?", "Dict with default value from collections"),
        ("17. What is OrderedDict?", "Dict that remembers insertion order"),
        ("18. How to loop through dictionary?", "for key, value in dict.items()"),
        ("19. Dict vs list difference?", "Dict uses keys, list uses indices"),
        ("20. What is dictionary view?", "Dynamic views of dictionary items"),
        ("21. How to copy a dictionary?", "copy() method or dict() constructor"),
        ("22. Deep copy for dict?", "import copy; copy.deepcopy(dict)"),
        ("23. Time complexity?", "Average O(1) for get/set, O(n) worst"),
        ("24. Can dictionary have duplicate keys?", "No, each key is unique"),
        ("25. JSON and dict relationship?", "JSON objects are similar to Python dicts")
    ]
    
    # DECK 6: Sets (25 unique questions)
    deck6 = [
        ("1. What is a set?", "Unordered collection of unique items"),
        ("2. How to create a set?", "my_set = {1, 2, 3} or set()"),
        ("3. Set vs list difference?", "Sets have unique items, unordered, faster membership"),
        ("4. How to add item?", "add() method"),
        ("5. How to remove item?", "remove(), discard(), pop(), clear()"),
        ("6. What is set union?", "set1 | set2 or union()"),
        ("7. What is set intersection?", "set1 & set2 or intersection()"),
        ("8. What is set difference?", "set1 - set2"),
        ("9. What is symmetric difference?", "set1 ^ set2"),
        ("10. How to check subset?", "set1.issubset(set2) or set1 <= set2"),
        ("11. How to check superset?", "set1.issuperset(set2) or set1 >= set2"),
        ("12. What is frozenset?", "Immutable version of set"),
        ("13. What is set comprehension?", "{x**2 for x in range(10)}"),
        ("14. How to remove duplicates from list?", "list(set(my_list))"),
        ("15. Membership test speed?", "Sets have O(1) membership test"),
        ("16. How to loop through set?", "for item in my_set"),
        ("17. remove() vs discard()?", "remove() raises error if missing, discard() doesn't"),
        ("18. Can set contain mutable items?", "No, only hashable items"),
        ("19. How to get set length?", "len(set)"),
        ("20. What is isdisjoint()?", "Checks if sets have no common elements"),
        ("21. What is update()?", "Adds multiple elements from iterable"),
        ("22. What is intersection_update()?", "Keeps only common elements"),
        ("23. What is difference_update()?", "Removes elements found in other set"),
        ("24. When to use set?", "When you need unique items and fast membership"),
        ("25. What is hashing in sets?", "Sets use hash tables for O(1) operations")
    ]
    
    # DECK 7: Strings (25 unique questions)
    deck7 = [
        ("1. What is a string?", "Sequence of characters"),
        ("2. How to create strings?", "Single '', double \"\", triple '''\"\"\"'''"),
        ("3. What is string concatenation?", "Joining strings with + operator"),
        ("4. What is string repetition?", "Repeat with * operator: 'Hi' * 3 = 'HiHiHi'"),
        ("5. What is string slicing?", "Extract substring: text[2:5]"),
        ("6. What is negative indexing?", "Access from end: text[-1] last character"),
        ("7. What is len() for strings?", "Returns number of characters"),
        ("8. What are f-strings?", "Formatted strings: f'Hello {name}'"),
        ("9. What is format() method?", "String formatting: 'Hello {}'.format(name)"),
        ("10. What is upper()?", "Converts string to uppercase"),
        ("11. What is lower()?", "Converts string to lowercase"),
        ("12. What is strip()?", "Removes whitespace from ends"),
        ("13. What is split()?", "Splits string into list"),
        ("14. What is join()?", "Joins list into string: '-'.join(['a','b','c'])"),
        ("15. What is replace()?", "Replaces substring"),
        ("16. What is find()?", "Finds substring index, -1 if not found"),
        ("17. What is count()?", "Counts occurrences of substring"),
        ("18. What is startswith()?", "Checks if string starts with substring"),
        ("19. What is endswith()?", "Checks if string ends with substring"),
        ("20. What is isdigit()?", "Checks if all characters are digits"),
        ("21. What is isalpha()?", "Checks if all characters are alphabetic"),
        ("22. What is isalnum()?", "Checks if alphanumeric"),
        ("23. What are escape characters?", "\\n new line, \\t tab, \\\\ backslash"),
        ("24. What is raw string?", "r'text' ignores escape characters"),
        ("25. What is string immutability?", "Strings cannot be changed, new strings created")
    ]
    
    # DECK 8: Control Flow (25 unique questions)
    deck8 = [
        ("1. What is an if statement?", "Executes code block when condition is True"),
        ("2. What is an else statement?", "Executes when if condition is False"),
        ("3. What is an elif statement?", "Checks another condition when previous False"),
        ("4. If-elif-else syntax?", "if condition1: ... elif condition2: ... else: ..."),
        ("5. Can you nest if statements?", "Yes, if statements can be nested"),
        ("6. What is ternary operator?", "x if condition else y - one-line conditional"),
        ("7. Difference between = and ==?", "= assignment, == comparison"),
        ("8. What is the not operator?", "Reverses boolean: not True = False"),
        ("9. What is the and operator?", "True only if both conditions True"),
        ("10. What is the or operator?", "True if at least one condition True"),
        ("11. What is short-circuit evaluation?", "Stops evaluating once result determined"),
        ("12. What is pass statement?", "Does nothing, used as placeholder"),
        ("13. is vs == difference?", "is checks identity, == checks equality"),
        ("14. What are truthy and falsy?", "Values evaluating to True/False in boolean context"),
        ("15. Falsy values in Python?", "None, False, 0, '', [], {}, set(), range(0)"),
        ("16. What is bool() function?", "Converts value to boolean (True/False)"),
        ("17. How to check if variable exists?", "if 'var' in locals() or in globals()"),
        ("18. What is match statement?", "Python 3.10+ pattern matching (like switch-case)"),
        ("19. if vs elif difference?", "elif only checked if previous conditions False"),
        ("20. Multiple elif statements?", "Yes, as many as needed"),
        ("21. Else clause in loops?", "Executes when loop completes without break"),
        ("22. What is walrus operator (:=)?", "Assignment expression: if (n := len(x)) > 10:"),
        ("23. break vs continue?", "break exits loop, continue skips to next iteration"),
        ("24. What is conditional expression?", "Another name for ternary operator"),
        ("25. Multiple conditions writing?", "Use and/or or chain: 1 < x < 10")
    ]
    
    # DECK 9: Loops (25 unique questions)
    deck9 = [
        ("1. What is a for loop?", "Iterates over a sequence"),
        ("2. What is a while loop?", "Repeats while condition is True"),
        ("3. What is range() function?", "Generates number sequence: range(5) = 0,1,2,3,4"),
        ("4. How to loop with index?", "for i, item in enumerate(list)"),
        ("5. What is break?", "Exits the current loop immediately"),
        ("6. What is continue?", "Skips to next iteration of the loop"),
        ("7. Else clause in loops?", "Executes if loop completes without break"),
        ("8. What is infinite loop?", "Loop that never ends (while True)"),
        ("9. Iterate over dictionary?", "for key, value in dict.items()"),
        ("10. What is nested loop?", "Loop inside another loop"),
        ("11. Loop efficiency?", "O(n) single, O(n�) nested"),
        ("12. How to use enumerate()?", "for index, value in enumerate(list, start=1)"),
        ("13. What is zip() in loops?", "Iterates over multiple sequences in parallel"),
        ("14. How to loop backwards?", "for i in range(len(list)-1, -1, -1) or reversed()"),
        ("15. List comprehension vs loop?", "Comprehension more concise and often faster"),
        ("16. What is while else?", "else executes when condition becomes False (not break)"),
        ("17. Loop through files?", "for line in file: process line"),
        ("18. for vs while difference?", "for for known iterations, while for unknown"),
        ("19. Break out of nested loops?", "Use flags, functions, or for-else with break"),
        ("20. Performance of for vs while?", "for generally faster and more Pythonic"),
        ("21. Skip first N items?", "for item in list[N:]: or use itertools.islice"),
        ("22. What is itertools module?", "Provides efficient looping tools"),
        ("23. Simple counter creation?", "count = 0; while count < 10: count += 1"),
        ("24. Time complexity of loops?", "O(n) linear, O(n�) nested, O(log n) binary search"),
        ("25. Loop with step size?", "for i in range(start, end, step)")
    ]
    
    # DECK 10: Functions (25 unique questions)
    deck10 = [
        ("1. What is a function?", "Reusable block of code for specific task"),
        ("2. How to define a function?", "def function_name(parameters):"),
        ("3. What is a parameter?", "Variable in function definition"),
        ("4. What is an argument?", "Value passed to function when called"),
        ("5. What is return statement?", "Returns value, ends function execution"),
        ("6. What is default parameter?", "Parameter with default: def func(x=5)"),
        ("7. What is keyword argument?", "Passing by name: func(x=5, y=10)"),
        ("8. What is *args?", "Variable number of positional arguments"),
        ("9. What is **kwargs?", "Variable number of keyword arguments"),
        ("10. What is lambda?", "Anonymous one-line function: lambda x: x*2"),
        ("11. What is function scope?", "Variables inside function are local"),
        ("12. What is a docstring?", "Documentation string after function definition"),
        ("13. What is recursion?", "Function that calls itself"),
        ("14. return vs print?", "return gives value, print displays"),
        ("15. Function overloading?", "Python doesn't support traditional overloading"),
        ("16. What is a closure?", "Function remembering outer scope variables"),
        ("17. What is a decorator?", "Function that modifies another function"),
        ("18. What is generator function?", "Uses yield to produce sequence"),
        ("19. What is pure function?", "Same output for same input, no side effects"),
        ("20. Maximum recursion depth?", "Default 1000, change with sys.setrecursionlimit()"),
        ("21. What is nested function?", "Function defined inside another function"),
        ("22. What is global keyword?", "Access/modify global variable inside function"),
        ("23. What is nonlocal keyword?", "Modify variable in nested function's outer scope"),
        ("24. What is function annotation?", "Type hints: def func(x: int) -> str:"),
        ("25. Local vs global scope?", "Local inside function, global throughout module")
    ]
    
    # DECK 11: Exception Handling (25 unique questions)
    deck11 = [
        ("1. What is an exception?", "Error during program execution"),
        ("2. What is try block?", "Contains code that might raise exception"),
        ("3. What is except block?", "Handles specific exception"),
        ("4. What is finally block?", "Always executes (cleanup code)"),
        ("5. What is else block in try?", "Executes if no exception occurred"),
        ("6. What is raise statement?", "Manually triggers an exception"),
        ("7. Built-in exceptions?", "TypeError, ValueError, IndexError, KeyError"),
        ("8. except vs except Exception as e?", "except catches all, except Exception catches most"),
        ("9. Catch multiple exceptions?", "except (TypeError, ValueError):"),
        ("10. Exception hierarchy?", "BaseException -> Exception -> specific"),
        ("11. What is custom exception?", "User-defined class inheriting from Exception"),
        ("12. Purpose of finally?", "Cleanup resources (file close, db connection)"),
        ("13. try-finally vs try-except?", "finally always runs, except only on error"),
        ("14. Else clause purpose?", "Code that runs only if no error occurs"),
        ("15. Get exception message?", "except Exception as e: print(e)"),
        ("16. What is traceback?", "Information about where exception occurred"),
        ("17. Ignore exception?", "Use except: pass (not recommended)"),
        ("18. Best practice for exception handling?", "Be specific, don't catch everything"),
        ("19. Error vs exception?", "Error unrecoverable, exception can be handled"),
        ("20. What is RuntimeError?", "General error not fitting other categories"),
        ("21. What is ZeroDivisionError?", "Division by zero"),
        ("22. What is FileNotFoundError?", "File doesn't exist"),
        ("23. What is ImportError?", "Module not found"),
        ("24. How to reraise exception?", "raise inside except block"),
        ("25. Cost of try-except?", "Exception handling has overhead")
    ]
    
    # DECK 12: File I/O (25 unique questions)
    deck12 = [
        ("1. What is file handling?", "Reading from and writing to files"),
        ("2. How to open a file?", "open('filename.txt', 'mode')"),
        ("3. File modes?", "r read, w write, a append, x create, b binary"),
        ("4. What is with statement?", "Context manager that auto-closes file"),
        ("5. How to read entire file?", "file.read()"),
        ("6. Read line by line?", "for line in file:"),
        ("7. Read all lines to list?", "file.readlines()"),
        ("8. How to write to file?", "file.write('text')"),
        ("9. Write multiple lines?", "file.writelines(list_of_lines)"),
        ("10. r+ vs w+?", "r+ read/write no truncate, w+ read/write truncate"),
        ("11. What is seek()?", "Moves file cursor to specific position"),
        ("12. What is tell()?", "Returns current cursor position"),
        ("13. Check if file exists?", "import os; os.path.exists(filename)"),
        ("14. read() vs readline()?", "read() all content, readline() one line"),
        ("15. Handle large files?", "Read in chunks or iterate line by line"),
        ("16. What is binary file?", "Non-text data (images, executables)"),
        ("17. Read binary file?", "open('file.bin', 'rb')"),
        ("18. Text vs binary mode?", "Text handles encoding, binary reads raw bytes"),
        ("19. Copy a file?", "shutil.copy(src, dst)"),
        ("20. What is file pointer?", "Current position in file"),
        ("21. Delete a file?", "os.remove(filename)"),
        ("22. Rename a file?", "os.rename(old, new)"),
        ("23. What is a directory?", "Folder containing files"),
        ("24. List directory contents?", "os.listdir(path) or glob.glob('*.txt')"),
        ("25. Create directory?", "os.mkdir(dirname) or os.makedirs(path)")
    ]
    
    # DECK 13: OOP - Classes (25 unique questions)
    deck13 = [
        ("1. What is a class?", "Blueprint for creating objects"),
        ("2. What is an object?", "Instance of a class"),
        ("3. What is __init__?", "Constructor called when object created"),
        ("4. What is self?", "Reference to current instance"),
        ("5. What are instance variables?", "Variables unique to each instance"),
        ("6. What are class variables?", "Variables shared across instances"),
        ("7. What is a method?", "Function defined inside class"),
        ("8. What is encapsulation?", "Bundling data and methods, hiding internal state"),
        ("9. What is abstraction?", "Hiding implementation details"),
        ("10. Class vs instance methods?", "Class uses @classmethod, instance uses self"),
        ("11. What is static method?", "Method without instance or class (@staticmethod)"),
        ("12. What is property decorator?", "@property makes method accessible as attribute"),
        ("13. __str__ vs __repr__?", "__str__ for users, __repr__ for developers"),
        ("14. What are magic methods?", "Special methods like __add__, __len__, __getitem__"),
        ("15. What is composition?", "Class contains instances of other classes"),
        ("16. What is aggregation?", "Weak form of composition"),
        ("17. Public vs private in Python?", "Uses naming convention _ and __"),
        ("18. What is name mangling?", "Python renames __var to _class__var"),
        ("19. What is hasattr()?", "Check if object has attribute"),
        ("20. What is getattr()?", "Get attribute value by name"),
        ("21. What is setattr()?", "Set attribute value by name"),
        ("22. What is delattr()?", "Delete attribute by name"),
        ("23. What is issubclass()?", "Checks if class is subclass of another"),
        ("24. What is isinstance()?", "Checks if object is instance of class"),
        ("25. What is a metaclass?", "Class of a class (type is default metaclass)")
    ]
    
    # DECK 14: Inheritance (25 unique questions)
    deck14 = [
        ("1. What is inheritance?", "Child class inherits from parent"),
        ("2. What is single inheritance?", "One parent class"),
        ("3. What is multiple inheritance?", "Multiple parent classes"),
        ("4. What is multilevel inheritance?", "Child of another child"),
        ("5. What is hierarchical inheritance?", "Multiple children from one parent"),
        ("6. What is hybrid inheritance?", "Combination of multiple and multilevel"),
        ("7. What is method overriding?", "Child redefines parent method"),
        ("8. What is super()?", "Calls parent class method"),
        ("9. What is MRO?", "Method Resolution Order for inheritance"),
        ("10. How to check MRO?", "ClassName.__mro__ or ClassName.mro()"),
        ("11. What is diamond problem?", "Ambiguity in multiple inheritance"),
        ("12. Python's diamond solution?", "Uses C3 linearization algorithm"),
        ("13. What is abstract base class?", "Cannot be instantiated, has abstract methods"),
        ("14. What is ABC module?", "Provides ABC class and abstractmethod"),
        ("15. What is @abstractmethod?", "Method that must be implemented by subclasses"),
        ("16. What is mixin?", "Class providing methods via inheritance"),
        ("17. Interfaces in Python?", "No interfaces, use ABC instead"),
        ("18. Composition vs inheritance?", "Prefer composition (has-a) over inheritance"),
        ("19. isinstance() vs issubclass()?", "isinstance checks object, issubclass checks class"),
        ("20. What is method chaining?", "Returning self to chain method calls"),
        ("21. What is factory method?", "Method creating and returning objects"),
        ("22. What is abstract method?", "Method declared but not implemented"),
        ("23. What is concrete method?", "Method with full implementation"),
        ("24. What is virtual inheritance?", "Ensures single base class copy"),
        ("25. What is base class?", "Parent class that is inherited from")
    ]
    
    # DECK 15: Modules & Packages (25 unique questions)
    deck15 = [
        ("1. What is a module?", "Python file with functions and classes"),
        ("2. How to import module?", "import module_name"),
        ("3. Import specific function?", "from module import function"),
        ("4. What is __name__?", "'__main__' when script run directly"),
        ("5. What is a package?", "Directory with modules and __init__.py"),
        ("6. What is __init__.py?", "Marks directory as Python package"),
        ("7. What is relative import?", "from . import module"),
        ("8. What is absolute import?", "import package.module"),
        ("9. What is sys.path?", "Directories Python searches for modules"),
        ("10. How to reload module?", "import importlib; importlib.reload(module)"),
        ("11. import module vs from module import *?", "import keeps namespace, * pollutes"),
        ("12. What is __all__?", "Symbols exported by from module import *"),
        ("13. What is namespace package?", "Package spanning multiple directories"),
        ("14. How to create a module?", "Save Python code in .py file"),
        ("15. Module vs package?", "Module single file, package directory"),
        ("16. What is standard library?", "Built-in modules with Python"),
        ("17. What is pip?", "Package installer for Python"),
        ("18. Install third-party package?", "pip install package_name"),
        ("19. What is virtual environment?", "Isolated Python environment"),
        ("20. Create virtual environment?", "python -m venv env_name"),
        ("21. What is requirements.txt?", "Lists project dependencies"),
        ("22. Generate requirements.txt?", "pip freeze > requirements.txt"),
        ("23. Local vs global packages?", "Local: project-specific, Global: system-wide"),
        ("24. What is site-packages?", "Location where packages installed"),
        ("25. Check installed packages?", "pip list")
    ]
    
    # DECK 16: Comprehensions (25 unique questions)
    deck16 = [
        ("1. What is list comprehension?", "[x for x in iterable]"),
        ("2. List comprehension syntax?", "[expression for item in iterable if condition]"),
        ("3. Create list of squares?", "[x**2 for x in range(10)]"),
        ("4. Filter with comprehension?", "[x for x in range(10) if x % 2 == 0]"),
        ("5. What is nested comprehension?", "[[j for j in range(3)] for i in range(3)]"),
        ("6. Flatten a list?", "[item for sublist in list_of_lists for item in sublist]"),
        ("7. What is dict comprehension?", "{key: value for item in iterable}"),
        ("8. What is set comprehension?", "{x**2 for x in range(10)}"),
        ("9. What is generator expression?", "(x**2 for x in range(10)) - memory efficient"),
        ("10. List comprehension vs map()?", "Comprehension more Pythonic and faster"),
        ("11. If-else in comprehension?", "[x if x > 0 else 0 for x in numbers]"),
        ("12. Performance benefit?", "Faster than traditional loops"),
        ("13. Create matrix?", "[[0 for i in range(5)] for j in range(5)]"),
        ("14. Nested if in comprehension?", "[x for x in range(50) if x > 10 if x < 40]"),
        ("15. List of tuples?", "[(x, x**2) for x in range(10)]"),
        ("16. Memory advantage?", "List comprehension creates list in memory"),
        ("17. Transpose matrix?", "[[row[i] for row in matrix] for i in range(len(matrix[0]))]"),
        ("18. Comprehension vs loop?", "Comprehension expression, loop statement"),
        ("19. Comprehension with zip()?", "[a + b for a, b in zip(list1, list2)]"),
        ("20. Conditional expression?", "['even' if x%2==0 else 'odd' for x in range(10)]"),
        ("21. Dict from two lists?", "{k: v for k, v in zip(keys, values)}"),
        ("22. Time complexity?", "Same as equivalent loop O(n)"),
        ("23. Count values with comprehension?", "sum(1 for x in list if condition)"),
        ("24. Maximum nesting level?", "No limit, keep readable"),
        ("25. Debug comprehension?", "Convert to regular loop for debugging")
    ]
    
    # DECK 17: Lambda Functions (25 unique questions)
    deck17 = [
        ("1. What is lambda?", "Anonymous inline function"),
        ("2. Lambda syntax?", "lambda arguments: expression"),
        ("3. Lambda vs def?", "Lambda single expression, def multiple statements"),
        ("4. Lambda with map()?", "map(lambda x: x*2, list)"),
        ("5. Lambda with filter()?", "filter(lambda x: x > 5, list)"),
        ("6. Lambda with sorted()?", "sorted(list, key=lambda x: x[1])"),
        ("7. Multiple arguments?", "lambda x, y: x + y"),
        ("8. Lambda limitations?", "No statements, no annotations"),
        ("9. When to use lambda?", "Simple operations with map/filter/sorted"),
        ("10. Closure with lambda?", "Lambda capturing outer scope variables"),
        ("11. Immediate lambda?", "(lambda x: x*2)(5)"),
        ("12. Lambda performance?", "Similar to regular functions"),
        ("13. Recursive lambda?", "No, can't call itself by name"),
        ("14. Lambda with reduce()?", "from functools import reduce; reduce(lambda x,y: x+y, list)"),
        ("15. Ternary in lambda?", "lambda x: 'even' if x%2==0 else 'odd'"),
        ("16. Default arguments in lambda?", "Yes: lambda x, y=10: x+y"),
        ("17. Store lambda in variable?", "double = lambda x: x*2"),
        ("18. Lambda scope?", "Same as regular function"),
        ("19. Lambda with key functions?", "max(list, key=lambda x: x[1])"),
        ("20. Lambda vs partial?", "Partial fixes arguments, lambda creates new"),
        ("21. Lambda in list comprehension?", "[lambda x: x*2 for i in range(5)]"),
        ("22. Function composition?", "compose = lambda f, g: lambda x: f(g(x))"),
        ("23. Debug lambda?", "Convert to def function"),
        ("24. Lambda in GUI?", "Callback functions"),
        ("25. Is lambda Pythonic?", "For simple operations only")
    ]
    
    # DECK 18: Decorators (25 unique questions)
    deck18 = [
        ("1. What is a decorator?", "Function that modifies another function"),
        ("2. Decorator syntax?", "@decorator_name above function definition"),
        ("3. Simple decorator?", "def decorator(func): def wrapper(): ... return wrapper"),
        ("4. What is wrapper function?", "Inner function that adds functionality"),
        ("5. What is @ symbol?", "Syntactic sugar for applying decorator"),
        ("6. *args and **kwargs?", "Allow decorator to work with any function"),
        ("7. Decorator with arguments?", "Decorator that takes parameters"),
        ("8. @staticmethod vs @classmethod?", "Static: no self/cls, Class: receives class"),
        ("9. What is @property?", "Makes method accessible as attribute"),
        ("10. What is @cached_property?", "Caches result of property"),
        ("11. What is @lru_cache?", "Caches function results by arguments"),
        ("12. Preserve function metadata?", "@functools.wraps(func)"),
        ("13. What is nested decorator?", "Multiple decorators: @dec1 @dec2"),
        ("14. Order of decorators?", "Bottom to top (dec2 runs first)"),
        ("15. What is class decorator?", "Decorator applied to class"),
        ("16. Decorator vs inheritance?", "Decorator dynamic, inheritance static"),
        ("17. Debug decorator?", "Print inside wrapper function"),
        ("18. What is decorator factory?", "Function returning decorator (for arguments)"),
        ("19. Performance cost?", "Minor overhead of function call"),
        ("20. Logging decorator?", "Log function calls and arguments"),
        ("21. Timing decorator?", "Measures execution time"),
        ("22. Authentication decorator?", "Check permissions before executing"),
        ("23. Retry decorator?", "Retries function on failure"),
        ("24. Memoization decorator?", "Caches function results"),
        ("25. Decorators in Flask?", "@app.route, @login_required")
    ]
    
    # DECK 19: Generators (25 unique questions)
    deck19 = [
        ("1. What is a generator?", "Function producing sequence using yield"),
        ("2. What is yield keyword?", "Pauses function and returns value"),
        ("3. yield vs return?", "return ends, yield pauses"),
        ("4. Generator expression?", "(x**2 for x in range(10)) - lazy"),
        ("5. Advantage of generators?", "Memory efficient for large sequences"),
        ("6. Iterate over generator?", "for item in generator:"),
        ("7. What is next() function?", "Gets next value from generator"),
        ("8. What is StopIteration?", "Exception when generator exhausted"),
        ("9. What is send() method?", "Sends value to generator and continues"),
        ("10. What is throw() method?", "Throws exception inside generator"),
        ("11. What is close() method?", "Closes generator"),
        ("12. Generator vs list?", "Generator on-demand, list stores all"),
        ("13. Memory advantage?", "Generator O(1) memory, list O(n)"),
        ("14. Can generator be reused?", "No, exhausted after iteration"),
        ("15. Infinite generator?", "while True: yield value"),
        ("16. What is yield from?", "Delegates to another generator"),
        ("17. Uses of generators?", "Processing large files, infinite sequences"),
        ("18. Performance comparison?", "Generator faster for large datasets"),
        ("19. Convert generator to list?", "list(generator)"),
        ("20. Iterator vs generator?", "Generator is a type of iterator"),
        ("21. Pipelining with generators?", "Chaining generators for data processing"),
        ("22. Detect generator function?", "inspect.isgeneratorfunction(func)"),
        ("23. Generator in file reading?", "Read line by line without loading entire file"),
        ("24. Recursion depth?", "Limited by stack depth"),
        ("25. Debug generator?", "Use print or yield with debug flag")
    ]
    
    # DECK 20: Advanced Topics (25 unique questions)
    deck20 = [
        ("1. What is SQLite?", "Lightweight embedded SQL database"),
        ("2. Connect to SQLite?", "import sqlite3; conn = sqlite3.connect('db.db')"),
        ("3. What is a cursor?", "Object to execute SQL commands"),
        ("4. Create table?", "cursor.execute('CREATE TABLE ...')"),
        ("5. Insert data?", "cursor.execute('INSERT INTO ... VALUES (?)', (value,))"),
        ("6. Query data?", "cursor.execute('SELECT * FROM table')"),
        ("7. What is commit()?", "Saves changes to database"),
        ("8. What is rollback()?", "Undoes changes"),
        ("9. What is an ORM?", "Object-Relational Mapping (SQLAlchemy)"),
        ("10. What is SQLAlchemy?", "Popular Python ORM"),
        ("11. What is multiprocessing?", "Running multiple processes in parallel"),
        ("12. What is threading?", "Running multiple threads (GIL limits)"),
        ("13. What is the GIL?", "Global Interpreter Lock in CPython"),
        ("14. What is asyncio?", "Asynchronous I/O framework"),
        ("15. What is async/await?", "Keywords for asynchronous programming"),
        ("16. What is a coroutine?", "Async function with async def"),
        ("17. Async vs threading?", "Async single-threaded concurrency, threading multi-threaded"),
        ("18. What is type hinting?", "Annotations: def func(x: int) -> str:"),
        ("19. What are dataclasses?", "@dataclass decorator for data classes"),
        ("20. What are enums?", "Enumeration of named constants"),
        ("21. What is typing module?", "Type hints support (List, Dict, Optional)"),
        ("22. What is a metaclass?", "Class of a class (type is default)"),
        ("23. What is with statement?", "Context manager for resource management"),
        ("24. What is walrus operator (:=)?", "Assignment expression in Python 3.8+"),
        ("25. Positional-only parameters?", "Parameters before / must be positional")
    ]
    
    all_decks = [deck1, deck2, deck3, deck4, deck5, deck6, deck7, deck8, deck9, deck10,
                 deck11, deck12, deck13, deck14, deck15, deck16, deck17, deck18, deck19, deck20]
    
    deck_names = [
        "1. Python Basics", "2. Variables & Data Types", "3. Lists", "4. Tuples", "5. Dictionaries",
        "6. Sets", "7. Strings", "8. Control Flow", "9. Loops", "10. Functions",
        "11. Exception Handling", "12. File I/O", "13. OOP - Classes", "14. Inheritance",
        "15. Modules & Packages", "16. List Comprehensions", "17. Lambda Functions",
        "18. Decorators", "19. Generators", "20. Advanced Topics"
    ]
    
    created_decks = []
    for deck_idx, (deck_questions, deck_name) in enumerate(zip(all_decks, deck_names), 1):
        deck = Deck(
            name=deck_name,
            user_id=user_id,
            subject="Python Programming",
            difficulty="Beginner" if deck_idx <= 10 else "Intermediate"
        )
        db.session.add(deck)
        db.session.flush()
        
        for card_idx, (q, a) in enumerate(deck_questions, 1):
            # FSRS for odd numbers (1,3,5...), SM2 for even numbers (2,4,6...)
            # This gives 13 FSRS and 12 SM2 per deck
            algo = 'FSRS' if card_idx % 2 == 1 else 'SM2'
            card = Card(
                question=q,
                answer=a,
                deck_id=deck.id,
                algorithm=algo,
                stability=2.0,
                difficulty=5.0,
                e_factor=2.5,
                interval=1,
                review_count=0,
                avg_time=0.0,
                is_mastered=False
            )
            db.session.add(card)
        
        created_decks.append(deck)
        fsrs_count = sum(1 for c in deck.cards if c.algorithm == 'FSRS')
        sm2_count = sum(1 for c in deck.cards if c.algorithm == 'SM2')
        print(f"  Created: {deck_name} (FSRS: {fsrs_count}, SM2: {sm2_count})")
    
    db.session.commit()
    print(f"\n Successfully created {len(created_decks)} decks with 25 cards each for user {user_id}")
    return created_decks
