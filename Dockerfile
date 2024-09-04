FROM odoo:17.0

ENV ADDON_PATH=/opt/cm_addons

COPY odoo.conf /etc/odoo/odoo.conf
COPY cm_addons/fields_databank ${ADDON_PATH}/fields_databank/
COPY cm_addons/custom_properties ${ADDON_PATH}/custom_properties/


COPY requirements.txt requirements.txt
RUN apt-get update && apt-get install -y python3-pip && pip3 install --no-cache-dir -r requirements.txt

CMD ["odoo", "-d", "odoo", "--log-db=all"]
