
USE company;
GO

INSERT INTO employee (ssn, fname, lname, bdate, address, gender, salary, Dno)
VALUES ('777777777', 'Sara', 'Kamal', '1994-04-12', '5 Roushdy St, Alexandria', 'F', 40000.00, 1);
GO

INSERT INTO department (Dnumber, Dname, mgr_ssn, mgr_start_date)
VALUES (4, 'Finance', '777777777', '2024-01-01');
GO

-- Expected: fails with a FOREIGN KEY / REFERENCE conflict (Msg 547)
DELETE FROM employee WHERE ssn = '777777777';
GO

-- Proof that the employee is still there
SELECT ssn, fname, lname FROM employee WHERE ssn = '777777777';
GO


-- ---------------- Q1.2 ----------------
-- Insert a project that references department 9, which does not exist yet.

-- Expected: fails (Msg 547)
INSERT INTO project (Pnumber, Pname, Plocation, Dno)
VALUES (50, 'Cloud Migration', 'Alexandria', 9);
GO

-- Create the department first (its manager already exists) ...
INSERT INTO department (Dnumber, Dname, mgr_ssn, mgr_start_date)
VALUES (9, 'Legal', '111111111', '2024-01-01');
GO

-- ... and now the same project insert works
INSERT INTO project (Pnumber, Pname, Plocation, Dno)
VALUES (50, 'Cloud Migration', 'Alexandria', 9);
GO

SELECT * FROM project WHERE Pnumber = 50;
GO


------------------------------------------------------------
-- PART B  (first re-run problem1_DDL.sql so the tables are EMPTY)
------------------------------------------------------------

-- ---------------- Q1.3 ----------------
-- mgr_ssn and Dno are both NOT NULL: how do we insert the first row?

USE company;
GO

-- Attempt 1: first employee. Expected: fails, department 1 does not exist (Msg 547)
INSERT INTO employee (ssn, fname, lname, bdate, address, gender, salary, Dno)
VALUES ('111111111', 'Ahmed', 'Hassan', '1985-03-14', '12 Fouad St, Alexandria', 'M', 52000.00, 1);
GO

-- Attempt 2: first department. Expected: fails, employee 111111111 does not exist (Msg 547)
INSERT INTO department (Dnumber, Dname, mgr_ssn, mgr_start_date)
VALUES (1, 'Research', '111111111', '2020-01-01');
GO

-- Solution: switch both foreign keys off, insert, switch them back on WITH CHECK
ALTER TABLE employee   NOCHECK CONSTRAINT FK_employee_department;
ALTER TABLE department NOCHECK CONSTRAINT FK_department_manager;
GO

INSERT INTO employee (ssn, fname, lname, bdate, address, gender, salary, Dno)
VALUES ('111111111', 'Ahmed', 'Hassan', '1985-03-14', '12 Fouad St, Alexandria', 'M', 52000.00, 1);
GO

INSERT INTO department (Dnumber, Dname, mgr_ssn, mgr_start_date)
VALUES (1, 'Research', '111111111', '2020-01-01');
GO

ALTER TABLE employee   WITH CHECK CHECK CONSTRAINT FK_employee_department;
ALTER TABLE department WITH CHECK CHECK CONSTRAINT FK_department_manager;
GO

SELECT * FROM employee;
SELECT * FROM department;
GO


------------------------------------------------------------
-- PART C  Re-run problem1_DDL.sql, then problem1_DML.sql.
------------------------------------------------------------
