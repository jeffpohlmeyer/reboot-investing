<template>
  <apexchart
    type="candlestick"
    width="100%"
    height="80%"
    :series="series"
    :options="chartOptions"
  ></apexchart>
</template>

<script>
import { computed, defineComponent, watch } from 'vue';

export default defineComponent({
  props: {
    symbol: {
      type: String,
      required: true,
    },
    interval: {
      type: String,
      required: true,
    },
    series: {
      type: Array,
      required: true,
    },
  },
  setup(props) {
    const interval = computed(() => props.interval);
    const symbol = computed(() => props.symbol);
    const series = computed(() => props.series);

    const title = computed(() =>
      !series.value.length ? '' : `${interval.value} Chart of $${symbol.value}`
    );
    const animation = computed(() => {
      if (!series.value.length) return true
      return series.value[0].data.length < 200
    })

    const chartOptions = computed(() => ({
      chart: {
        type: 'candlestick',
        id: 'candles',
        animations: {
          enabled: animation.value,
          speed: 300,
        },
        dynamicAnimations: {
          enabled: animation.value,
          speed: 300
        },
        toolbar: {
          autoSelected: 'pan',
          show: false,
        },
        zoom: {
          enabled: false,
        },
      },
      title: {
        text: title.value,
        align: 'left',
        floating: true,
        offsetY: 25,
        offsetX: 10,
        style: {
          fontSize: '2rem',
        },
      },
      xaxis: {
        type: 'datetime',
      },
      yaxis: {
        tooltip: {
          enabled: true,
        },
        labels: {
          formatter: (val) => val.toFixed(0),
        },
      },
    }));
    return { series, chartOptions };
  },
});
</script>

<style scoped></style>
