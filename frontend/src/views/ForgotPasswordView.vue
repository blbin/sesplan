<template>
  <div class="forgot-password-container">
    <div class="forgot-password-card">
      <h1 class="forgot-password-title">Forgot Your Password?</h1>
      <p class="instructions">
        Enter your email address below, and we'll send you a link to reset your password.
      </p>

      <div v-if="message" :class="['alert', success ? 'alert-success' : 'alert-error']">
        {{ message }}
      </div>

      <form @submit.prevent="handleForgotPassword" class="forgot-password-form">
        <div class="form-group">
          <label for="email">Email Address</label>
          <input
            id="email"
            v-model="email"
            type="email"
            required
            autocomplete="email"
            placeholder="you@example.com"
            :class="{ 'input-error': !isEmailValid && email !== '' }"
          />
          <span v-if="!isEmailValid && email !== ''" class="error-text">Please enter a valid email address.</span>
        </div>

        <button type="submit" class="submit-button" :disabled="isLoading">
          <span v-if="isLoading" class="spinner"></span>
          <span v-else>Send Reset Link</span>
        </button>

        <div class="login-link">
          <router-link to="/login">Back to Login</router-link>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue';
import { authService } from '@/services/auth.service'; // Assuming path

const email = ref('');
const isLoading = ref(false);
const message = ref('');
const success = ref(false);

// Basic email validation regex
const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
const isEmailValid = computed(() => emailRegex.test(email.value));

const handleForgotPassword = async () => {
  isLoading.value = true;
  message.value = '';
  success.value = false;

  if (!email.value) {
    message.value = 'Email address is required.';
    success.value = false;
    isLoading.value = false;
    return;
  }

  if (!isEmailValid.value) {
    message.value = 'Please enter a valid email address.';
    success.value = false;
    isLoading.value = false;
    return;
  }

  try {
    // Placeholder for actual API call.
    // await authService.requestPasswordReset(email.value); 
    // Simulate API call for now
    await new Promise(resolve => setTimeout(resolve, 1000));
    console.log(`Password reset requested for: ${email.value}`);


    success.value = true;
    message.value = "If an account with that email exists, a password reset link has been sent. Please check your inbox.";
    email.value = ''; // Clear email field on success
  } catch (error: any) {
    success.value = false;
    // In a real app, you might get a more specific error message from the service
    message.value = error?.response?.data?.detail || "An error occurred. Please try again.";
    console.error("Forgot Password error:", error);
  } finally {
    isLoading.value = false;
  }
};
</script>

<style scoped>
.forgot-password-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background-color: #f5f7fa;
  padding: 20px;
}

.forgot-password-card {
  width: 100%;
  max-width: 450px; /* Slightly wider for the instruction text */
  padding: 2rem;
  background: white;
  border-radius: 8px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
}

.forgot-password-title {
  margin-bottom: 1rem;
  color: #2c3e50;
  font-size: 1.8rem;
  font-weight: 600;
  text-align: center;
}

.instructions {
  font-size: 0.95rem;
  color: #4a5568;
  text-align: center;
  margin-bottom: 1.5rem;
  line-height: 1.6;
}

.forgot-password-form {
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

.submit-button {
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
  height: 45px; /* Consistent height */
}

.submit-button:hover {
  background-color: #3182ce;
}

.submit-button:disabled {
  background-color: #a0aec0;
  cursor: not-allowed;
}

.login-link {
  text-align: center;
  margin-top: 1rem;
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
