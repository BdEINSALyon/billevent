<template>
    <div id="app">
        <h1>Hello App!</h1>
        <p>
            <!-- use router-link component for navigation. -->
            <!-- specify the link by passing the `to` prop. -->
            <!-- `<router-link>` will be rendered as an `<a>` tag by default -->
            <router-link to="/hello">Go to Hello</router-link>
            <router-link to="/hallo">Go to Hallo</router-link>
        </p>
        <!-- route outlet -->
        <!-- component matched by the route will render here -->
        <router-view></router-view>
    </div>
</template>

<script>
    import VueRouter from 'vue-router'
    import hello from './hello.vue'
    import hallo from './hallo.vue'
    import Vue from "vue";



    export default {
        name: 'app',
        router: new VueRouter({
            routes: [
                {path: '/hello', component: hello},
                {path: '/hallo', component: hallo},
            ]
        })
    }
</script>

<style type="scss">

</style>