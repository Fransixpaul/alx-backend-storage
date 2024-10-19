--Script to create the 'users' table with unique email field
-- Create table 'users' with unique email and auto-incrementing id
CREATE TABLE IF NOT EXISTS users (
    id INT NOT NULL AUTO_INCREMENT,
    email VARCHAR(255) NOT NULL UNIQUE,
    name VARCHAR(255),
    PRINMARY KEY (id)
);