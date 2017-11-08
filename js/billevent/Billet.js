

import Product from "./Product";
import Option from "./Option";

export default class Billet{

    constructor(billet) {
        this.id = billet.id;
        this.product = new Product(billet.product);
        this.options = billet.options.map((option) => new Option(option))
    }

}