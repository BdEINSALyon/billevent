import Vue from 'vue'
import App from './components/App.vue'
import MainComponent from './components/MainComponent.vue'


new Vue({
    el: '#app',
    components: {
        'app': App,
        'main': MainComponent
    }
});
console.log("Hello World2!");