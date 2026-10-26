DROP DATABASE IF EXISTS registration; 
CREATE DATABASE registration;
USE registration;

CREATE TABLE users (
    user_id           INT          NOT NULL identity(1,1),
    email             VARCHAR(255) NOT NULL,
    name              VARCHAR(100) NOT NULL,
    password_hash     VARCHAR(255) NOT NULL,
    registration_date DATETIME2   NOT NULL DEFAULT SYSDATETIME(),
    PRIMARY KEY (user_id),
    UNIQUE (email)
);


CREATE TABLE todos (
    todo_id    INT          NOT NULL identity(1,1),
    user_id    INT          NOT NULL,
    title      VARCHAR(200) NOT NULL,
    is_done    TINYINT   NOT NULL DEFAULT 0,
    created_at DATETIME2 NOT NULL DEFAULT SYSDATETIME(),
    PRIMARY KEY (todo_id),
    FOREIGN KEY (user_id) REFERENCES users (user_id)
);


select * from users
select * from todos


INSERT INTO users (email, name, password_hash)
VALUES ('test@example.com', 'Test User', 'fake-hash-for-testing');

INSERT INTO todos (user_id, title)
VALUES (1, 'Finish the database lab');


drop table users 
drop table todos


SELECT * FROM users;
SELECT * FROM todos;






