<template>
  <div class="h-screen">
    <Chart :series="series" :symbol="symbol" :interval="interval" :volume="volume" />
    <Selections @setData="setData" />
  </div>
</template>

<script>
import { defineComponent, ref } from 'vue';
import Selections from './components/Selections.vue';
import Chart from './components/Chart.vue';

export default defineComponent({
  components: {
    Selections,
    Chart,
  },
  setup() {
    const series = ref([]);
    const symbol = ref('');
    const interval = ref('Daily');
    const volume = ref([])

    const setData = (payload) => {
      series.value = payload.series;
      symbol.value = payload.symbol;
      interval.value = payload.interval;
      volume.value = payload.volume
    };

    return { setData, series, symbol, interval, volume };
  },
});
</script>

<style></style>
