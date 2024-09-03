/** @odoo-module **/

import { CustomNotification } from "./custom_notification";
import { Transition } from "@web/core/transition";

import { Component, xml, useState } from "@odoo/owl";

export class CustomNotificationContainer extends Component {
    setup() {
        this.notifications = useState(this.props.notifications);
    }
}
CustomNotificationContainer.props = {
    notifications: Object,
};

CustomNotificationContainer.template = xml`
    <div class="o_custom_notification_manager">
        <t t-foreach="notifications" t-as="notification" t-key="notification">
            <Transition leaveDuration="0" name="'o_custom_notification_fade'" t-slot-scope="transition">
                <CustomNotification t-props="notification_value.props" className="(notification_value.props.className || '') + ' ' + transition.className"/>
            </Transition>
        </t>
    </div>`;
CustomNotificationContainer.components = { CustomNotification, Transition };
