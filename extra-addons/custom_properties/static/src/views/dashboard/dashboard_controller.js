/** @odoo-module */

import { Component , useState, onWillStart, useRef, onMounted } from "@odoo/owl";
import { ChartRenderer } from "./chart_renderer/chart_renderer"
import { registry } from "@web/core/registry";
import { standardViewProps } from "@web/views/standard_view_props"
import { useService } from "@web/core/utils/hooks";
import { DashboardItem } from "./dashboard_item/dashboard_item";
import { Layout } from "@web/search/layout"
import { browser } from "@web/core/browser/browser";
import { PieChart } from "./pie_chart/pie_chart";
import { RadarChart } from "./radar_chart/radar_chart";
import { ScatterChart } from "./scatter_chart/scatter_chart";
import { BarChart } from "./bar_chart/bar_chart";
import { LineChart } from "./line_chart/line_chart";
import { KpiCard } from "./kpi_card/kpi_card";

export class DashBoardController extends Component {
    static template = 'custom_properties.DashboardView';
    static components = { DashboardItem, KpiCard, Layout, PieChart, RadarChart, ScatterChart, BarChart, 
                          LineChart, ChartRenderer}
    static props = {
        ...standardViewProps,
    }

    setup(){
        this.statistics = useState(useService("dashboard.statistics"));
        this.dialog = useService("dialog");
        this.display = {
                controlPanel: {},
        };

        this.items = registry.category("dashboard").getAll();
        this.state = useState({
            disabledItems: browser.localStorage.getItem("disabledDashboardItems")?.split(",") || [],
            quotations: {
                value:10,
                percentage:6,
            },
            period:90,
	    division: "",
	    division_id: 0,
	    division_count: 0,
        });
        this.orm = useService("orm")
        this.actionService = useService("action")

        onWillStart(async ()=>{
            this.getDates()
            await this.getQuotations()
            await this.getOrders()
        })
        onMounted(async () => { 
	    await this.getDivsions()
        }); 
    }

    async onChangePeriod(){
        this.getDates()
        await this.getQuotations()
        await this.getOrders()
	await this.getDivsions_details()
    }

    async getDivsions(){ 
	const selectElement = document.getElementById('cm_select');  
        let domain = [['status', 'not in', ['sent', 'draft']]]
        //const options = await this.orm.search("cm.master", domain)
        const options_key = await this.orm.searchRead("cm.master", domain, ["name","id"], { });
	//const options = ['Option 1', 'Option 2', 'Option 3'];
	if (selectElement) {
          for (const optionText of options_key) {
             const option = document.createElement('option');
             option.value = optionText['name'];
             option.value1 = optionText['id'];
             option.text = optionText['name'];   
             selectElement.appendChild(option);
           }
	}    
    }
    async getDivsions_details(){
        let domain = [['status', 'not in', ['sent', 'draft']]]
        let div_domain = [['status', 'not in', ['sent', 'draft']]]
	const selectElement = document.getElementById('cm_select');
	const selectedValue = selectElement.value;
	this.state.division = selectedValue
        if (this.state.division){
            div_domain.push(['name','=', this.state.division])
        }
	const division_key = await this.orm.searchRead("cm.master", div_domain, ["id"], { });
        for (const div_rec of division_key) {
		this.state.division_id = div_rec["id"]
	}
        if (this.state.division_id > 0){
            domain.push(['division_id','=', this.state.division_id])
        }
        const div_count = await this.orm.searchCount("ct.transaction", domain);
	this.state.division_count = div_count   

    }	    

    getDates(){
        this.state.current_date = '2024-07-18'//moment().subtract(this.state.period, 'days').format('YYYY-MM-DD')
        this.state.previous_date = '2024-01-01'//moment().subtract(this.state.period * 2, 'days').format('YYYY-MM-DD')
    }

    async getQuotations(){
        let domain = [['status', 'in', ['sent', 'draft']]]
        if (this.state.period > 0){
            domain.push(['entry_date','>', this.state.current_date])
        }
        const data = await this.orm.searchCount("ct.transaction", domain)
        this.state.quotations.value = data

        // previous period
        let prev_domain = [['status', 'in', ['sent', 'draft']]]
        if (this.state.period > 0){
            prev_domain.push(['entry_date','>', this.state.previous_date], ['entry_date','<=', this.state.current_date])
        }
        const prev_data = await this.orm.searchCount("ct.transaction", prev_domain)
        const percentage = ((data - prev_data)/prev_data) * 100
        this.state.quotations.percentage = percentage.toFixed(2)
    }

    async getOrders(){
        let domain = [['status', 'in', ['approved']]]
        if (this.state.period > 0){
            domain.push(['entry_date','>', this.state.current_date])
        }
        const data = await this.orm.searchCount("ct.transaction", domain)
        //this.state.quotations.value = data

        // previous period
        let prev_domain = [['status', 'in', ['approved']]]
        if (this.state.period > 0){
            prev_domain.push(['entry_date','>', this.state.previous_date], ['entry_date','<=', this.state.current_date])
        }
        const prev_data = await this.orm.searchCount("ct.transaction", prev_domain)
        const percentage = ((data - prev_data)/prev_data) * 100
        //this.state.quotations.percentage = percentage.toFixed(2)

        //revenues
        const current_revenue = await this.orm.readGroup("ct.transaction", domain, ["net_amt:sum"], [])
        const prev_revenue = await this.orm.readGroup("ct.transaction", prev_domain, ["net_amt:sum"], [])
        const revenue_percentage = ((current_revenue[0].amount_total - prev_revenue[0].amount_total) / prev_revenue[0].amount_total) * 100

        //average
        const current_average = await this.orm.readGroup("ct.transaction", domain, ["net_amt:avg"], [])
        const prev_average = await this.orm.readGroup("ct.transaction", prev_domain, ["net_amt:avg"], [])
        const average_percentage = ((current_average[0].amount_total - prev_average[0].amount_total) / prev_average[0].amount_total) * 100
        this.state.orders = {
            value: data,
            percentage: percentage.toFixed(2),
            revenue: `$${(current_revenue[0].amount_total/1000).toFixed(2)}K`,
            revenue_percentage: revenue_percentage.toFixed(2),
            average: `$${(current_average[0].amount_total/1000).toFixed(2)}K`,
            average_percentage: average_percentage.toFixed(2),
        }

        //this.env.services.company
    }

    async viewQuotations(){
        let domain = [['status', 'in', ['sent', 'draft']]]
        if (this.state.period > 0){
            domain.push(['entry_date','>', this.state.current_date])
        }

        let list_view = await this.orm.searchRead("ir.model.data", [['name', '=', 'view_quotation_tree_with_onboarding']], ['res_id'])

        this.actionService.doAction({
            type: "ir.actions.act_window",
            name: "Quotations",
            res_model: "ct.transaction",
            domain,
            views: [
                [list_view.length > 0 ? list_view[0].res_id : false, "list"],
                [false, "form"],
            ]
        })
    }

    viewOrders(){
        let domain = [['status', 'in', ['approved']]]
        if (this.state.period > 0){
            domain.push(['entry_date','>', this.state.current_date])
        }

        this.actionService.doAction({
            type: "ir.actions.act_window",
            name: "Quotations",
            res_model: "ct.transaction",
            domain,
            context: {group_by: ['entry_date']},
            views: [
                [false, "list"],
                [false, "form"],
            ]
        })
    }

    viewRevenues(){
        let domain = [['status', 'in', ['approved']]]
        if (this.state.period > 0){
            domain.push(['entry_date','>', this.state.current_date])
        }

        this.actionService.doAction({
            type: "ir.actions.act_window",
            name: "Quotations",
            res_model: "ct.transaction",
            domain,
            context: {group_by: ['entry_date']},
            views: [
                [false, "pivot"],
                [false, "form"],
            ]
        })
    }

    openConfiguration() {
        this.dialog.add(ConfigurationDialog, {
            items: this.items,
            disabledItems: this.state.disabledItems,
            onUpdateConfiguration: this.updateConfiguration.bind(this),
        })

        /**onWillStart(async () => {
                //this.statistics = await this.rpc("/awesome_dashboard/statistics");
                this.statistics = await this.statistics.loadStatistics();
        });*/
    }
    openCustomerView() {
        this.action.doAction("base.action_partner_form");

        }
    openfieldsdatabankView() {
        this.action.doAction("fields_databank.action_fields_databank");

        }

    openLeads() {
        this.action.doAction({
            type: "ir.actions.act_window",
            name: "All leads",
            res_model: "crm.lead",
            views: [
                [false, "list"],
                [false, "form"],
                [false, "kanban"],
                [false, "pivot"],
            ],
        });
    }


}

