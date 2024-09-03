/* @odoo-module */

import {ListRenderer} from "@web/views/list/list_renderer";
import {patch} from "@web/core/utils/patch";
const DEFAULT_GROUP_PAGER_COLSPAN = 1;
patch(ListRenderer.prototype, {
    freezeColumnWidths() {
        const table = this.tableRef.el;
        const child_table = table.firstElementChild.firstElementChild;

	// Check if the "S.No" column is already present
	if (!$(child_table).find('.o_list_row_count_sheliya').length) {
	    // Find the index of the multiple select checkbox column
	    const selectCheckboxIndex = $(child_table).find('th').index($(child_table).find('.o_list_record_selector').closest('th'));

	    if (selectCheckboxIndex !== -1) {
		// Insert the "S.No" column after the multiple select checkbox column
		const newColumn = '<th class="o_list_row_number_header o_list_row_count_sheliya" style="width: 6% !important;">S.No</th>';
		$(child_table).find('th').eq(selectCheckboxIndex).after(newColumn);

		// Insert the "Pin" column after the "S.No" column
		

		/*const snColumnIndex = $(child_table).find('th').index($(child_table).find('.o_list_row_count_sheliya'));
		const pinColumn = '<th class="o_list_row_header o_list_row_pin">Pin</th>';
		$(child_table).find('th').eq(snColumnIndex).after(pinColumn);*/

	    } else {
		// Append the "S.No" column at the end if the checkbox column is not found
		const newColumn = '<th class="o_list_row_number_header o_list_row_count_sheliya" tabindex="-1" style="width: 6% !important;">S.No</th>';
		$(child_table).prepend(newColumn);
	    }
	}


        
        return super.freezeColumnWidths();
    },
    
    
    // Below code for S.No width adjustment in one2many list.
    
    setDefaultColumnWidths() {
        const widths = this.state.columns.map((col) => this.calculateColumnWidth(col));
        const sumOfRelativeWidths = widths
            .filter(({ type }) => type === "relative")
            .reduce((sum, { value }) => sum + value, 0);

        // 1 because nth-child selectors are 1-indexed, 2 when the first column contains
        // the checkboxes to select records.
        const columnOffset = this.hasSelectors ? 2 : 1;
        widths.forEach(({ type, value }, i) => {
            const headerEl = this.tableRef.el.querySelector(`th:nth-child(${i+1 + columnOffset})`);
            if (type === "absolute") {
                if (this.isEmpty) {
                    headerEl.style.width = value;
                } else {
                    headerEl.style.minWidth = value;
                }
            } else if (type === "relative" && this.isEmpty) {
                headerEl.style.width = `${((value / sumOfRelativeWidths) * 100).toFixed(2)}%`;
            }
        });
    },
    
    getFirstAggregateIndex(group) {
        return this.state.columns.findIndex((col) => col.name in group.aggregates);
    },

    getGroupNameCellColSpan(group) {
        // if there are aggregates, the first th spans until the first
        // aggregate column then all cells between aggregates are rendered
        const firstAggregateIndex = this.getFirstAggregateIndex(group);
        let colspan;
        if (firstAggregateIndex > -1) {
            colspan = firstAggregateIndex + 2;
        } else {
            colspan = Math.max(1, this.state.columns.length - DEFAULT_GROUP_PAGER_COLSPAN + 2);
            if (this.displayOptionalFields) {
                colspan++;
            }
        }
        if (this.hasSelectors) {
            colspan++;
        }
        return colspan;
    },
    
});
