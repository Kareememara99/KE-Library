USE master;
GO

IF DB_ID('library') IS NOT NULL
BEGIN
    ALTER DATABASE library SET SINGLE_USER WITH ROLLBACK IMMEDIATE;
    DROP DATABASE library;
END
GO

CREATE DATABASE library;
GO

USE library;
GO

CREATE TABLE author (
    author_id INT IDENTITY(1,1) NOT NULL,
    name      VARCHAR(100)      NOT NULL,
    country   VARCHAR(50)       NOT NULL,
    PRIMARY KEY (author_id)
);
GO

CREATE TABLE book (
    book_id   INT IDENTITY(1,1) NOT NULL,
    title     VARCHAR(150)      NOT NULL,
    price     DECIMAL(10, 2)    NOT NULL,
    author_id INT               NOT NULL,
    PRIMARY KEY (book_id),
    CONSTRAINT CK_book_price CHECK (price >= 0),
    -- deleting an author deletes all of his/her books too
    CONSTRAINT FK_book_author FOREIGN KEY (author_id)
        REFERENCES author (author_id)
        ON DELETE CASCADE
);
GO
