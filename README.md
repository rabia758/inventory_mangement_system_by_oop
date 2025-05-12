# Inventory_Management_System

This is a robust Inventory Management System built with Python using Object-Oriented Programming principles. The system allows you to manage different types of products (electronics, groceries, and clothing), handle stock operations, process sales, and persist data to JSON files.

# Features
# Product_Management:

Abstract base Product class with common attributes and methods

Three specialized product types:

Electronics: With warranty and brand information

Grocery: With expiry date tracking and expiration checking

Clothing: With size and material details

# Inventory_Operations:

Add, remove, and search products

Sell and restock items with proper stock validation

Calculate total inventory value

Automatic removal of expired grocery items

# Data_Persistence:

Save entire inventory to JSON file

Load inventory from JSON file with proper object reconstruction

# Error_Handling:

Custom exceptions for common error scenarios

Input validation throughout the system

# User_Interface:

Command-line interface with intuitive menu system

Clear feedback for all operations
