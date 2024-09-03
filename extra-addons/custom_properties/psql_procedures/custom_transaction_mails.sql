-- FUNCTION: public.custom_transaction_mails(integer, character, character, character)

-- DROP FUNCTION IF EXISTS public.custom_transaction_mails(integer, character, character, character);

CREATE OR REPLACE FUNCTION public.custom_transaction_mails(
	v_trans_id integer,
	v_trans_state character,
	v_ref_no character,
	v_user_name character)
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
v_draft_name char varying(10000);
v_trans_name char varying(10000);
v_entry_date char varying (10000);
v_division char varying(10000);
v_department char varying(10000);
v_created_by char varying(10000);
v_confirmed_by char varying(10000);
v_approved_by char varying(10000);
v_supplier char varying(10000);

--Line fields
v_sl_no integer;
v_description char varying(10000);
v_brand char varying(10000);
v_uom char varying(10000);
v_qty char varying(10000);
v_unitprice char varying(10000);
v_disc_amt char varying(10000);
v_tax_amt char varying(10000);
v_line_tot_amt float;
v_net_amt float;

BEGIN

v_table_heading='';
v_data='';
v_sl_no =1;

			v_table_heading='<html ><head>
			<style type="text/css">
			* {-webkit-font-smoothing: antialiased;}
			body {Margin: 0;padding: 0;min-width: 100%;font-family: "Times New Roman", Times, serif;-webkit-font-smoothing: antialiased;mso-line-height-rule: exactly;}
			table {border-spacing: 0;color: #333333;font-family:"Times New Roman", Times, serif;}
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
			#customers,#customers-campus,#customers-nohover {font-family: "Times New Roman", Times, serif;border-collapse: collapse;width: 100%;background: #ffffff;}
			#customers tbody,#customers-campus tbody,#customers-nohover tbody {width: 80%;}
			#customers-nohover th {padding: 8px;background: #fff;}
			#customers td,#customers th,#customers-campus td,#customers-campus th {border-left: 1px solid #2f9780;border-right: 1px solid #2f9780;border-top: 1px solid #2f9780;padding: 8px;border-bottom: 1px solid #2f9780;padding: 8px;}
			#customers th,#customers-campus th {font-weight: normal;}
			#customers tr:nth-child(even) {background-color: #f2f2f2;}
			#customers tr:hover {background-color: #ddd;}
			#customers tr th:hover {background-color: none!important;}
			#customers tbody tr th:hover {background-color: none!important;}
			#customers th,#customers-campus th {text-align: left;padding: 8px;}
			.green {background: #ddd;}
			</style></head>';
			
			
			v_table_heading= v_table_heading || '<body style="Margin:0;padding-top:0;padding-bottom:0;padding-right:0;padding-left:0;min-width:100%;background-color:#ececec;">
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
			<td style="width:100%; border-top-left-radius:10px; border-top-right-radius:10px" height="6" bgcolor="#2f9780" class="contents">
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
			<table class="one-column" border="0" cellpadding="0" cellspacing="0" width="100%" style="border-spacing:0" bgcolor="#2f9780">
			<tr>
			<td align="left" style="padding-left:10px; padding-right:20px; padding-top:0px; padding-bottom:10px">
			</td>
			</tr>';
			
			Open cursor_temp FOR
			
			select trans.name_draft,trans.name,to_char(trans.entry_date,'dd/mm/yyyy') as entry_date,div.name as Division,
			dep.name as department,supplier.name,partner.name,con_name.name,ap_name.name,trans.net_amt from  ct_transaction trans
			left join cm_master div on div.id = trans.division_id
			left join cm_master dep on dep.id = trans.department_id
			left join res_partner supplier on supplier.id = trans.partner_id
			left join res_users users on users.id = trans.user_id
			left join res_users ap_user on ap_user.id = trans.ap_rej_user_id
			left join res_users confirm_user on confirm_user.id = trans.confirm_user_id
			left join res_partner partner on partner.id = users.partner_id
			left join res_partner con_name on con_name.id = confirm_user.partner_id
			left join res_partner ap_name on ap_name.id = ap_user.partner_id
			where trans.id = v_trans_id ;			
			
			LOOP                 
		  		FETCH cursor_temp INTO v_draft_name,v_trans_name,v_entry_date,v_division,v_department,v_supplier,v_created_by,v_confirmed_by,v_approved_by,v_net_amt;

				IF NOT FOUND then 
		    		Exit;
		   		end if; 

			if(v_trans_name is null) then
				v_trans_name='';
			end if;
			if(v_draft_name is null) then
				v_draft_name='';
			end if;
			
			if(v_entry_date is null) then
				v_entry_date='';
			end if;
			
			if(v_division is null) then
				v_division='';
			end if;
			
			if(v_department is null) then
				v_department='';
			end if;

			if(v_supplier is null) then
				v_supplier='';
			end if;

			if(v_created_by is null) then
				v_created_by='';
			end if;

			if(v_confirmed_by is null) then
				v_confirmed_by=v_user_name;
			end if;
			if(v_approved_by is null) then
				v_approved_by=v_user_name;
			end if;
			if(v_net_amt is null) then
				v_net_amt=0;
			end if;
			
			v_table_heading= v_table_heading || '<table id="customers" style="border:none;">
				<tr style="border:1px solid #2f9780;"><td colspan="2" style="border:none;"><b style="margin-top: 15px;">Dear Sir / Mam</b>,</td></tr>';
				
           if(v_trans_state = 'wfa') then
				v_table_heading= v_table_heading || '<tr style="border-left:1px solid #2f9780;border-right:1px solid #2f9780;"><td colspan="2" style="border:none;">&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; <span>The <b>'||v_ref_no||'</b> is required your approval, It has been created by '||v_created_by||'.</span></td></tr>
				</table>';
		   elseif (v_trans_state = 'approved') then
			    v_table_heading= v_table_heading || '<tr style="border-left:1px solid #2f9780;border-right:1px solid #2f9780;"><td colspan="2" style="border:none;">&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; <span>The <b>'||v_ref_no||'</b> has been approved.</span></td></tr>
				</table>';
		   else 
		       v_table_heading= v_table_heading || '<tr style="border-left:1px solid #2f9780;border-right:1px solid #2f9780;"><td colspan="2" style="border:none;">&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; <span>The detailsd of <b>'||v_ref_no||'</b> below, It has been created by '||v_created_by||'.</span></td></tr>
				</table>';
		      end if;
			
			v_data= v_table_heading ;
			
			
			v_data=v_data || '<table id="customers">
			<th colspan="18" scope="colgroup" class="table-heading green"><b>Transaction Info:</b></th>';
			
		if (v_trans_state != 'approved') then
		    
		     v_data=v_data || '<tr>
			<td colspan="3">Transaction Draft No</td>
			<td colspan="3">'||v_ref_no||'</td>
			</tr>';
		else
		    v_data=v_data || '<tr>
			<td colspan="3">Transaction No</td>
			<td colspan="3">'||v_ref_no||'</td>
			</tr>';
	   end if;
			
			v_data=v_data || '<tr>
			<td colspan="3">Transaction Date</td>
			<td colspan="3">'||v_entry_date||'</td>
			</tr>
		
			<tr>
			<td colspan="3">Division</td>
			<td colspan="3">'||v_division||'</td>
			</tr>
			
			<tr>
			<td colspan="3">Department</td>
			<td colspan="3">'||v_department||'</td>
			</tr>
			
			<tr>
			<td colspan="3">Partner</td>
			<td colspan="3">'||v_supplier||'</td>
			</tr>
			
			<tr>
			<td colspan="3">Created By</td>
			<td colspan="3">'||v_created_by||'</td>
			</tr>
			
			<tr>
			<td colspan="3">Confirmed By</td>
			<td colspan="3">'||v_confirmed_by||'</td>
			</tr>';
			
		if (v_trans_state = 'approved') then
		    
		   v_data=v_data || '<tr>
			<td colspan="3"><b>Approved By</b></td>
			<td colspan="3"><b>'||v_user_name||'</b></td>
			</tr>';

		end if;
			
			v_data=v_data || '</table><table id="customers">
			<th colspan="18" scope="colgroup" class="table-heading green"><b>Line Details:</b></th>

			<tr>
                <th colspan="2"><b><center>S.No</center></b></th>
                <th colspan="2"><b><center>Description</center></b></th>
                <th colspan="2"><b><center>Brand</center></b></th>
                <th colspan="2"><b><center>UOM</center></b></th>
                <th colspan="2"><b><center>Qty</center></b></th>
                <th colspan="2"><b><center>Unit Price</center></b></th>
                <th colspan="2"><b><center>Discount</center></b></th>
                <th colspan="2"><b><center>Tax</center></b></th>
                <th colspan="2"><b><center>Total(<font style="font-size:13px;">WT</font>)</center></b></th>
			</tr>';
			
			
			
			Open cursor_temp123 FOR
            
            select line.description,brand.name,uom.name->>'en_US',round(line.qty::numeric,3) as qty,
			trim(TO_CHAR((line.unit_price::numeric)::float, '99G99G99G99G99G99G990D99')) as unit_price,
			trim(TO_CHAR((line.disc_amt::numeric)::float, '99G99G99G99G99G99G990D99')) as disc_amt,
			trim(TO_CHAR((line.tax_amt::numeric)::float, '99G99G99G99G99G99G990D99')) as tax_amt,
			line.line_tot_amt::numeric as line_tot_amt
			from ct_transaction_line line
			left join uom_uom uom on uom.id = line.uom_id
			left join cm_master brand on brand.id = line.brand_id
			where line.header_id = v_trans_id;
            LOOP                 
                  FETCH cursor_temp123 INTO v_description,v_brand,v_uom,v_qty,v_unitprice,v_disc_amt,v_tax_amt,v_line_tot_amt;

               IF NOT FOUND then
                    Exit;
                   end if;
            if(v_description is null) then
                v_description='';
            end if;
            
            if(v_brand is null) then
                v_brand='';
            end if;
            
            if(v_uom is null) then
                v_uom='';
            end if;
			
			if(v_qty is null) then
                v_qty='';
            end if;
			
			if(v_unitprice is null) then
                v_unitprice='';
            end if;
			
			if(v_disc_amt is null) then
                v_disc_amt='';
            end if;
			
			if(v_tax_amt is null) then
                v_tax_amt='';
            end if;
			
			if(v_line_tot_amt is null) then
                v_line_tot_amt='';
            end if;
           
				v_data=v_data ||
				'<tr>
                <td colspan="2"><center>'||v_sl_no||'</center></td>
                <td colspan="2">'||v_description||'</td>
                <td colspan="2">'||v_brand||'</td>
                <td colspan="2">'||v_uom||'</td>
                <td colspan="2" align="right">'||v_qty||'</td>
                <td colspan="2" align="right">'||v_unitprice||'</td>
                <td colspan="2" align="right">'||v_disc_amt||'</td>
                <td colspan="2" align="right">'||v_tax_amt||'</td>
                <td colspan="2" align="right">'||trim(TO_CHAR((v_line_tot_amt::numeric)::float, '99G99G99G99G99G99G990D99'))||'</td>
                </tr>';
			--v_net_amt = v_net_amt + v_line_tot_amt;
			v_sl_no = v_sl_no+1;
			END LOOP;
            Close cursor_temp123;
			
			
			v_data=v_data || '<tr>
                <td colspan="16" align="right"><b>Net Amount (<font style="font-size:13px;">INR</font>):</b></td>
                <td colspan="2" align="right"><b>'||trim(TO_CHAR((v_net_amt::numeric)::float, '99G99G99G99G99G99G990D99'))||'</b></td>
            </tr>';
			
			v_data=v_data || '</table>
                                
                <br>
                <br>

            <table id="customers">
			<table width="100%" border="0" cellspacing="0" cellpadding="0">
			<tr>
			<td>
				  <table width="100%" cellpadding="0" cellspacing="0" border="0" bgcolor="#2f9780">
			<tr>
			<td height="2" align="center" bgcolor="#2f9780" class="one-column"></td>
			</tr>
			<tr>
			<td align="center" bgcolor="#2f9780" class="one-column" style="padding-top:0;padding-bottom:5px;padding-right:10px;padding-left:10px;"><font style="font-size:13px; text-decoration:none; color:#ffffff; font-family: Times New Roman; text-align:right;"> ** This mail is auto generated by ERP System </font></td>
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
	
	END LOOP;
		Close cursor_temp;
				
	RETURN v_data;

END;

$BODY$;

ALTER FUNCTION public.custom_transaction_mails(integer, character, character, character)
    OWNER TO odoo;

