/** @odoo-module **/

import { browser } from "@web/core/browser/browser";
import { registry } from "@web/core/registry";
import { CustomNotificationContainer } from "./custom_notification_container";

import { reactive } from "@odoo/owl";

const AUTOCLOSE_DELAY = 4000;

export const customNotificationService = {
    notificationContainer: CustomNotificationContainer,

    start() {
        let notifId = 0;
        const notifications = reactive({});

        registry.category("main_components").add(
            this.notificationContainer.name,
            {
                Component: this.notificationContainer,
                props: { notifications },
            },
            { sequence: 100 }
        );

        function add(message, options = {}) {
            const id = ++notifId;
            const closeFn = () => close(id);
            const props = Object.assign({}, options, { message, close: closeFn });
            const sticky = props.sticky;
            delete props.sticky;
            delete props.onClose;
            let closeTimeout;
            const refresh = sticky
                ? () => {}
                : () => {
                      closeTimeout = browser.setTimeout(closeFn, AUTOCLOSE_DELAY);
                  };
            const freeze = sticky
                ? () => {}
                : () => {
                      browser.clearTimeout(closeTimeout);
                  };
            props.refresh = refreshAll;
            props.freeze = freezeAll;
            const notification = {
                id,
                props,
                onClose: options.onClose,
                refresh,
                freeze,
            };
            notifications[id] = notification;
            if (!sticky) {
                closeTimeout = browser.setTimeout(closeFn, AUTOCLOSE_DELAY);
            }
            return closeFn;
        }

        function refreshAll() {
            for (const id in notifications) {
                notifications[id].refresh();
            }
        }

        function freezeAll() {
            for (const id in notifications) {
                notifications[id].freeze();
            }
        }

        function close(id) {
            if (notifications[id]) {
                const notification = notifications[id];
                if (notification.onClose) {
                    notification.onClose();
                }
                delete notifications[id];
            }
        }

        return { add };
    },
};

registry.category("services").add("custom_notification", customNotificationService);
