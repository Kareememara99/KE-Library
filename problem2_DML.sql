USE library;
GO

-- Run problem2_DDL.sql first: the ids are generated automatically (1, 2, 3, 4).
INSERT INTO author (name, country) VALUES
('Naguib Mahfouz',          'Egypt'),    
('Agatha Christie',         'UK'),        
('Gabriel Garcia Marquez',  'Colombia'),  
('Taha Hussein',            'Egypt');     
GO

INSERT INTO book (title, price, author_id) VALUES
('Palace Walk',                    14.50, 1),
('Midaq Alley',                    12.00, 1),
('Children of the Alley',          13.75, 1),
('Murder on the Orient Express',   11.25, 2),
('And Then There Were None',       10.99, 2),
('Death on the Nile',              11.50, 2),
('One Hundred Years of Solitude',  16.00, 3),
('Love in the Time of Cholera',    15.25, 3),
('The Days',                        9.50, 4);
GO

SELECT * FROM author;
SELECT * FROM book;
GO
