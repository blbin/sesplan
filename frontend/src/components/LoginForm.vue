<template>
  <div class="login-container">
    <div class="login-card">
      <h1 class="login-title">Login</h1>

      <div v-if="authError || message" :class="['alert', success ? 'alert-success' : 'alert-error']">
        {{ authError || message }}
      </div>

      <form @submit.prevent="handleLogin" class="login-form">
        <div class="form-group">
          <label for="username">Username</label>
          <input
            id="username"
            v-model="username"
            type="text"
            required
            autocomplete="username"
            :class="{ 'input-error': errors.username }"
          />
          <span v-if="errors.username" class="error-text">{{ errors.username }}</span>
        </div>

        <div class="form-group">
          <label for="password">Password</label>
          <input
            id="password"
            v-model="password"
            type="password"
            required
            autocomplete="current-password"
            :class="{ 'input-error': errors.password }"
          />
          <span v-if="errors.password" class="error-text">{{ errors.password }}</span>
        </div>

        <button type="submit" class="login-button" :disabled="isLoading">
          <span v-if="isLoading" class="spinner"></span>
          <span v-else>Login</span>
        </button>
      </form>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, computed } from 'vue';
import { useRouter } from 'vue-router';
import { useAuthStore } from '../store/auth.store';

export default defineComponent({
  name: 'LoginForm',
  setup() {
    const router = useRouter();
    const authStore = useAuthStore();
    const username = ref('');
    const password = ref('');
    const message = ref('');
    const success = ref(false);
    const errors = ref({
      username: '',
      password: ''
    });

    const isLoading = computed(() => authStore.isLoading);
    const authError = computed(() => authStore.authError);

    const validateForm = (): boolean => {
      errors.value = {
        username: '',
        password: ''
      };

      let isValid = true;

      if (!username.value.trim()) {
        errors.value.username = 'Username is required';
        isValid = false;
      }

      if (!password.value) {
        errors.value.password = 'Password is required';
        isValid = false;
      }

      return isValid;
    };

    const handleLogin = async () => {
      if (!validateForm()) return;

      message.value = '';
      success.value = false;

      try {
        await authStore.login({
          username: username.value,
          password: password.value
        });

        success.value = true;
        message.value = 'Login successful! Redirecting...';

        setTimeout(() => {
          router.push('/dashboard');
        }, 1500);
      } catch (error: any) {
        success.value = false;
        console.error("Login component error catcher:", error);
      }
    };

    return {
      username,
      password,
      isLoading,
      authError,
      message,
      success,
      errors,
      handleLogin
    };
  }
});
</script>

<style scoped>
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background-color: #f5f7fa;
  padding: 20px;
}

.login-card {
  width: 100%;
  max-width: 400px;
  padding: 2rem;
  background: white;
  border-radius: 8px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
}

.login-title {
  margin-bottom: 1.5rem;
  color: #2c3e50;
  font-size: 1.8rem;
  font-weight: 600;
  text-align: center;
}

.login-form {
  display: flex;
  flex-direction: column;
  gap: 1.2rem;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

label {
  font-size: 0.9rem;
  font-weight: 500;
  color: #4a5568;
}

input {
  padding: 0.75rem 1rem;
  border: 1px solid #e2e8f0;
  border-radius: 4px;
  font-size: 1rem;
  transition: border-color 0.2s;
}

input:focus {
  border-color: #4299e1;
  outline: none;
  box-shadow: 0 0 0 3px rgba(66, 153, 225, 0.15);
}

.input-error {
  border-color: #e53e3e;
}

.error-text {
  color: #e53e3e;
  font-size: 0.8rem;
  margin-top: 0.25rem;
}

.login-button {
  margin-top: 1rem;
  padding: 0.75rem 1rem;
  background-color: #4299e1;
  color: white;
  border: none;
  border-radius: 4px;
  font-size: 1rem;
  font-weight: 500;
  cursor: pointer;
  transition: background-color 0.2s;
  display: flex;
  justify-content: center;
  align-items: center;
  height: 45px;
}

.login-button:hover {
  background-color: #3182ce;
}

.login-button:disabled {
  background-color: #a0aec0;
  cursor: not-allowed;
}

.alert {
  padding: 0.75rem 1rem;
  border-radius: 4px;
  margin-bottom: 1rem;
  font-size: 0.9rem;
}

.alert-success {
  background-color: #c6f6d5;
  color: #2f855a;
  border: 1px solid #9ae6b4;
}

.alert-error {
  background-color: #fed7d7;
  color: #c53030;
  border: 1px solid #feb2b2;
}

.spinner {
  display: inline-block;
  width: 20px;
  height: 20px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-radius: 50%;
  border-top-color: white;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}
</style>