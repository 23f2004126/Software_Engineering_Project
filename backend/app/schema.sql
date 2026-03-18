-- Create Database
CREATE DATABASE IF NOT EXISTS shop_db;
USE shop_db;

-- Users Table
CREATE TABLE users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100),
    email VARCHAR(100) UNIQUE,
    password VARCHAR(255),
    phone VARCHAR(20),
    role ENUM('owner','employee','admin'),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Shifts Table
CREATE TABLE shifts (
    shift_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    start_time DATETIME,
    end_time DATETIME,
    shift_date DATE,
    status VARCHAR(50),
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);

-- Products Table
CREATE TABLE products (
    product_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100),
    category VARCHAR(50),
    unit VARCHAR(20),
    price DECIMAL(10,2),
    stock_quantity INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Customers Table
CREATE TABLE customers (
    customer_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100),
    phone VARCHAR(20),
    address TEXT,
    credit_balance DECIMAL(10,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Bills Table
CREATE TABLE bills (
    bill_id INT AUTO_INCREMENT PRIMARY KEY,
    customer_id INT,
    user_id INT,
    bill_date DATETIME,
    total_amount DECIMAL(10,2),
    payment_method VARCHAR(50),
    status VARCHAR(50),
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id),
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);

-- Bill Items Table
CREATE TABLE bill_items (
    bill_item_id INT AUTO_INCREMENT PRIMARY KEY,
    bill_id INT,
    product_id INT,
    quantity INT,
    price DECIMAL(10,2),
    subtotal DECIMAL(10,2),
    FOREIGN KEY (bill_id) REFERENCES bills(bill_id),
    FOREIGN KEY (product_id) REFERENCES products(product_id)
);

-- Credit Transactions
CREATE TABLE credit_transactions (
    transaction_id INT AUTO_INCREMENT PRIMARY KEY,
    customer_id INT,
    amount DECIMAL(10,2),
    type ENUM('credit','payment'),
    transaction_date DATETIME,
    note TEXT,
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
);

-- Expenses Table
CREATE TABLE expenses (
    expense_id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(100),
    amount DECIMAL(10,2),
    category VARCHAR(50),
    expense_date DATE,
    note TEXT
);

-- Suppliers Table
CREATE TABLE suppliers (
    supplier_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100),
    phone VARCHAR(20),
    address TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Purchase Orders
CREATE TABLE purchase_orders (
    purchase_id INT AUTO_INCREMENT PRIMARY KEY,
    supplier_id INT,
    product_id INT,
    quantity INT,
    price DECIMAL(10,2),
    total_cost DECIMAL(10,2),
    purchase_date DATE,
    FOREIGN KEY (supplier_id) REFERENCES suppliers(supplier_id),
    FOREIGN KEY (product_id) REFERENCES products(product_id)
);

-- Loss Logs
CREATE TABLE loss_logs (
    loss_id INT AUTO_INCREMENT PRIMARY KEY,
    product_id INT,
    quantity_lost INT,
    reason VARCHAR(255),
    loss_date DATE,
    FOREIGN KEY (product_id) REFERENCES products(product_id)
);

-- Milk Subscribers
CREATE TABLE milk_subscribers (
    subscriber_id INT AUTO_INCREMENT PRIMARY KEY,
    customer_id INT UNIQUE,
    daily_quantity DECIMAL(5,2),
    price_per_liter DECIMAL(10,2),
    start_date DATE,
    status VARCHAR(50),
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
);

-- Milk Daily Entries
CREATE TABLE milk_daily_entries (
    entry_id INT AUTO_INCREMENT PRIMARY KEY,
    subscriber_id INT,
    entry_date DATE,
    quantity DECIMAL(5,2),
    amount DECIMAL(10,2),
    delivered_by INT,
    FOREIGN KEY (subscriber_id) REFERENCES milk_subscribers(subscriber_id),
    FOREIGN KEY (delivered_by) REFERENCES users(user_id)
);