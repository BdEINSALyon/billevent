<template>
  <div id="hello">{{ msg }}</div>
</template>

<script>
export default {
    name: 'hello',
  data () {
    console.log("Hello World!");
        return {
      msg: 'Hello world!'
    }
  }
}
</script>

<style>
.example {
  color: red;
}
</style>