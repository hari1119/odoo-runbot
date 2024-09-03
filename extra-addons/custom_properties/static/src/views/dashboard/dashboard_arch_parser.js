/** @odoo-module */

import { parseXML } from "@web/core/utils/xml";

export class BeautifulArchParser extends parseXML {
    parse(arch) {
        const xmlDoc = this.parseXML(arch);
	console.log("KKKKKKKKKKKKKKKKKKKK", xmlDoc)    
        const fieldFromTheArch = xmlDoc.getAttribute("fieldFromTheArch");
        return {
            fieldFromTheArch,
        };
    }
}
