-- FUNCTION: public.generatesequenceno(integer, character varying, date, integer, integer, character varying)

-- DROP FUNCTION IF EXISTS public.generatesequenceno(integer, character varying, date, integer, integer, character varying);

CREATE OR REPLACE FUNCTION public.generatesequenceno(
	v_sequence_id integer,
	v_sequence_code character varying,
	v_date date,
	v_company_id integer,
	v_division_id integer,
	v_sequence_type character varying)
    RETURNS character varying
    LANGUAGE 'plpgsql'
    COST 100
    VOLATILE PARALLEL UNSAFE
AS $BODY$
DECLARE 	
  exist_count integer;
  v_prefix  char varying(100);
  v_ir_name  char varying(100);
  v_company_code  char varying(100);
  v_division_code  char varying(100);
  v_seq_month char varying(100);
  v_fiscal_year_code  char varying(100);
  v_fiscal_year_id  integer;
  v_seq_year char varying(100);
  v_seq_day integer;
  v_ir_sequence_id integer;
  v_seq_next_number integer;
  v_generated_prefix  char varying(100);
  v_padding integer;
  v_seq_month_str char varying(10);
  v_seq_year_str char varying(10);
  v_seq_day_str char varying(10);
  v_seq_number_str char varying(100);
  v_trans_date date;
  v_reset_sequence char varying(100);
  v_actual_seq_year integer;
  v_previuos_year int;
  v_actual_month int;
  v_previuos_month int;

BEGIN
		select value into v_reset_sequence from ir_config_parameter where key = 'custom_properties.seq_num_reset' order by id desc limit 1;
        
		select prefix,id,padding,name into v_prefix,
        v_ir_sequence_id,v_padding,v_ir_name from ir_sequence where code=v_sequence_code
        and id=v_sequence_id;

        select name into v_company_code
        from res_company where id=v_company_id;

        select short_name into v_division_code
        from cm_master where id=v_division_id;

        if(v_date is null) then
          v_trans_date=now();
        else 
          v_trans_date=v_date;
        end if;
        
        select extract(month from v_trans_date) into v_seq_month;
        select extract(year from v_trans_date) into v_seq_year;
              
       exist_count=0;

		if(v_reset_sequence='fiscal_year') then
			select id,short_name into v_fiscal_year_id,v_fiscal_year_code from cm_fiscal_year where from_date <= v_trans_date and to_date >= v_trans_date and status = 'active' and active='t';
			if(v_fiscal_year_id is not null) then
				if(v_sequence_type='division') then 
					 select count(*) into exist_count from cp_ir_sequence_generate where  fiscal_year_id=v_fiscal_year_id and fiscal_year_code=v_fiscal_year_code and ir_sequence_id=v_ir_sequence_id and company_id=v_company_id and division_id=v_division_id;
					  if(exist_count >0) then
						select seq_next_number into v_seq_next_number from cp_ir_sequence_generate where  fiscal_year_id=v_fiscal_year_id and fiscal_year_code=v_fiscal_year_code and ir_sequence_id=v_ir_sequence_id and company_id=v_company_id and division_id=v_division_id; 
						Update cp_ir_sequence_generate set seq_next_number=seq_next_number + 1  where  fiscal_year_id=v_fiscal_year_id and fiscal_year_code=v_fiscal_year_code and ir_sequence_id=v_ir_sequence_id and company_id=v_company_id and division_id=v_division_id;
					  else
						v_seq_next_number=1;
						Insert into cp_ir_sequence_generate(ir_sequence_id,create_date,seq_next_number,company_id,division_id,fiscal_year_id,fiscal_year_code,active,name,entry_mode,user_id,crt_date)
						Values(v_ir_sequence_id,now(),2,v_company_id,v_division_id,v_fiscal_year_id,v_fiscal_year_code,'t',v_ir_name,'manual',1,now());
					  end if;
				elseif(v_sequence_type='company') then 
					 select count(*) into exist_count from cp_ir_sequence_generate where  fiscal_year_id=v_fiscal_year_id and fiscal_year_code=v_fiscal_year_code and ir_sequence_id=v_ir_sequence_id and company_id=v_company_id;
					  if(exist_count >0) then
						select seq_next_number into v_seq_next_number from cp_ir_sequence_generate where  fiscal_year_id=v_fiscal_year_id and fiscal_year_code=v_fiscal_year_code and ir_sequence_id=v_ir_sequence_id and company_id=v_company_id; 
						Update cp_ir_sequence_generate set seq_next_number=seq_next_number + 1  where  fiscal_year_id=v_fiscal_year_id and fiscal_year_code=v_fiscal_year_code and ir_sequence_id=v_ir_sequence_id and company_id=v_company_id;
					  else
						v_seq_next_number=1;
						Insert into cp_ir_sequence_generate(ir_sequence_id,create_date,seq_next_number,company_id,fiscal_year_id,fiscal_year_code,active,name,entry_mode,user_id,crt_date)
						Values(v_ir_sequence_id,now(),2,v_company_id,v_fiscal_year_id,v_fiscal_year_code,'t',v_ir_name,'manual',1,now());
					  end if;
				else 
					 select count(*) into exist_count from cp_ir_sequence_generate where  fiscal_year_id=v_fiscal_year_id and fiscal_year_code=v_fiscal_year_code and ir_sequence_id=v_ir_sequence_id;
					  if(exist_count >0) then
						select seq_next_number into v_seq_next_number from cp_ir_sequence_generate where  fiscal_year_id=v_fiscal_year_id and fiscal_year_code=v_fiscal_year_code and ir_sequence_id=v_ir_sequence_id; 
						Update cp_ir_sequence_generate set seq_next_number=seq_next_number + 1  where  fiscal_year_id=v_fiscal_year_id and fiscal_year_code=v_fiscal_year_code and ir_sequence_id=v_ir_sequence_id;
					  else
						v_seq_next_number=1;
						Insert into cp_ir_sequence_generate(ir_sequence_id,create_date,seq_next_number,fiscal_year_id,fiscal_year_code,active,name,entry_mode,user_id,crt_date)
						Values(v_ir_sequence_id,now(),2,v_fiscal_year_id,v_fiscal_year_code,'t',v_ir_name,'manual',1,now());
					  end if;
				end if;
			else
				v_seq_next_number = 0;
			end if;
		elseif(v_reset_sequence='calendar_year') then
			if(v_sequence_type='division') then 
				 select count(*) into exist_count from cp_ir_sequence_generate where seq_year=v_seq_year and ir_sequence_id=v_ir_sequence_id and company_id=v_company_id and division_id=v_division_id;
				  if(exist_count >0) then
					select seq_next_number into v_seq_next_number from cp_ir_sequence_generate where  seq_year=v_seq_year and ir_sequence_id=v_ir_sequence_id and company_id=v_company_id and division_id=v_division_id; 
					Update cp_ir_sequence_generate set seq_next_number=seq_next_number + 1  where  seq_year=v_seq_year and ir_sequence_id=v_ir_sequence_id and company_id=v_company_id and division_id=v_division_id;
				  else
					v_seq_next_number=1;
					Insert into cp_ir_sequence_generate(ir_sequence_id,create_date,seq_year,seq_next_number,company_id,division_id,active,name,entry_mode,user_id,crt_date)
					Values(v_ir_sequence_id,now(),v_seq_year,2,v_company_id,v_division_id,'t',v_ir_name,'manual',1,now());
				  end if;
			elseif(v_sequence_type='company') then 
				 select count(*) into exist_count from cp_ir_sequence_generate where  seq_year=v_seq_year and ir_sequence_id=v_ir_sequence_id and company_id=v_company_id;
				  if(exist_count >0) then
					select seq_next_number into v_seq_next_number from cp_ir_sequence_generate where  seq_year=v_seq_year and ir_sequence_id=v_ir_sequence_id and company_id=v_company_id; 
					Update cp_ir_sequence_generate set seq_next_number=seq_next_number + 1  where  seq_year=v_seq_year and ir_sequence_id=v_ir_sequence_id and company_id=v_company_id;
				  else
					v_seq_next_number=1;
					Insert into cp_ir_sequence_generate(ir_sequence_id,create_date,seq_year,seq_next_number,company_id,active,name,entry_mode,user_id,crt_date)
					Values(v_ir_sequence_id,now(),v_seq_year,2,v_company_id,'t',v_ir_name,'manual',1,now());
				  end if;
			else 
				 select count(*) into exist_count from cp_ir_sequence_generate where  seq_year=v_seq_year and ir_sequence_id=v_ir_sequence_id;
				  if(exist_count >0) then
					select seq_next_number into v_seq_next_number from cp_ir_sequence_generate where  seq_year=v_seq_year and ir_sequence_id=v_ir_sequence_id; 
					Update cp_ir_sequence_generate set seq_next_number=seq_next_number + 1  where  seq_year=v_seq_year and ir_sequence_id=v_ir_sequence_id;
				  else
					v_seq_next_number=1;
					Insert into cp_ir_sequence_generate(ir_sequence_id,create_date,seq_year,seq_next_number,active,name,entry_mode,user_id,crt_date)
					Values(v_ir_sequence_id,now(),v_seq_year,2,'t',v_ir_name,'manual',1,now());
				  end if;
			end if;
		end if;
		
		v_generated_prefix='';
		
		if(v_reset_sequence='fiscal_year') then
        	v_generated_prefix=Replace(v_prefix,'%(year)s',v_fiscal_year_code);
		elseif(v_reset_sequence='calendar_year') then
			v_generated_prefix=Replace(v_prefix,'%(year)s',v_seq_year);
		end if;
		
        v_seq_number_str=lpad(v_seq_next_number::char varying(100),v_padding , '0');
        
        
		if(v_sequence_type='division') then
			v_generated_prefix=v_generated_prefix || v_division_code || '/' || v_seq_number_str;
		elseif(v_sequence_type='company') then
			v_generated_prefix=v_generated_prefix || v_company_code || '/' || v_seq_number_str;
		else
			v_generated_prefix=v_generated_prefix || v_seq_number_str;
        end if;
        
       RETURN v_generated_prefix;
END;
$BODY$;

ALTER FUNCTION public.generatesequenceno(integer, character varying, date, integer, integer, character varying)
    OWNER TO odoo;

