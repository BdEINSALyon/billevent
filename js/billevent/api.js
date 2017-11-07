import Order from "./Order";

export default class API{

    static getOrder(event_id) {
        return Order.load(event_id);
    }

}