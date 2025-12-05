![img_1.png](img_1.png)
# Week 7: Secure Authentication System
Student Name: Munkurize Darina Visane

Student ID: M010157225

Course: CST1510 -CW2 - Multi-Domain Intelligence Platform
## Project Description
A command-line authentication system implementing secure password hashing
This system allows users to register accounts and login with proper pass
## Features
-   Secure password hashing using bcrypt with automatic salt generation
-   User registration with duplicate username prevention
-   User login with password verification
-   Input validation for usernames and passwords - File-based user data persistence

## Technical Implementation

-  Hashing Algorithm: bcrypt with automatic salting
- Data storage: Plain text file ('users.txt') with comma-separated values 
- Password Security: One-way hashing, no plaintext storage
- Validation: Username (3-20 alphanumeric characters), Password (6-50) characters