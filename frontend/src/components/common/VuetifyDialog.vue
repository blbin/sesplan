<template>
  <v-dialog
    v-model="modelValue"
    :max-width="maxWidth"
    :persistent="persistent"
    :scrollable="scrollable"
  >
    <v-card>
      <v-card-title class="text-h5 d-flex align-center">
        <v-icon v-if="icon" class="mr-2" :color="iconColor">{{ icon }}</v-icon>
        {{ title }}
        <v-spacer></v-spacer>
        <v-btn v-if="!hideCloseButton" icon variant="text" @click="close">
          <v-icon>mdi-close</v-icon>
        </v-btn>
      </v-card-title>

      <v-divider v-if="!hideHeaderDivider"></v-divider>

      <v-card-text :class="contentClass">
        <slot></slot>
      </v-card-text>

      <v-divider v-if="!hideFooterDivider && !hideFooter"></v-divider>

      <v-card-actions v-if="!hideFooter">
        <slot name="actions">
          <v-spacer></v-spacer>
          <v-btn color="primary" variant="text" @click="close">
            {{ cancelText }}
          </v-btn>
          <v-btn 
            color="primary" 
            variant="elevated" 
            @click="confirm"
            :loading="loading"
            :disabled="disabled"
          >
            {{ confirmText }}
          </v-btn>
        </slot>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script lang="ts">
import { defineComponent } from 'vue'

export default defineComponent({
  name: 'VuetifyDialog',
  props: {
    modelValue: {
      type: Boolean,
      required: true
    },
    title: {
      type: String,
      default: 'Dialog'
    },
    maxWidth: {
      type: [String, Number],
      default: 500
    },
    persistent: {
      type: Boolean,
      default: false
    },
    scrollable: {
      type: Boolean,
      default: false
    },
    hideCloseButton: {
      type: Boolean,
      default: false
    },
    hideHeaderDivider: {
      type: Boolean,
      default: false
    },
    hideFooterDivider: {
      type: Boolean,
      default: false
    },
    hideFooter: {
      type: Boolean,
      default: false
    },
    confirmText: {
      type: String,
      default: 'Potvrdit'
    },
    cancelText: {
      type: String,
      default: 'Zrušit'
    },
    loading: {
      type: Boolean,
      default: false
    },
    disabled: {
      type: Boolean,
      default: false
    },
    contentClass: {
      type: String,
      default: 'pt-4'
    },
    icon: {
      type: String,
      default: ''
    },
    iconColor: {
      type: String,
      default: 'primary'
    }
  },
  emits: ['update:modelValue', 'confirm', 'cancel'],
  setup(_, { emit }) {
    const close = () => {
      emit('update:modelValue', false)
      emit('cancel')
    }

    const confirm = () => {
      emit('confirm')
    }

    return {
      close,
      confirm
    }
  }
})
</script>

<style scoped>
/* Zde můžete přidat doplňující styly, pokud budou potřeba */
</style> 