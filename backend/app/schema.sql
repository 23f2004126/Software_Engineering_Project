-- =========================
-- CREATE DATABASE
-- =========================
CREATE DATABASE IF NOT EXISTS shop_db;
USE shop_db;

-- =========================
-- ROLES TABLE
-- =========================
CREATE TABLE roles (
    role_id INT AUTO_INCREMENT PRIMARY KEY,
    role_name VARCHAR(50) UNIQUE NOT NULL
);

INSERT INTO roles (role_name) VALUES 
('admin'),
('employee');

-- =========================
-- DESIGNATIONS TABLE
-- =========================
CREATE TABLE designations (
    designation_id INT AUTO_INCREMENT PRIMARY KEY,
    designation_name VARCHAR(50) UNIQUE NOT NULL
);

INSERT INTO designations (designation_name) VALUES
('Supervisor'),
('Sales_staff'),
('Store_manager'),
('Inventory_manager');

-- =========================
-- USERS TABLE
-- =========================
CREATE TABLE users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    phone VARCHAR(20),

    role_id INT NOT NULL,
    designation_id INT NULL,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    FOREIGN KEY (role_id) REFERENCES roles(role_id),
    FOREIGN KEY (designation_id) REFERENCES designations(designation_id)
);

-- =========================
-- SHIFTS TABLE
-- =========================
CREATE TABLE shifts (
    shift_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    start_time DATETIME,
    end_time DATETIME,
    shift_date DATE,
    status ENUM('active','completed','cancelled'),

    FOREIGN KEY (user_id) REFERENCES users(user_id)
);

-- =========================
-- CATEGORIES TABLE
-- =========================
CREATE TABLE categories (
    category_id INT AUTO_INCREMENT PRIMARY KEY,
    category_name VARCHAR(50) UNIQUE NOT NULL
);

-- =========================
-- PRODUCTS TABLE
-- =========================
CREATE TABLE products (
    product_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    category_id INT,
    unit VARCHAR(20),
    price DECIMAL(10,2),
    stock_quantity INT DEFAULT 0,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    FOREIGN KEY (category_id) REFERENCES categories(category_id)
);

-- =========================
-- CUSTOMERS TABLE
-- =========================
CREATE TABLE customers (
    customer_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100),
    phone VARCHAR(20),
    address TEXT,
    credit_balance DECIMAL(10,2) DEFAULT 0,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =========================
-- BILLS TABLE
-- =========================
CREATE TABLE bills (
    bill_id INT AUTO_INCREMENT PRIMARY KEY,
    customer_id INT,
    user_id INT,

    bill_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    total_amount DECIMAL(10,2),

    payment_method ENUM('cash','card','upi','credit'),
    status ENUM('paid','pending','cancelled'),

    FOREIGN KEY (customer_id) REFERENCES customers(customer_id),
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);

-- =========================
-- BILL ITEMS TABLE
-- =========================
CREATE TABLE bill_items (
    bill_item_id INT AUTO_INCREMENT PRIMARY KEY,
    bill_id INT,
    product_id INT,

    quantity INT,
    price DECIMAL(10,2),
    subtotal DECIMAL(10,2),

    FOREIGN KEY (bill_id) REFERENCES bills(bill_id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES products(product_id)
);

-- =========================
-- CREDIT TRANSACTIONS
-- =========================
CREATE TABLE credit_transactions (
    transaction_id INT AUTO_INCREMENT PRIMARY KEY,
    customer_id INT,

    amount DECIMAL(10,2),
    type ENUM('credit','payment'),
    transaction_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    note TEXT,

    FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
);

-- =========================
-- EXPENSES TABLE
-- =========================
CREATE TABLE expenses (
    expense_id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(100),
    amount DECIMAL(10,2),

    category VARCHAR(50),
    expense_date DATE,
    note TEXT
);

-- =========================
-- SUPPLIERS TABLE
-- =========================
CREATE TABLE suppliers (
    supplier_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100),
    phone VARCHAR(20),
    address TEXT,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =========================
-- PURCHASE ORDERS
-- =========================
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

-- =========================
-- LOSS LOGS
-- =========================
CREATE TABLE loss_logs (
    loss_id INT AUTO_INCREMENT PRIMARY KEY,
    product_id INT,

    quantity_lost INT,
    reason VARCHAR(255),
    loss_date DATE,

    FOREIGN KEY (product_id) REFERENCES products(product_id)
);

-- =========================
-- MILK SUBSCRIBERS
-- =========================
CREATE TABLE milk_subscribers (
    subscriber_id INT AUTO_INCREMENT PRIMARY KEY,
    customer_id INT UNIQUE,

    daily_quantity DECIMAL(5,2),
    price_per_liter DECIMAL(10,2),

    start_date DATE,
    status ENUM('active','inactive'),

    FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
);

-- =========================
-- MILK DAILY ENTRIES
-- =========================
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

-- =========================
-- INDEXES (PERFORMANCE)
-- =========================
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_products_name ON products(name);
CREATE INDEX idx_customers_phone ON customers(phone);