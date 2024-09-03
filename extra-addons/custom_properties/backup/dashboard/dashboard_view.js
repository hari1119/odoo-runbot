/** @odoo-module */

import { registry } from "@web/core/registry";
import { DashBoardController} from "./dashboard_controller"

const DashboardView = {
    type: "dashboard",
    display_name: "Dash Board",
    icon: "fa fa-desktop",
    multiRecord: true,
    Controller: DashBoardController,
}

registry.category("views").add("dashboard", DashboardView);

