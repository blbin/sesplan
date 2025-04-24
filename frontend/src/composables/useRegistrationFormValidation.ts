import { ref, reactive, computed, type Ref } from 'vue';
import type { UserCreate } from '@/types/user';

// Define the structure for form errors
interface RegistrationErrors {
  username?: string;
  email?: string;
  password?: string;
  passwordConfirm?: string;
}

// Define the structure for the form data (matching UserCreate)
// We add passwordConfirm which is not part of UserCreate
interface RegistrationFormData extends Omit<UserCreate, 'id' | 'created_at' | 'updated_at'> { // Omit server-generated fields
  passwordConfirm: string;
}

export function useRegistrationFormValidation(formData: Ref<RegistrationFormData>) {
  const errors = reactive<RegistrationErrors>({});

  const validateEmail = (email: string): boolean => {
    // Basic email validation regex (consider using a more robust library if needed)
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
  };

  const validateForm = (): boolean => {
    // Reset errors
    Object.keys(errors).forEach(key => delete errors[key as keyof RegistrationErrors]);

    let isValid = true;

    // Username validation
    if (!formData.value.username.trim()) {
      errors.username = 'Username is required.';
      isValid = false;
    }

    // Email validation
    if (!formData.value.email.trim()) {
      errors.email = 'Email is required.';
      isValid = false;
    } else if (!validateEmail(formData.value.email)) {
      errors.email = 'Please enter a valid email address.';
      isValid = false;
    }

    // Password validation
    if (!formData.value.password) { // Check if password exists (non-empty)
      errors.password = 'Password is required.';
      isValid = false;
    } else if (formData.value.password.length < 8) {
      errors.password = 'Password must be at least 8 characters long.';
      isValid = false;
    }

    // Password confirmation validation
    if (!formData.value.passwordConfirm) {
        errors.passwordConfirm = 'Please confirm your password.';
        isValid = false;
    } else if (formData.value.password !== formData.value.passwordConfirm) {
      errors.passwordConfirm = 'Passwords do not match.';
      isValid = false;
    }

    return isValid;
  };

  // Expose errors and validation function
  return {
    errors,
    validateForm,
  };
} 