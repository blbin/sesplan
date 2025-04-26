<template>
  <v-form
    ref="form"
    v-model="isValid"
    @submit.prevent="submitForm"
    class="vuetify-form"
  >
    <v-container>
      <v-row>
        <v-col cols="12">
          <v-text-field
            v-model="name"
            :rules="nameRules"
            label="Název"
            variant="outlined"
            density="comfortable"
            required
          ></v-text-field>
        </v-col>
      </v-row>

      <v-row>
        <v-col cols="12">
          <v-textarea
            v-model="description"
            :rules="descriptionRules"
            label="Popis"
            variant="outlined"
            density="comfortable"
          ></v-textarea>
        </v-col>
      </v-row>

      <v-row>
        <v-col cols="12" md="6">
          <v-select
            v-model="category"
            :items="categories"
            label="Kategorie"
            variant="outlined"
            density="comfortable"
            :rules="categoryRules"
          ></v-select>
        </v-col>
        
        <v-col cols="12" md="6">
          <v-checkbox
            v-model="isPublic"
            label="Veřejné"
            hide-details
          ></v-checkbox>
        </v-col>
      </v-row>

      <v-row>
        <v-col cols="12">
          <v-file-input
            v-model="file"
            label="Nahrát soubor"
            variant="outlined"
            density="comfortable"
            prepend-icon="mdi-paperclip"
            :rules="fileRules"
          ></v-file-input>
        </v-col>
      </v-row>

      <v-row justify="end">
        <v-col cols="12" class="d-flex justify-end">
          <v-btn
            variant="text"
            class="me-2" 
            @click="resetForm"
          >
            Zrušit
          </v-btn>
          <v-btn
            type="submit"
            color="primary"
            :loading="loading"
            :disabled="!isValid || loading"
          >
            Uložit
          </v-btn>
        </v-col>
      </v-row>
    </v-container>
  </v-form>
</template>

<script lang="ts">
import { defineComponent, ref } from 'vue'

export default defineComponent({
  name: 'VuetifyForm',
  props: {
    loading: {
      type: Boolean,
      default: false
    },
    initialData: {
      type: Object,
      default: () => ({})
    }
  },
  emits: ['submit', 'cancel'],
  setup(props, { emit }) {
    const form = ref<any>(null)
    const isValid = ref(false)
    
    // Form fields
    const name = ref(props.initialData.name || '')
    const description = ref(props.initialData.description || '')
    const category = ref(props.initialData.category || null)
    const isPublic = ref(props.initialData.isPublic ?? false)
    const file = ref(null)
    
    // Form validation rules
    const nameRules = [
      (v: string) => !!v || 'Název je povinný',
      (v: string) => (v && v.length >= 3) || 'Název musí mít alespoň 3 znaky',
    ]
    
    const descriptionRules = [
      (v: string) => !v || v.length <= 1000 || 'Popis může mít maximálně 1000 znaků',
    ]
    
    const categoryRules = [
      (v: any) => !!v || 'Kategorie je povinná',
    ]
    
    const fileRules = [
      (v: any) => !v || v.size < 2000000 || 'Soubor musí být menší než 2 MB',
    ]
    
    // Available categories
    const categories = [
      'Fantasy',
      'Sci-Fi',
      'Historical',
      'Modern',
      'Horror',
      'Other'
    ]
    
    // Form submit handler
    const submitForm = () => {
      if (!form.value.validate()) return
      
      emit('submit', {
        name: name.value,
        description: description.value,
        category: category.value,
        isPublic: isPublic.value,
        file: file.value
      })
    }
    
    // Reset form handler
    const resetForm = () => {
      form.value.reset()
      emit('cancel')
    }
    
    return {
      form,
      isValid,
      name,
      description,
      category,
      isPublic,
      file,
      nameRules,
      descriptionRules,
      categoryRules,
      fileRules,
      categories,
      submitForm,
      resetForm
    }
  }
})
</script>

<style scoped>
.vuetify-form {
  width: 100%;
  max-width: 900px;
  margin: 0 auto;
}
</style> 