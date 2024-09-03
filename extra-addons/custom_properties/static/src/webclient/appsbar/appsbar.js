/** @odoo-module **/

import { url } from '@web/core/utils/urls';
import { useService } from '@web/core/utils/hooks';

import { Component, onWillUnmount } from '@odoo/owl';

export class AppsBar extends Component {
	static template = 'custom_properties.AppsBar';
        static props = {};
        static clickCount = false;
	setup() {
		this.companyService = useService('company');
                this.expend = false
        this.appMenuService = useService('app_menu');
    	if (this.companyService.currentCompany.has_appsbar_image) {
            this.sidebarImageUrl = url('/web/image', {
                model: 'res.company',
                field: 'appbar_image',
                id: this.companyService.currentCompany.id,
            });
    	}
    	const renderAfterMenuChange = () => {
            this.render();
        };
        this.env.bus.addEventListener(
        	'MENUS:APP-CHANGED', renderAfterMenuChange
        );
        onWillUnmount(() => {
            this.env.bus.removeEventListener(
            	'MENUS:APP-CHANGED', renderAfterMenuChange
            );
        });
    }
    
    
    closeTab(){
          const button = document.getElementById('silde');
          const icon = document.getElementById('arrow_icon');
	  if (this.clickCount) {
	    button.classList.remove('mk_sidebar_type_large_custom');
	    icon.classList.remove('fa-chevron-right');
	    icon.classList.add('fa-chevron-left');
	    this.clickCount = false;
	  } else {
	    button.classList.add('mk_sidebar_type_large_custom');
	    icon.classList.remove('fa-chevron-left');
	    icon.classList.add('fa-chevron-right');
	    this.clickCount = true;
	  }
	     this.expend = true 
    }
}
