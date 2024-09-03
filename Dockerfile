FROM odoo:17.0

ENV ADDON_PATH=/opt/cm_addons

COPY odoo.conf /etc/odoo/odoo.conf
COPY cm_addons/fields_databank ${ADDON_PATH}/fields_databank/
COPY cm_addons/custom_properties ${ADDON_PATH}/custom_properties/
COPY cm_addons/ct_transaction ${ADDON_PATH}/ct_transaction/
COPY cm_addons/cm_master ${ADDON_PATH}/cm_master/
COPY cm_addons/cm_profile_master ${ADDON_PATH}/cm_profile_master/
COPY cm_addons/cm_login_page ${ADDON_PATH}/cm_login_page/
COPY cm_addons/cm_user_mgmt ${ADDON_PATH}/cm_user_mgmt/
COPY cm_addons/sh_message ${ADDON_PATH}/sh_message/
COPY cm_addons/cm_fiscal_year ${ADDON_PATH}/cm_fiscal_year/
COPY cm_addons/cr_report ${ADDON_PATH}/cr_report/
COPY cm_addons/cm_survey ${ADDON_PATH}/cm_survey/
COPY cm_addons/auditlog ${ADDON_PATH}/auditlog/
COPY cm_addons/cm_base_inherit ${ADDON_PATH}/cm_base_inherit/
COPY cm_addons/v_assistant ${ADDON_PATH}/v_assistant/

COPY requirements.txt requirements.txt
RUN apt-get update && apt-get install -y python3-pip && pip3 install --no-cache-dir -r requirements.txt

CMD ["odoo", "-d", "odoo", "--log-db=all"]
