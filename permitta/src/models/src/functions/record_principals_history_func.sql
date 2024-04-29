CREATE OR REPLACE FUNCTION record_principals_history()
  RETURNS TRIGGER
  LANGUAGE PLPGSQL
  AS
$$
BEGIN
    IF (TG_OP = 'DELETE') THEN
        insert into principals_history select nextval('principals_history_principal_history_id_seq'), now(), 'D', OLD.*;
    ELSIF (TG_OP = 'UPDATE') THEN -- both OLD and NEW are valid
        insert into principals_history select nextval('principals_history_principal_history_id_seq'), now(), 'U', NEW.*;
    ELSIF (TG_OP = 'INSERT') THEN -- OLD is null, NEW is valid
        insert into principals_history select nextval('principals_history_principal_history_id_seq'), now(), 'I', NEW.*;
    END IF;
	RETURN NULL; -- not required for an AFTER trigger
END;
$$;