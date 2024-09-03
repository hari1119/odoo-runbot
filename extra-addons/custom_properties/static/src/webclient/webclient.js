/** @odoo-module */

import { patch } from '@web/core/utils/patch';

import { WebClient } from '@web/webclient/webclient';
import { AppsBar } from '@custom_properties/webclient/appsbar/appsbar';

patch(WebClient, {
    components: {
        ...WebClient.components,
        AppsBar,
    },
});
