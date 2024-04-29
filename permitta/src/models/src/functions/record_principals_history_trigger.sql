CREATE OR REPLACE TRIGGER record_principals_history
AFTER INSERT OR UPDATE OR DELETE ON principals
FOR EACH ROW EXECUTE FUNCTION record_principals_history();