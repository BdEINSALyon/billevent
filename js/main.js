import Vue from 'vue'
import hello from './components/hello.vue'
import Billetterie from './components/Billetterie.vue'

new Vue({
    el: '#app',
    components: {
        'app': Billetterie
    }
});
console.log("Hello World2!");