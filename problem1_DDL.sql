
IF DB_ID('company') IS NOT NULL
BEGIN
    ALTER DATABASE company SET SINGLE_USER WITH ROLLBACK IMMEDIATE;
    DROP DATABASE company;
END
GO

CREATE DATABASE company;
GO

USE company;

CREATE TABLE employee (
    ssn     CHAR(9)        NOT NULL,
    fname   VARCHAR(30)    NOT NULL,
    lname   VARCHAR(30)    NOT NULL,
    bdate   DATE           NOT NULL,
    address VARCHAR(100)   NOT NULL,
    gender  CHAR(1)        NOT NULL,
    salary  DECIMAL(10, 2) NOT NULL,
    Dno     INT            NOT NULL,
    PRIMARY KEY (ssn)
);
GO

CREATE TABLE department (
    Dnumber        INT         NOT NULL,
    Dname          VARCHAR(50) NOT NULL,
    mgr_ssn        CHAR(9)     NOT NULL,
    mgr_start_date DATE        NOT NULL,
    PRIMARY KEY (Dnumber),
    UNIQUE (Dname)
);
GO

CREATE TABLE project (
    Pnumber   INT         NOT NULL,
    Pname     VARCHAR(50) NOT NULL,
    Plocation VARCHAR(50) NOT NULL,
    Dno       INT         NOT NULL,
    PRIMARY KEY (Pnumber)
);
GO


ALTER TABLE employee
    ADD CONSTRAINT FK_employee_department
    FOREIGN KEY (Dno) REFERENCES department (Dnumber);
GO

ALTER TABLE department
    ADD CONSTRAINT FK_department_manager
    FOREIGN KEY (mgr_ssn) REFERENCES employee (ssn);
GO

ALTER TABLE project
    ADD CONSTRAINT FK_project_department
    FOREIGN KEY (Dno) REFERENCES department (Dnumber);
GO
