<!-- src/views/RegisterView.vue -->
<template>
  <div class="register-view">
    <RegisterForm />
  </div>
</template>

<script lang="ts">
import { defineComponent } from 'vue';
import RegisterForm from '../components/RegisterForm.vue';

export default defineComponent({
  name: 'RegisterView',
  components: {
    RegisterForm
  }
});
</script> 