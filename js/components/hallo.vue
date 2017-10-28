<template>
  <div id="hello">{{ msg }}</div>
</template>

<script>
export default {
    name: 'hallo',
  data () {
    console.log("Hello World!");
        return {
      msg: 'Hallo world!'
    }
  }
}
</script>

<style>
.example {
  color: red;
}
</style>