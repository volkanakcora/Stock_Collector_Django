DO
$do$
BEGIN
    IF NOT EXISTS(SELECT rolname FROM pg_roles WHERE rolname = 'stock') THEN
        CREATE ROLE stock WITH LOGIN;
    END IF;
END
$do$;

-- Attempt to create the database; it will fail if it already exists
CREATE DATABASE stock WITH OWNER = stock;
