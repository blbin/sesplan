<template>
  <div class="tiptap-editor-wrapper">
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
  padding: 10px;
  min-height: 150px; /* Adjust as needed */
}

.tiptap-content {
  /* Add styles for the editor content area if needed */
  /* ProseMirror default styles might be sufficient */
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