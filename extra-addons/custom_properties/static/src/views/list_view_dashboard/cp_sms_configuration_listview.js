/** @odoo-module **/

import { registry } from "@web/core/registry";
import { listView } from "@web/views/list/list_view";
import { ListRenderer } from "@web/views/list/list_renderer";
import { CpSmsConfigurationDashBoard } from '@custom_properties/views/list_view_dashboard/cp_sms_configuration_dashboard';

export class CpSmsConfigurationDashBoardRenderer extends ListRenderer {};

CpSmsConfigurationDashBoardRenderer.template = 'custom_properties.CpSmsConfigurationListView';
CpSmsConfigurationDashBoardRenderer.components= Object.assign({}, ListRenderer.components, {CpSmsConfigurationDashBoard})

export const CpSmsConfigurationListView = {
    ...listView,
    Renderer: CpSmsConfigurationDashBoardRenderer,
};

registry.category("views").add("cp_sms_configuration_list", CpSmsConfigurationListView);
