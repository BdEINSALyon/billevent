import Product from './Product'

/**
 * Store Events retrieved from Server
 * @type {Object<string, Event>}
 */
const events = {};

export default class Event {

    constructor(event){
        if(events.hasOwnProperty(event.id.toString())) {
            // If we already has loaded the object, use the previous one
            return events[event.id];
        } else {
            this.id = event.id;
            this.name = event.name;
            this.description = event.description;
            this.products = event.products ?
        event.products.map((product) => new Product(product)) : [];
            this.logo_url = event.logo_url
        }
    }

}
