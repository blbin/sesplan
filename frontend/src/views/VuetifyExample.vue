<template>
  <div class="vuetify-example">
    <v-container>
      <v-row>
        <v-col cols="12">
          <v-card class="mb-5">
            <v-card-title class="text-h4">
              Vuetify Komponenty
              <v-chip class="ml-2" color="primary">Ukázka</v-chip>
            </v-card-title>
            <v-card-subtitle>
              Tato stránka demonstruje použití Vuetify komponent v Sesplan aplikaci
            </v-card-subtitle>
            <v-card-text>
              <p>
                Vuetify poskytuje bohatou sadu komponent pro tvorbu moderních webových aplikací.
                Zde jsou ukázky některých z nich:
              </p>
            </v-card-text>
          </v-card>
        </v-col>
      </v-row>

      <!-- Ukázka různých tlačítek -->
      <v-row>
        <v-col cols="12">
          <v-card>
            <v-card-title>
              <v-icon class="mr-2" color="primary">mdi-button-cursor</v-icon>
              Tlačítka
            </v-card-title>
            <v-card-text>
              <div class="d-flex flex-wrap gap-2">
                <v-btn color="primary">Primární</v-btn>
                <v-btn color="secondary">Sekundární</v-btn>
                <v-btn color="success">Úspěch</v-btn>
                <v-btn color="error">Chyba</v-btn>
                <v-btn color="warning">Varování</v-btn>
                <v-btn color="info">Info</v-btn>
              </div>

              <v-divider class="my-4"></v-divider>

              <div class="d-flex flex-wrap gap-2">
                <v-btn variant="outlined" color="primary">Outlined</v-btn>
                <v-btn variant="text" color="primary">Text</v-btn>
                <v-btn variant="plain" color="primary">Plain</v-btn>
                <v-btn variant="elevated" color="primary">Elevated</v-btn>
                <v-btn variant="tonal" color="primary">Tonal</v-btn>
              </div>

              <v-divider class="my-4"></v-divider>

              <div class="d-flex flex-wrap gap-2">
                <v-btn prepend-icon="mdi-check" color="primary">S ikonou</v-btn>
                <v-btn append-icon="mdi-arrow-right" color="primary">S ikonou</v-btn>
                <v-btn icon="mdi-heart" color="error"></v-btn>
                <v-btn icon="mdi-thumb-up" color="success"></v-btn>
                <v-btn size="small" color="primary">Malé</v-btn>
                <v-btn size="large" color="primary">Velké</v-btn>
              </div>
            </v-card-text>
          </v-card>
        </v-col>
      </v-row>

      <!-- Ukázka formuláře -->
      <v-row class="mt-5">
        <v-col cols="12">
          <v-card>
            <v-card-title>
              <v-icon class="mr-2" color="primary">mdi-form-select</v-icon>
              Ukázkový formulář
            </v-card-title>
            <v-card-text>
              <VuetifyForm @submit="handleFormSubmit" @cancel="handleFormCancel" />
            </v-card-text>
          </v-card>
        </v-col>
      </v-row>

      <!-- Ukázka dialogu -->
      <v-row class="mt-5">
        <v-col cols="12">
          <v-card>
            <v-card-title>
              <v-icon class="mr-2" color="primary">mdi-dialog</v-icon>
              Ukázka dialogů
            </v-card-title>
            <v-card-text>
              <div class="d-flex flex-wrap gap-2">
                <v-btn color="primary" @click="showDialog = true">
                  Otevřít dialog
                </v-btn>
                <v-btn color="secondary" @click="showAlertDialog = true">
                  Ukázat alert
                </v-btn>
              </div>
            </v-card-text>
          </v-card>
        </v-col>
      </v-row>

      <!-- Ukázka data table -->
      <v-row class="mt-5">
        <v-col cols="12">
          <v-card>
            <v-card-title>
              <v-icon class="mr-2" color="primary">mdi-table</v-icon>
              Data tabulka
            </v-card-title>
            <v-data-table
              :headers="headers"
              :items="items"
              :items-per-page="5"
              :search="search"
              class="elevation-1"
            >
              <template v-slot:top>
                <v-toolbar flat>
                  <v-toolbar-title>Seznam světů</v-toolbar-title>
                  <v-spacer></v-spacer>
                  <v-text-field
                    v-model="search"
                    prepend-icon="mdi-magnify"
                    label="Hledat"
                    single-line
                    variant="outlined"
                    density="comfortable"
                    hide-details
                    class="mx-4"
                    style="max-width: 300px;"
                  ></v-text-field>
                  <v-btn color="primary" prepend-icon="mdi-plus">
                    Přidat
                  </v-btn>
                </v-toolbar>
              </template>
              
              <template v-slot:item.actions="{ item }">
                <v-icon size="small" class="me-2" @click="editItem(item)">
                  mdi-pencil
                </v-icon>
                <v-icon size="small" @click="deleteItem(item)">
                  mdi-delete
                </v-icon>
              </template>
            </v-data-table>
          </v-card>
        </v-col>
      </v-row>
    </v-container>

    <!-- Dialog komponent -->
    <VuetifyDialog
      v-model="showDialog"
      title="Ukázkový dialog"
      icon="mdi-information"
      max-width="500"
      @confirm="confirmDialog"
    >
      <p>Toto je ukázkový dialog, který demonstruje použití Vuetify dialogy v aplikaci Sesplan.</p>
      <p>Dialog obsahuje potvrzovací a zrušit tlačítka, které lze přizpůsobit potřebám aplikace.</p>
    </VuetifyDialog>

    <!-- Alert dialog -->
    <v-dialog v-model="showAlertDialog" max-width="400">
      <v-card>
        <v-card-title class="text-h5">
          <v-icon color="warning" class="mr-2">mdi-alert</v-icon>
          Upozornění
        </v-card-title>
        <v-card-text>
          Tento dialog je ukázka základního alertu, který lze použít pro zobrazení důležitých zpráv uživateli.
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn color="primary" @click="showAlertDialog = false">
            Rozumím
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref } from 'vue'
import VuetifyForm from '../components/common/VuetifyForm.vue'
import VuetifyDialog from '../components/common/VuetifyDialog.vue'

export default defineComponent({
  name: 'VuetifyExample',
  components: {
    VuetifyForm,
    VuetifyDialog
  },
  setup() {
    // Dialog states
    const showDialog = ref(false)
    const showAlertDialog = ref(false)
    
    // Table search
    const search = ref('')
    
    // Table headers
    const headers = [
      { title: 'Název', key: 'name' },
      { title: 'Typ', key: 'type' },
      { title: 'Popis', key: 'description' },
      { title: 'Vytvořeno', key: 'created' },
      { title: 'Veřejné', key: 'public' },
      { title: 'Akce', key: 'actions', sortable: false }
    ]
    
    // Sample data
    const items = [
      {
        name: 'Aetheria',
        type: 'Fantasy',
        description: 'Svět plný magie a draků',
        created: '2023-01-15',
        public: 'Ano'
      },
      {
        name: 'Nexus-7',
        type: 'Sci-Fi',
        description: 'Futuristická vesmírná stanice',
        created: '2023-02-20',
        public: 'Ne'
      },
      {
        name: 'Eldoria',
        type: 'Fantasy',
        description: 'Středověký svět s elfími kmeny',
        created: '2023-03-10',
        public: 'Ano'
      },
      {
        name: 'Nova Terra',
        type: 'Post-Apocalyptic',
        description: 'Země po globální katastrofě',
        created: '2023-04-05',
        public: 'Ne'
      },
      {
        name: 'Chronos',
        type: 'Steampunk',
        description: 'Svět mechanických vynálezů',
        created: '2023-05-12',
        public: 'Ano'
      },
      {
        name: 'Mysthaven',
        type: 'Fantasy',
        description: 'Tajemná říše kouzel',
        created: '2023-06-18',
        public: 'Ne'
      }
    ]
    
    // Form handling
    const handleFormSubmit = (formData: any) => {
      console.log('Form submitted:', formData)
      alert('Formulář byl odeslán!')
    }
    
    const handleFormCancel = () => {
      console.log('Form cancelled')
    }
    
    // Dialog handling
    const confirmDialog = () => {
      console.log('Dialog confirmed')
      showDialog.value = false
    }
    
    // Table actions
    const editItem = (item: any) => {
      console.log('Edit item:', item)
    }
    
    const deleteItem = (item: any) => {
      console.log('Delete item:', item)
    }
    
    return {
      showDialog,
      showAlertDialog,
      search,
      headers,
      items,
      handleFormSubmit,
      handleFormCancel,
      confirmDialog,
      editItem,
      deleteItem
    }
  }
})
</script>

<style scoped>
.vuetify-example {
  padding: 20px 0;
}

.gap-2 {
  gap: 8px;
}
</style> 