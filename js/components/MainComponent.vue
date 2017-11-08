<template>
  <div id="hello">{{ msg }}</div>
</template>

<script>
export default {
    name: 'main_component',
  data () {
    return new Promise((resolve) => {
        setTimeout(() => {
          resolve({msg: 'hello'})
        }, 2000);
    })
  }
}
</script>

<style>
.example {
  color: red;
}
</style>