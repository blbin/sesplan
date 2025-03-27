<template>
  <div class="register-container">
    <div class="register-card">
      <h1 class="register-title">Register</h1>

      <div v-if="message" :class="['alert', success ? 'alert-success' : 'alert-error']">
        {{ message }}
      </div>

      <form @submit.prevent="handleRegister" class="register-form">
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
          <label for="email">Email</label>
          <input
            id="email"
            v-model="email"
            type="email"
            required
            autocomplete="email"
            :class="{ 'input-error': errors.email }"
          />
          <span v-if="errors.email" class="error-text">{{ errors.email }}</span>
        </div>

        <div class="form-group">
          <label for="password">Password</label>
          <input
            id="password"
            v-model="password"
            type="password"
            required
            autocomplete="new-password"
            :class="{ 'input-error': errors.password }"
          />
          <span v-if="errors.password" class="error-text">{{ errors.password }}</span>
        </div>

        <div class="form-group">
          <label for="confirmPassword">Confirm Password</label>
          <input
            id="confirmPassword"
            v-model="confirmPassword"
            type="password"
            required
            autocomplete="new-password"
            :class="{ 'input-error': errors.confirmPassword }"
          />
          <span v-if="errors.confirmPassword" class="error-text">{{ errors.confirmPassword }}</span>
        </div>

        <button type="submit" class="register-button" :disabled="loading">
          <span v-if="loading" class="spinner"></span>
          <span v-else>Register</span>
        </button>

        <div class="login-link">
          Already have an account? <router-link to="/login">Log in</router-link>
        </div>
      </form>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref } from 'vue';
import { useRouter } from 'vue-router';
import { userService } from '../services/user.service';

export default defineComponent({
  name: 'RegisterForm',
  setup() {
    const router = useRouter();
    const username = ref('');
    const email = ref('');
    const password = ref('');
    const confirmPassword = ref('');
    const loading = ref(false);
    const message = ref('');
    const success = ref(false);
    const errors = ref({
      username: '',
      email: '',
      password: '',
      confirmPassword: ''
    });

    const validateEmail = (email: string): boolean => {
      const regex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
      return regex.test(email);
    };

    const validateForm = (): boolean => {
      errors.value = {
        username: '',
        email: '',
        password: '',
        confirmPassword: ''
      };

      let isValid = true;

      if (!username.value.trim()) {
        errors.value.username = 'Username is required';
        isValid = false;
      } else if (username.value.length < 3) {
        errors.value.username = 'Username must be at least 3 characters';
        isValid = false;
      }

      if (!email.value.trim()) {
        errors.value.email = 'Email is required';
        isValid = false;
      } else if (!validateEmail(email.value)) {
        errors.value.email = 'Please enter a valid email address';
        isValid = false;
      }

      if (!password.value) {
        errors.value.password = 'Password is required';
        isValid = false;
      } else if (password.value.length < 6) {
        errors.value.password = 'Password must be at least 6 characters';
        isValid = false;
      }

      if (!confirmPassword.value) {
        errors.value.confirmPassword = 'Please confirm your password';
        isValid = false;
      } else if (password.value !== confirmPassword.value) {
        errors.value.confirmPassword = 'Passwords do not match';
        isValid = false;
      }

      return isValid;
    };

    const handleRegister = async () => {
      if (!validateForm()) return;

      loading.value = true;
      message.value = '';

      try {
        await userService.register({
          username: username.value,
          email: email.value,
          password: password.value
        });

        success.value = true;
        message.value = 'Registration successful! Redirecting to login...';

        setTimeout(() => {
          router.push('/login');
        }, 2000);
      } catch (error: any) {
        success.value = false;

        if (error.response) {
          // Handle specific error responses
          if (error.response.status === 400) {
            if (error.response.data?.detail?.includes('Username already registered')) {
              errors.value.username = 'Username already exists';
            } else if (error.response.data?.detail?.includes('email')) {
              errors.value.email = 'Email already registered';
            } else {
              message.value = error.response.data?.detail || 'Registration failed. Please try again.';
            }
          } else {
            message.value = 'Registration failed. Please try again.';
          }
        } else {
          message.value = 'Registration failed. Please check your connection.';
        }
      } finally {
        loading.value = false;
      }
    };

    return {
      username,
      email,
      password,
      confirmPassword,
      loading,
      message,
      success,
      errors,
      handleRegister
    };
  }
});
</script>

<style scoped>
.register-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background-color: #f5f7fa;
  padding: 20px;
}

.register-card {
  width: 100%;
  max-width: 450px;
  padding: 2rem;
  background: white;
  border-radius: 8px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
}

.register-title {
  margin-bottom: 1.5rem;
  color: #2c3e50;
  font-size: 1.8rem;
  font-weight: 600;
  text-align: center;
}

.register-form {
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

.register-button {
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

.register-button:hover {
  background-color: #3182ce;
}

.register-button:disabled {
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

.login-link {
  margin-top: 1rem;
  text-align: center;
  font-size: 0.9rem;
  color: #4a5568;
}

.login-link a {
  color: #4299e1;
  text-decoration: none;
  font-weight: 500;
}

.login-link a:hover {
  text-decoration: underline;
}
</style> 