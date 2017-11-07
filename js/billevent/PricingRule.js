/**
 * Store PricingRule retrieved from Server
 * @type {Object<string, PricingRule>}
 */
const rules = {};

export default class PricingRule{

    constructor(rule){
        if(rules.hasOwnProperty(rule.id)){
            return rules[rule.id];
        } else {
            this.id = rule.id;
            this.type = rule.type;
            this.value = rule.value;
        }
    }

}