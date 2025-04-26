<template>
  <div class="tiptap-editor-wrapper">
    <!-- Toolbar -->
    <div v-if="editor" class="tiptap-toolbar">
      <v-btn-toggle variant="outlined" divided density="compact">
        <v-btn 
          icon
          @click="editor.chain().focus().toggleBold().run()"
          :disabled="!editor.can().chain().focus().toggleBold().run()"
          :class="{ 'is-active': editor.isActive('bold') }"
          title="Bold (Ctrl+B)"
        >
          <v-icon>mdi-format-bold</v-icon>
        </v-btn>
        <v-btn 
          icon
          @click="editor.chain().focus().toggleItalic().run()"
          :disabled="!editor.can().chain().focus().toggleItalic().run()"
          :class="{ 'is-active': editor.isActive('italic') }"
          title="Italic (Ctrl+I)"
        >
          <v-icon>mdi-format-italic</v-icon>
        </v-btn>
        <v-btn 
          icon
          @click="editor.chain().focus().toggleStrike().run()"
          :disabled="!editor.can().chain().focus().toggleStrike().run()"
          :class="{ 'is-active': editor.isActive('strike') }"
          title="Strikethrough"
        >
          <v-icon>mdi-format-strikethrough</v-icon>
        </v-btn>
      </v-btn-toggle>

      <v-btn-toggle variant="outlined" divided density="compact" class="ml-2">
         <v-btn 
          icon
          @click="editor.chain().focus().toggleBulletList().run()"
          :class="{ 'is-active': editor.isActive('bulletList') }"
          title="Bullet List"
        >
          <v-icon>mdi-format-list-bulleted</v-icon>
        </v-btn>
        <v-btn 
          icon
          @click="editor.chain().focus().toggleOrderedList().run()"
          :class="{ 'is-active': editor.isActive('orderedList') }"
          title="Ordered List"
        >
          <v-icon>mdi-format-list-numbered</v-icon>
        </v-btn>
      </v-btn-toggle>

      <v-btn-toggle variant="outlined" divided density="compact" class="ml-2">
         <v-btn 
          icon
          @click="editor.chain().focus().toggleBlockquote().run()"
          :class="{ 'is-active': editor.isActive('blockquote') }"
          title="Blockquote"
        >
          <v-icon>mdi-format-quote-close</v-icon>
        </v-btn>
        <v-btn 
          icon
          @click="editor.chain().focus().setHorizontalRule().run()"
          title="Horizontal Rule"
        >
          <v-icon>mdi-minus</v-icon>
        </v-btn>
      </v-btn-toggle>
    </div>

    <v-divider v-if="editor" class="my-2"></v-divider>

    <editor-content :editor="editor" class="tiptap-content" />
  </div>
</template>

<script setup lang="ts">
import { ref, watch, onBeforeUnmount } from 'vue'
import { useEditor, EditorContent } from '@tiptap/vue-3'
import StarterKit from '@tiptap/starter-kit'
import { Markdown } from 'tiptap-markdown'

// Define props and emits inline
const props = defineProps<{ modelValue: string }>()
const emit = defineEmits<{ (e: 'update:modelValue', value: string): void }>()

const internalContent = ref(props.modelValue)

const editor = useEditor({
  content: internalContent.value, // Initialize with Markdown
  extensions: [
    StarterKit.configure({
      // Configure StarterKit options if needed
      // e.g., disable heading levels, etc.
    }),
    Markdown.configure({
      html: false, // Prevent HTML input/output for security
      tightLists: true,
      linkify: true, // Automatically convert URL-like text to links
      breaks: true, // Convert newlines in markdown to <br>
      transformPastedText: true, // Allow pasting markdown
      transformCopiedText: true, // Copy as markdown
    }),
  ],
  editorProps: {
    attributes: {
      class: 'prose prose-sm sm:prose lg:prose-lg xl:prose-2xl mx-auto focus:outline-none', // Basic prose styling, adjust as needed
    },
  },
  onUpdate: () => {
    if (editor.value) {
      // Get content as Markdown and emit update
      const markdown = editor.value.storage.markdown.getMarkdown()
      internalContent.value = markdown
      emit('update:modelValue', markdown)
    }
  },
})

// Watch for external changes to modelValue
watch(() => props.modelValue, (newValue) => {
  if (editor.value && editor.value.storage.markdown.getMarkdown() !== newValue) {
    // Avoid unnecessary updates and potential cursor jumps
    // Set content expects markdown here thanks to the Markdown extension
    editor.value.commands.setContent(newValue, false) // false to not emit update again
  }
})

// Ensure editor is destroyed when component unmounts
onBeforeUnmount(() => {
  if (editor.value) {
    editor.value.destroy()
  }
})

</script>

<style scoped>
.tiptap-editor-wrapper {
  border: 1px solid #ccc; /* Basic border */
  border-radius: 4px;
  /* Removed padding here, toolbar handles top padding */
}

.tiptap-toolbar {
  display: flex;
  flex-wrap: wrap; /* Allow wrapping on smaller screens */
  align-items: center;
  padding: 8px 10px;
  border-bottom: 1px solid #ccc; 
}

.tiptap-toolbar .v-btn {
  /* Ensure consistent height/look */
}

.tiptap-toolbar .v-btn.is-active {
  background-color: rgba(0, 0, 0, 0.1); /* Visual cue for active button */
  border-color: rgba(0, 0, 0, 0.2); 
}

.ml-2 {
  margin-left: 8px; /* Space between button groups */
}
.my-2 {
    margin-top: 8px;
    margin-bottom: 8px;
}

.tiptap-content {
  padding: 10px; /* Add padding back to the content area */
  outline: none;
}

/* Style ProseMirror/Tiptap elements if needed */
:deep(.ProseMirror) {
  min-height: 100px; /* Ensure minimum height */
}

:deep(.ProseMirror p.is-editor-empty:first-child::before) {
  content: attr(data-placeholder);
  float: left;
  color: #adb5bd;
  pointer-events: none;
  height: 0;
}
</style> 