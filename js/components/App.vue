<template>
    <div id="app">
        <router-view></router-view>
    </div>
</template>

<script>
    import VueRouter from 'vue-router'
    import main_component from './MainComponent.vue'
    import Vue from "vue";
    import API from "../billevent/api";

    window.BAPI = API;

    export default {
        name: 'app',
        router: new VueRouter({
            routes: [
                {path: '/', component: main_component},
            ]
        })
    }
</script>

<style type="scss">

</style>