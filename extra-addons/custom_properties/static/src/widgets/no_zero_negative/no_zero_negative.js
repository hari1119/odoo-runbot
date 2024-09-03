/** @odoo-module **/

import { registry } from "@web/core/registry";
import { _t } from "@web/core/l10n/translation";
import { useInputField } from "@web/views/fields/input_field_hook";
import { standardFieldProps } from "@web/views/fields/standard_field_props";
import { useService } from "@web/core/utils/hooks";
import { Component, useState } from "@odoo/owl";

export class NoZeroNegativeField extends Component {
    static template = "cml_no_zero_negative_field_widget.NoZeroNegativeField";
    static props = {
        ...standardFieldProps,
        placeholder: { type: String, optional: true },
    };

    setup() {
        this.state = useState({
            errorMessage: '',
            showError: false,
        });

        this.inputRef = useInputField({
            getValue: () => this.formattedValue,
            parse: (v) => this.parse(v),
        });

        // Bind methods to ensure correct context
        this.validatenumeric = this.validatenumeric.bind(this);
        this.handlePaste = this.handlePaste.bind(this);
    }

    // Validate numeric input on keypress
    validatenumeric(event) {
        const inputElement = event.target;
        const charCode = event.charCode;
        const charStr = String.fromCharCode(charCode);

        let newvalue = inputElement.value;
        const numericValue = parseFloat(newvalue);
        if (numericValue < 0) {
            event.preventDefault();
            this.showErrorMessage('Value should be greater than or equal to zero.');
            inputElement.value = '0.000'; // Reset the input field to 0.000
        }

        // Allow only numbers, decimal point, and control characters
        if (!charStr.match(/[0-9.]/) && !event.ctrlKey && !event.metaKey) {
            event.preventDefault();
            return;
        }

        // Prevent entering a second decimal point
        if (charStr === '.' && event.target.value.includes('.')) {
            event.preventDefault();
            return;
        }

        // Prevent entering negative values
        if (charStr === '-') {
            event.preventDefault();
            return;
        }
    }

    // Handle paste event
    handlePaste(event) {
        event.preventDefault();
        const paste = (event.clipboardData || window.clipboardData).getData('text');
        let numericValue = parseFloat(paste);

        // Check if the pasted content is strictly a valid number and greater than or equal to zero
        if (isNaN(numericValue) || numericValue < 0) {
            this.showErrorMessage('Value should be greater than or equal to zero.');
        } else {
            numericValue = this.roundToThreeDecimals(numericValue);
            document.execCommand('insertText', false, numericValue.toFixed(3));
        }
    }

    // Round a number to three decimal places
    roundToThreeDecimals(value) {
        return Math.round(value * 1000) / 1000;
    }

    // Show error message and set timer to hide it
    showErrorMessage(message) {
        this.state.errorMessage = message;
        this.state.showError = true;
        setTimeout(() => {
            this.state.showError = false;
            this.render();
        }, 7000); // 7 seconds
    }

    parse(value) {
        return this.roundToThreeDecimals(parseFloat(value));
    }

    get formattedValue() {
        return this.value ? this.value.toFixed(3) : '0.000';
    }

    get value() {
        return this.props.record.data[this.props.name];
    }
}

// Define Odoo field registration
export const nozeronegativeField = {
    component: NoZeroNegativeField,
    displayName: _t("NoZeroNegative"),
    supportedTypes: ["float", "int"],
    extractProps: ({ attrs }) => ({
        placeholder: attrs.placeholder,
    }),
};

// Register field in Odoo registry
registry.category("fields").add("no_zero_negative", nozeronegativeField);
