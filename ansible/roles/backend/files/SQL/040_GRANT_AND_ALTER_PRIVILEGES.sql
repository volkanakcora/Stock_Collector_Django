-- application user for public schema
\connect stock;
-- default privileges (Default grants for new tables etc.)
ALTER DEFAULT PRIVILEGES FOR ROLE stock IN SCHEMA public GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO stock;
ALTER DEFAULT PRIVILEGES FOR ROLE stock IN SCHEMA public GRANT USAGE ON SEQUENCES TO stock;
ALTER DEFAULT PRIVILEGES FOR ROLE stock IN SCHEMA public GRANT EXECUTE ON FUNCTIONS TO stock;
-- grants (For already existing tables etc.)
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES in SCHEMA public TO stock;
GRANT USAGE ON ALL SEQUENCES IN SCHEMA public TO stock;
GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA public TO stock;
-- general grants
GRANT CONNECT ON DATABASE stock TO stock;
GRANT USAGE ON SCHEMA public TO stock;
