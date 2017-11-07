import Event from './Event'
import PricingRule from "./PricingRule";
import Option from './Option'
import Question from "./Question";

/**
 * Store Products retrieved from Server
 * @type {Object<string, Event>}
 */
const products = {};

export default class Product{

    constructor(product){
        if(products.hasOwnProperty(product.id)){
            return products[product.id];
        } else {
            this.id = product.id;
            this.name = product.name;
            this.price_ht = product.price_ht;
            this.price_ttc = product.price_ttc;
            this.rules = product.rules.map((rule) => new PricingRule(rule));
            this.options = product.options.map((option) => new Option(option));
            this.questions = product.questions.map((question) => new Question(question));
            this.event = product.event ? new Event(product.event) : null;
        }
    }

}