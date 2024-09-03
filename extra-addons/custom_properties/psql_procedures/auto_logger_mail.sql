-- FUNCTION: public.auto_logger_mail()

-- DROP FUNCTION IF EXISTS public.auto_logger_mail();

CREATE OR REPLACE FUNCTION public.auto_logger_mail()
    RETURNS text
    LANGUAGE 'plpgsql'
    COST 100
    VOLATILE PARALLEL UNSAFE
AS $BODY$
DECLARE
cursor_temp refcursor;
cursor_temp123 refcursor;  

v_table_heading text;
v_data text;

-- Header fields
v_sl_no integer;
v_trans_id integer;
v_log_date char varying (10000);
v_db_name char varying (10000);
v_error_message text;

BEGIN

v_table_heading='';
v_data='';
v_sl_no =1;

			v_table_heading='<html ><head>
			<style type="text/css">
			* {-webkit-font-smoothing: antialiased;}
			body {Margin: 0;padding: 0;min-width: 100%;font-family: "Times New Roman", Times, serif;-webkit-font-smoothing: antialiased;mso-line-height-rule: exactly;}
			table {border-spacing: 0;color: #333333;font-family: "Times New Roman", Times, serif;}
			img {border: 0;}
			table.logo-table {margin-top: 30px;}
			table.table-top {margin-top: 6px;}
			.wrapper {width: 100%;table-layout: fixed;-webkit-text-size-adjust: 100%;-ms-text-size-adjust: 100%;}
			.webkit {max-width: 600px;}
			.outer {Margin: 0 auto;width: 100%;max-width: 600px;}
			.full-width-image img {width: 100%;max-width: 600px;height: auto;}
			.inner {padding: 10px;}
			.contents {width: 100%;}
			.two-column img {width: 100%;max-width: 280px;height: auto;margin-top: 20px;}
			#customers,#customers-campus,#customers-nohover {font-family: "Times New Roman", Times, serif;border-collapse: collapse;width: 100%;}
			#customers tbody,#customers-campus tbody,#customers-nohover tbody {width: 80%;}
			#customers-nohover th {padding: 8px;background: #fff;}
			#customers td,#customers th,#customers-campus td,#customers-campus th {border-left: 1px solid #007AFF;border-right: 1px solid #007AFF;border-top: 1px solid #007AFF;padding: 8px;border-bottom: 1px solid #007AFF;padding: 8px;}
			#customers th,#customers-campus th {font-weight: normal;background: #ADD8E6;}
			#customers tr:nth-child(even) {background-color: #f2f2f2;}
			#customers tr:hover {background-color: #ddd;}
			#customers tr th:hover {background-color: none!important;}
			#customers tbody tr th:hover {background-color: none!important;}
			#customers th,#customers-campus th {text-align: left;padding: 8px;}
			.green {background: #ddd;}
			</style></head>
			<body style="Margin:0;padding-top:0;padding-bottom:0;padding-right:0;padding-left:0;min-width:100%;background-color:#ececec;">
			<center class="wrapper" style="width:100%;table-layout:fixed;-webkit-text-size-adjust:100%;-ms-text-size-adjust:100%;background-color:#ececec;">
			<table width="100%" cellpadding="0" cellspacing="0" border="0" style="background-color:#ececec;" bgcolor="#ececec;">
			<tr>
			<td width="100%">
			<div class="webkit" style="max-width:1000px;Margin:0 auto;">
			<table class="outer" align="center" cellpadding="0" cellspacing="0" border="0" style="border-spacing:0;Margin:0 auto;width:100%;max-width:1000px;">
			<tr>
			<td style="padding-top:0;padding-bottom:0;padding-right:0;padding-left:0;">
			<!-- ======= start header ======= -->
			<table border="0" width="100%" cellpadding="0" cellspacing="0" class="logo-table">
			<tr>
			<td style="width:100%; border-top-left-radius:10px; border-top-right-radius:10px" height="6" bgcolor="#029EFC" class="contents">
			<table style="width:100%;" cellpadding="0" cellspacing="0" border="0" class="table-top">
			<tbody>
			<tr>
			<td align="center">
			<center>
			<table border="0" align="center" width="100%" cellpadding="0" cellspacing="0" style="Margin: 0 auto;">
			<tbody>
			<tr>
			<td class="one-column" style="padding-top:0;padding-bottom:0;padding-right:0;padding-left:0;" bgcolor="#FFFFFF">
			<table class="logo" cellpadding="0" cellspacing="0" border="0" width="100%">
			<tr>
			<td class="two-column" style="padding-top:0;padding-bottom:0;padding-right:0;padding-left:0;text-align:center;font-size:0;">
			<div class="column" style="width:100%;max-width:150px;display:inline-block;vertical-align:top;">
			<table class="contents logo" style="border-spacing:0; width:100%" bgcolor="#ffffff">
			<tr>
			<td style="padding-top:0;padding-bottom:0;padding-right:0;padding-left:0;" align="center">
			<a href="#" target="_blank"><!-- <img src="#"  alt="" style="border-width:0; height:auto; display:block" /> --></a>
			</td>
			</tr>
			</table>
			</div>
			</td>
			</tr>
			</table>
			</td>
			</tr>
			</tbody>
			</table>
			</center>
			</td>
			</tr>
			</tbody>
			</table>
			</td>
			</tr>
			</table>
			<table class="one-column" border="0" cellpadding="0" cellspacing="0" width="100%" style="border-spacing:0" bgcolor="#029EFC">
			<tr>
			<td align="left" style="padding-left:10px; padding-right:20px; padding-top:0px; padding-bottom:10px">
			</td>';
			
			---Greetings
			SELECT current_database() into v_db_name;
			v_table_heading= v_table_heading || '<table id="customers" style="border:none;">
				<tr style="border:1px solid #007AFF;"><td colspan="2" style="border:none;"><b style="margin-top: 15px;">Dear Sir / Mam</b>,</td></tr>
				<tr style="border-left:1px solid #007AFF;border-right:1px solid #007AFF;"><td colspan="22" style="border:none;">&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; <span>The system facing the following errors in database '||v_db_name||', Kindly take necessary action.</span></td></tr></table>';
		   
			
			v_data= v_table_heading ;
			
			v_data=v_data || '<table id="customers"></table><table id="customers">
			
			<tr>
                <th colspan="2"><b><center>S.No</center></b></th>
                <th colspan="2"><b><center>Log Date</center></b></th>
                <th colspan="2"><b><center>Error Message</center></b></th>
			</tr>';
			
			Open cursor_temp FOR
			
			select to_char(create_date,'dd/mm/yyyy HH:MM:SS') as create_date,message from ir_logging 
            where level = 'ERROR' and create_date::date = Now()::date;			
			
			LOOP                 
		  		FETCH cursor_temp INTO v_log_date,v_error_message;

				IF NOT FOUND then 
		    		Exit;
		   		end if; 

			if(v_log_date is null) then
				v_log_date='';
			end if;
			
			if(v_error_message is null) then
				v_error_message='';
			end if;
					
			
			
			v_data=v_data ||
				'<tr>
				<td colspan="2"><center>'||v_sl_no||'</center></td>
                <td colspan="2"><center>'||v_log_date||'</center></td>
				<td colspan="2">'||v_error_message||'</td>
				</tr>';
				
			
			
			
	v_sl_no = v_sl_no+1;
	END LOOP;
		Close cursor_temp;
			
			v_data=v_data || '</table>
                                
                <br>
                <br>

            <table id="customers">
			<table width="100%" border="0" cellspacing="0" cellpadding="0">
			<tr>
			<td>
				  <table width="100%" cellpadding="0" cellspacing="0" border="0" bgcolor="#029EFC">
			<tr>
			<td height="2" align="center" bgcolor="#029EFC" class="one-column"></td>
			</tr>
			<tr>
			<td align="center" bgcolor="#029EFC" class="one-column" style="padding-top:0;padding-bottom:5px;padding-right:10px;padding-left:10px;"><font style="font-size:13px; text-decoration:none; color:white; font-family: Times New Roman; text-align:right;"> ** This mail is auto generated by ERP System </font></td>
			</tr>
			</table>
			</td>
			</tr>
			<tr>
			<td>
			<table width="100%" cellpadding="0" cellspacing="0" border="0">
			<tr>
			<td>&nbsp;</td>
			</tr>
			</table>
			</td>
			</tr>
			</table>
			</td>
			</tr>
			</table>
			</div>
			</td>
			</tr>
			</table>
			</center>
			</body>
			</html>';
				
        RETURN v_data;
END;

$BODY$;

ALTER FUNCTION public.auto_logger_mail()
    OWNER TO odoo;

