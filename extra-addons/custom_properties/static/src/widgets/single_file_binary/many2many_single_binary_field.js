/** @odoo-module **/

import { _t } from "@web/core/l10n/translation";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { standardFieldProps } from "@web/views/fields/standard_field_props";
import { FileInput } from "@web/core/file_input/file_input";
import { useX2ManyCrud } from "@web/views/fields/relational_utils";

import { Component } from "@odoo/owl";

export class SingleFileBinaryField extends Component {
    static template = "web.SingleFileBinaryField";
    static components = {
        FileInput,
    };
    static props = {
        ...standardFieldProps,
        acceptedFileExtensions: { type: String, optional: true },
        className: { type: String, optional: true },
    };

    setup() {
        this.orm = useService("orm");
        this.notification = useService("notification");
        this.operations = useX2ManyCrud(() => this.props.record.data[this.props.name], true);
    }

    get uploadText() {
        return this.props.record.fields[this.props.name].string;
    }

    get files() {
        const records = this.props.record.data[this.props.name].records;
        return records.length ? [{
            ...records[0].data,
            id: records[0].resId,
        }] : [];
    }

    getUrl(id) {
        return "/web/content/" + id + "?download=true";
    }

    getExtension(file) {
        return file.name.replace(/^.*\./, "");
    }

    async onFileUploaded(files) {
        const existingFiles = this.files;
        if (existingFiles.length > 0) {
            this.notification.add(_t("Only one file can be uploaded."), {
                title: _t("Uploading error"),
                type: "danger",
            });
            return;
        }
        
        for (const file of files) {
            if (file.error) {
                return this.notification.add(file.error, {
                    title: _t("Uploading error"),
                    type: "danger",
                });
            }

            // File size validation
            if (file.size === 0) {
                this.notification.add(_t("Empty file(0 bytes) should not allowed"), {
                    title: _t("Uploading error"),
                    type: "danger",
                });
                return;
            }

            await this.operations.saveRecord([file.id]);
        }
    }

    async onFileRemove(deleteId) {
        const record = this.props.record.data[this.props.name].records.find(
            (record) => record.resId === deleteId
        );
        this.operations.removeRecord(record);
    }
}

export const singleFileBinaryField = {
    component: SingleFileBinaryField,
    supportedOptions: [
        {
            label: _t("Accepted file extensions"),
            name: "accepted_file_extensions",
            type: "string",
        },
    ],
    supportedTypes: ["many2many"],
    isEmpty: () => false,
    relatedFields: [
        { name: "name", type: "char" },
        { name: "mimetype", type: "char" },
    ],
    extractProps: ({ attrs, options }) => ({
        acceptedFileExtensions: options.accepted_file_extensions,
        className: attrs.class,
    }),
};

registry.category("fields").add("single_file_binary", singleFileBinaryField);
