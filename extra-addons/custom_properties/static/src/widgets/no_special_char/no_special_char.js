/** @odoo-module **/

import { registry } from "@web/core/registry";
import { _t } from "@web/core/l10n/translation";
import { useInputField } from "@web/views/fields/input_field_hook";
import { standardFieldProps } from "@web/views/fields/standard_field_props";
import { useService } from "@web/core/utils/hooks";
import { Component, onWillStart, useState } from "@odoo/owl";

export class NoSpecialCharField extends Component {
    static template = "cml_no_special_char_widget.NoSpecialCharField";
    static props = {
        ...standardFieldProps,
        placeholder: { type: String, optional: true },
    };

    // Initial setup
    setup() {
        useInputField({ getValue: () => this.props.record.data[this.props.name] || "" });
        this.orm = useService("orm");
        this.allowedSpecialChars = '';
        this.fetchAllowedSpecialChars();
        
        // Bind methods to ensure correct context
        this.validateSpecialChar = this.validateSpecialChar.bind(this);
        this.handlePaste = this.handlePaste.bind(this);
        
        // State to manage error message visibility
        this.state = useState({
            errorMessage: '',
            showError: false,
        });
        
    }
    
    // Fetch allowed characters from res.config
    async fetchAllowedSpecialChars() {
        try {
            this.allowedSpecialChars = await this.orm.call("custom.properties", "retrieve_allowed_char");
            this.render();
        } catch (error) {
            console.error('Error fetching allowed special characters:', error);
        }
    }
    
    // Validate alphanumeric input
    validateSpecialChar(event) {
        const allowedCharsRegex = this.constructAllowedCharsRegex();
        var charCode = event.charCode;
        if (!allowedCharsRegex.test(String.fromCharCode(charCode)) && !event.ctrlKey && !event.metaKey) {
            event.preventDefault();
            this.showErrorMessage('Special characters not allowed.'); // Show error message
        }
    }
    
    // Construct allowed characters regex
    constructAllowedCharsRegex() {
        let allowedChars = /[a-zA-Z0-9]/;
        if (this.allowedSpecialChars) {
            allowedChars = new RegExp(`[${this.allowedSpecialChars}\\w]`);
        }
        return allowedChars;
    }
    
    // Handle paste event
    handlePaste(event) {
        event.preventDefault();
        const paste = (event.clipboardData || window.clipboardData).getData('text');
        
        const allowedCharsRegex = this.constructAllowedCharsRegex();
        // Construct regex to match allowed characters
        const allowedRegex = new RegExp(`[^a-zA-Z0-9${this.allowedSpecialChars}]`, 'g');
        const alphanumericPaste = paste.replace(allowedRegex, '');
        
        //document.execCommand('insertText', false, alphanumericPaste);
        
        // Check if the pasted content contains invalid characters
        if (allowedRegex.test(paste)) {
            document.execCommand('insertText', false, alphanumericPaste);
            this.showErrorMessage('Special characters not allowed.'); // Show error message
        } else {
            document.execCommand('insertText', false, alphanumericPaste);
        }
        
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
    

    // Get max length for input
    get maxLength() {
        return this.props.record.fields[this.props.name].size;
    }
}

// Define Odoo field registration
export const nospecialcharField = {
    component: NoSpecialCharField,
    displayName: _t("NoSpecialChar"),
    supportedTypes: ["char","text"],
    extractProps: ({ attrs }) => ({
        placeholder: attrs.placeholder,
    }),
};

// Register field in Odoo registry
registry.category("fields").add("no_special_char", nospecialcharField);
