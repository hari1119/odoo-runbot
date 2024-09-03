/** @odoo-module **/
import { _t } from "@web/core/l10n/translation";
import { registry } from "@web/core/registry";
import { patch } from "@web/core/utils/patch";
import { FileInput } from "@web/core/file_input/file_input";
import { checkFileSize } from "@web/core/utils/files";

patch(FileInput.prototype, {
    async uploadFiles(params) {
        try {
            if ((params.ufile && params.ufile.length) || params.file) {
                const file = params.ufile && params.ufile[0] ? params.ufile[0] : params.file;
                if (file) {
                    const fileSize = file.size;
                    if (!checkFileSize(fileSize, this.notification)) {
                        return null;
                    }
                } else {
                    this.notification.add(_t("Invalid file."), {
                        title: _t("Uploading error"),
                        type: "danger",
                    });
                    return null;
                }
            }

            const fileData = await this.http.post(this.props.route, params, "text");
            const parsedFileData = JSON.parse(fileData);

            if (parsedFileData.error) {
                throw new Error(parsedFileData.error);
            }

            return parsedFileData;
        } catch (error) {
            console.error("Error in uploadFiles:", error);
            this.notification.add(_t("An error occurred during file upload."), {
                title: _t("Uploading error"),
                type: "danger",
            });
            return null;
        }
    }
});
