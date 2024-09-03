/** @odoo-module **/

import { _t } from "@web/core/l10n/translation";
import { browser } from "@web/core/browser/browser";
import { ConnectionLostError } from "@web/core/network/rpc_service";
import { registry } from "@web/core/registry";

export const CustomNotificationService = {
    dependencies: ["action", "bus_service", "custom_notification", "rpc"],

    start(env, { action, bus_service, custom_notification, rpc }) {
        let CustomNotifTimeouts = {};
        const displayedNotifications = new Set();

        bus_service.subscribe("custom.notification", (payload) => {
            displayCustomNotification(payload);
        });
        bus_service.start();

        function displayCustomNotification(notifications) {
            notifications.forEach(function (notif) {
                const key = `${notif.user_id}_${notif.notify_name}`;
                if (displayedNotifications.has(key)) {
                    return;
                }

                const notificationRemove = custom_notification.add(notif.message, {
                    title: notif.title,
                    type: notif.close === "yes" ? "info" : "danger",
                    sticky: true,
                    onClose: () => {
                        displayedNotifications.delete(key);
                        if (CustomNotifTimeouts[key]) {
                            browser.clearTimeout(CustomNotifTimeouts[key]);
                        }
                    },
                    buttons: [
                        // {
                        //     name: _t("OK"),
                        //     primary: true,
                        //     onClick: async () => {
                        //         //await rpc("/ct_transaction/notify_ack");
                        //         notificationRemove();
                        //     },
                        // },
                        //~ {
                            //~ name: _t("Details"),
                            //~ onClick: async () => {
                                //~ await action.doAction({
                                    //~ type: 'ir.actions.act_window',
                                    //~ res_model: 'ct.transaction',
                                    //~ res_id: notif.event_id,
                                    //~ views: [[false, 'form']],
                                //~ });
                                //~ notificationRemove();
                            //~ },
                        //~ },
                        //~ {
                            //~ name: _t("Snooze"),
                            //~ onClick: () => {
                                //~ notificationRemove();
                            //~ },
                        //~ },
                        {
                            name: _t("Stop Today"),
                            onClick: async () => {
                                await rpc("/custom/popup/disable", {
                                    user_id: notif.user_id,
                                    notify_name: notif.notify_name,
                                });
                                notificationRemove();
                            },
                        },
                    ],
                });

                if (notif.close === 'yes') {
                    CustomNotifTimeouts[key] = browser.setTimeout(() => {
                        notificationRemove();
                        }, 10000); // 600,000 milliseconds = 10 minutes
                }

                displayedNotifications.add(key);
            });
        }

        //~ async function getNextCtTransactionNotif() {
            //~ try {
                //~ const result = await rpc("/ct_transaction/notify", {}, { silent: true });
                //~ displayCtTransactionNotification(result);
            //~ } catch (error) {
                //~ if (!(error instanceof ConnectionLostError)) {
                    //~ throw error;
                //~ }
            //~ }
        //~ }
    },
};

registry.category("services").add("CustomNotification", CustomNotificationService);
