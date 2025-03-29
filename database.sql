CREATE DATABASE FinanceTracker;
USE FinanceTracker;
CREATE TABLE Users (
    user_id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(255),
    email VARCHAR(255) UNIQUE,
    password VARCHAR(255)
);
CREATE TABLE Expenses (
    expense_id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT,
    category VARCHAR(100),
    amount DECIMAL(10,2),
    description TEXT,
    expense_date DATE,
    FOREIGN KEY (user_id) REFERENCES Users(user_id)
);
SHOW DATABASES;
INSERT INTO Users (name, email, password) VALUES 
('Aniruddh', 'aniruddhh76@gmail.@gmail.com', 'annuu@2005');

INSERT INTO Expenses (user_id, category, amount, description, expense_date) VALUES
(1, 'Food', 500.00, 'Dinner at restaurant', '2025-03-20');

select*from expenses
