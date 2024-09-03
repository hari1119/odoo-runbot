/** @odoo-module */

import { Component } from "@odoo/owl";
import { standardViewProps } from "@web/views/standard_view_props"
import { DashboardItem } from "./dashboard_item/dashboard_item";
import { Layout } from "@web/search/layout"

export class DashBoardController extends Component {
    static template = 'custom_properties.DashboardView';
    static components = { DashboardItem, Layout }
    static props = {
        ...standardViewProps,
    }

}

