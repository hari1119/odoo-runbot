/** @odoo-module **/

import { registry } from "@web/core/registry";
import { listView } from "@web/views/list/list_view";
import { ListRenderer } from "@web/views/list/list_renderer";
import { CpMailConfigurationDashBoard } from '@custom_properties/views/list_view_dashboard/cp_mail_configuration_dashboard';

export class CpMailConfigurationDashBoardRenderer extends ListRenderer {};

CpMailConfigurationDashBoardRenderer.template = 'custom_properties.CpMailConfigurationListView';
CpMailConfigurationDashBoardRenderer.components= Object.assign({}, ListRenderer.components, {CpMailConfigurationDashBoard})

export const CpMailConfigurationListView = {
    ...listView,
    Renderer: CpMailConfigurationDashBoardRenderer,
};

registry.category("views").add("cp_mail_configuration_list", CpMailConfigurationListView);
