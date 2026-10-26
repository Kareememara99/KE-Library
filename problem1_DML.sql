
USE company;
GO


ALTER TABLE employee   NOCHECK CONSTRAINT FK_employee_department;
ALTER TABLE department NOCHECK CONSTRAINT FK_department_manager;
GO

INSERT INTO employee (ssn, fname, lname, bdate, address, gender, salary, Dno) VALUES
('111111111', 'Ahmed',  'Hassan',  '1985-03-14', '12 Fouad St, Alexandria',        'M', 52000.00, 1),
('222222222', 'Mona',   'Salem',   '1990-07-22', '45 Corniche Rd, Alexandria',     'F', 47000.00, 2),
('333333333', 'Omar',   'Farouk',  '1988-11-05', '8 Sporting St, Alexandria',      'M', 61000.00, 3),
('444444444', 'Laila',  'Nabil',   '1993-01-30', '27 Gleem Ave, Alexandria',       'F', 38000.00, 1),
('555555555', 'Youssef','Mansour', '1995-09-18', '3 Smouha Blvd, Alexandria',      'M', 35000.00, 2),
('666666666', 'Nour',   'Adel',    '1992-05-09', '91 Stanley Bridge, Alexandria',  'F', 42000.00, 3);
GO

INSERT INTO department (Dnumber, Dname, mgr_ssn, mgr_start_date) VALUES
(1, 'Research',       '111111111', '2020-01-01'),
(2, 'Administration', '222222222', '2021-06-15'),
(3, 'Headquarters',   '333333333', '2019-09-01');
GO

ALTER TABLE employee   WITH CHECK CHECK CONSTRAINT FK_employee_department;
ALTER TABLE department WITH CHECK CHECK CONSTRAINT FK_department_manager;
GO

INSERT INTO project (Pnumber, Pname, Plocation, Dno) VALUES
(10, 'Data Warehouse',   'Alexandria', 1),
(20, 'Payroll System',   'Cairo',      2),
(30, 'Office Expansion', 'Alexandria', 3),
(40, 'Mobile App',       'Giza',       1);
GO

SELECT * FROM employee;
SELECT * FROM department;
SELECT * FROM project;
GO
