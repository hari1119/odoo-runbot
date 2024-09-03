CREATE OR REPLACE FUNCTION global_search(search_term text)
RETURNS TABLE (tablename text, columnname text, row_data text) AS
$$
DECLARE
    rec RECORD;
    sql_query TEXT;
BEGIN
    FOR rec IN
        SELECT table_name, column_name
        FROM information_schema.columns
        WHERE table_schema = 'public' -- Adjust schema as necessary
          AND data_type IN ('character', 'character varying', 'text')
    LOOP
        BEGIN
        sql_query := format('
        SELECT %L AS tablename, %L AS columnname, %I::text AS row_data
        FROM %I
        WHERE %I::text ILIKE %L',
        rec.table_name, rec.column_name, rec.column_name, rec.table_name, rec.column_name,
        '%' || search_term || '%');

            RETURN QUERY EXECUTE sql_query;
        EXCEPTION
            WHEN undefined_table THEN
                CONTINUE; -- Skip to the next iteration if the table doesn't exist
            WHEN undefined_column THEN
                CONTINUE; -- Skip to the next iteration if the column doesn't exist
            WHEN others THEN
                RAISE NOTICE 'Error occurred: %', SQLERRM; -- Optional: handle or log other exceptions
        END;
    END LOOP;
    RETURN;
END;
$$ LANGUAGE plpgsql
