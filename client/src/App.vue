<template>
  <div class="h-screen bg-gray-200">
    <Selections class="px-4"/>
  </div>
</template>

<script>
import { defineComponent, ref } from 'vue';
import Selections from './components/Selections.vue'

export default defineComponent({
  components: { Selections },
  setup() {
    const series = ref([])
    const symbol = ref('')
    const interval = ref('Daily')
    const volume = ref([])

    return { series, symbol, interval, volume }
  }
})
</script>
