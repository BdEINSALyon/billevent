import Event from './Event'
import PricingRule from "./PricingRule";
import Question from "./Question";

/**
 * Store Products retrieved from Server
 * @type {Object<string, Option>}
 */
const options = {};

export default class Option{

    constructor(option){
        if(options.hasOwnProperty(option.id)){
            return options[option.id];
        } else {
            this.id = option.id;
            this.name = option.name;
            this.price_ht = option.price_ht;
            this.price_ttc = option.price_ttc;
            this.rules = option.rules.map((rule) => new PricingRule(rule));
            this.questions = option.questions.map((question) => new Question(question));
            this.event = option.event ? new Event(option.event) : null;
        }
    }

}