/** @odoo-module */

import { registry } from "@web/core/registry";
import { FieldstrackerController } from "./fields_tracker"

const FieldstrackerView = {
    type: "fields_tracker",
    display_name: "Fields Tracker",
    icon: "fa fa-desktop",
    multiRecord: true,
    Controller: FieldstrackerController,
}

registry.category("views").add("fields_tracker", FieldstrackerView);

