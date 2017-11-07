import rest from 'rest'
import mime from 'rest/interceptor/mime'
import Client from './Client'
import Billet from './Billet'
import Event from './Event'
/**
 * Gestionaire d'une commande
 */
export default class Order {

    id = null;
    client = null;
    billets = [];

    constructor(response) {
        console.log(response);
        this.id = response.id;
        this.client = response.client ? new Client(response.client) : null;
        this.event = new Event(response.event);
        this.billets = response.billets ?
            response.billets.map((billet) => new Billet(billet)) : [];
    }

    static load(event) {
        return rest.wrap(mime)('/api/events/' + event + '/order').then(
            (response) => {
                return new Order(response.entity)
            },
            (error) => {}
        )
    }

    toJson(){
        return {
            id: this.id,
            client: this.client ? this.client.toJSON() : null,
            billets: this.billets
        }
    }

}
