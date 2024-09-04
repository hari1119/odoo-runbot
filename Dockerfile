FROM odoo:17.0

ENV ADDON_PATH=/opt/cm_addons

COPY odoo.conf /etc/odoo/odoo.conf
COPY extra-addons/fields_databank ${ADDON_PATH}/fields_databank/
COPY extra-addons/custom_properties ${ADDON_PATH}/custom_properties/


COPY requirements.txt requirements.txt

CMD ["odoo", "-d", "odoo", "--log-db=all"]
