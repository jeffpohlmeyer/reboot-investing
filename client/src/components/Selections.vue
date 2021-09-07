<template>
  <div class="px-5 sm:px-0">
    <JVPDialog :dialog="dialog" @closeDialog="dialog = false" />
    <div class="flex justify-around flex-col sm:flex-row sm:flex-wrap">
      <JVPInput
        v-model="state.symbol"
        id="symbol"
        label="Symbol"
        :vuelidate="v$.symbol"
        hint="Required"
        class="my-2 mx-1 sm:w-1/3 md:w-1/4 lg:w-2/12"
        placeholder="eg. MSFT"
        :autofocus="true"
        @keydown.enter="submit"
      />
      <JVPInput
        v-model="state.startDate"
        type="date"
        id="start-date"
        label="Start Date"
        :vuelidate="v$.startDate"
        hint="Optional"
        class="my-2 mx-1 sm:w-1/3 md:w-1/4 lg:w-2/12"
        @keydown.enter="submit"
      />
      <JVPInput
        v-model="state.endDate"
        type="date"
        id="end-date"
        label="End Date"
        :vuelidate="v$.endDate"
        hint="Optional"
        class="my-2 mx-1 sm:w-1/3 md:w-1/4 lg:w-2/12"
        @keydown.enter="submit"
      />
      <JVPSelect
        v-model="state.interval"
        id="interval"
        :options="intervals"
        label="Interval"
        :vuelidate="v$.interval"
        class="my-2 mx-1 sm:w-1/3 md:w-1/4 lg:w-2/12"
      />
    </div>
    <div class="flex justify-center">
      <div class="w-full sm:w-1/2 md:w-1/3 lg:w-1/4">
        <button
          type="button"
          class="
            w-full
            h-12
            px-6
            mt-6
            lg:mt-0
            text-indigo-100
            transition-colors
            duration-150
            bg-indigo-700
            rounded-lg
            focus:shadow-outline
            hover:bg-indigo-800
            disabled:opacity-50
          "
          :disabled="disabled"
          @click="submit"
        >
          <span
            v-if="loading"
            class="
              loader
              ease-linear
              rounded-full
              border-4 border-t-4 border-gray-200
              h-10
              w-10
              mx-auto
              block
            "
          ></span>
          <span v-else>Get Chart</span>
        </button>
        <p v-if="disabled" class="text-red-600 text-center text-xs">
          {{ disabledText }}
        </p>
      </div>
    </div>
  </div>
</template>

<script>
import { defineComponent, reactive, ref, computed } from 'vue';
import useVuelidate from '@vuelidate/core';
import { required } from '@vuelidate/validators';
import JVPSelect from './JVPSelect.vue';
import JVPInput from './JVPInput.vue';
import JVPDialog from './JVPDialog.vue';

export default defineComponent({
  components: { JVPSelect, JVPInput, JVPDialog },
  emits: ['setData'],
  setup(_, { emit }) {
    const intervals = ['Daily', 'Weekly', 'Monthly'];

    // Vuelidate's base docs include using reactive instead of refs
    // so it's cleaner to utilize this method.
    const state = reactive({
      symbol: '',
      interval: 'Daily',
      startDate: '',
      endDate: '',
    });
    const rules = {
      symbol: { required },
    };
    const v$ = useVuelidate(rules, state);

    // Set other reactive data
    const loading = ref(false);
    const dialog = ref(false);

    // This custom validation determines if the supposed "earlier"
    // date is actually earlier than the "later" date
    const validateEarlierDate = (earlier, later) => {
      const earlierDate = new Date(earlier);
      const laterDate = new Date(later);
      return earlierDate < laterDate;
    };

    // noSymbol and badDates are used to set whether the
    // button/submit method are disabled or not
    const noSymbol = computed(() => !state.symbol);
    const badDates = computed(() => {
      if (!state.startDate || !state.endDate) return false;
      return !validateEarlierDate(state.startDate, state.endDate);
    });
    const disabled = computed(() => noSymbol.value || badDates.value);
    const disabledText = computed(() => {
      if (!disabled.value) return '';
      if (noSymbol.value) return 'Please enter a symbol.';
      if (badDates.value)
        return 'The start date must be earlier than the end date.';
    });

    const submit = async () => {
      if (!disabled.value) {
        loading.value = true;
        try {
          // We will create a query string from an object including start and end dates,
          // so we first need to create the "query" object and populate with the relevant fields
          const query = {};
          if (!!state.startDate) query.start = state.startDate;
          if (!!state.endDate) query.end = state.endDate;
          const queryString = Object.keys(query)
            .filter((key) => !!query[key])
            .map((key) => {
              return (
                encodeURIComponent(key) + '=' + encodeURIComponent(query[key])
              );
            })
            .join('&');

          // Convert the human-readable interval format into one that yfinance prefers
          const interval =
            state.interval === 'Daily'
              ? '1d'
              : state.interval === 'Weekly'
              ? '1wk'
              : '1mo';

          // Create the url string and add the query if it exists
          let url = `http://localhost:8000/quote/${state.symbol}/${interval}`;
          if (queryString.length) url = `${url}?${queryString}`;
          const response = await fetch(url);
          const res = await response.json();

          // Next we will parse dates, and if the earliest available date is
          // LATER than the date that was input by the user then replace the
          // "startDate" value with the earliest available date
          // Also if either the startDate, endDate, or both were not included
          // then populate with data received from the server
          const dates = res.data.map((e) => e.date).sort();
          const formatDate = (d) => {
            const date = new Date(d);
            return date.toISOString().substr(0, 10);
          };
          if (
            !state.startDate ||
            !validateEarlierDate(dates[0], state.startDate)
          ) {
            state.startDate = formatDate(dates[0]);
          }
          if (!state.endDate)
            state.endDate = formatDate(dates[dates.length - 1]);

          // Set the candlestick data and volume data in the appropriate format
          // for ApexCharts, then pass the data up to be sent back down into the
          // Chart component
          const data = res.data.map((e) => ({
            x: new Date(e.date),
            y: e.data,
          }));
          const volData = res.data.map((e) => ({
            x: new Date(e.date),
            y: e.volume ?? 0,
          }));
          const payload = {
            series: [{ data }],
            symbol: state.symbol,
            interval: state.interval,
            volume: [{ name: 'volume', data: volData }],
          };
          emit('setData', payload);
        } catch (err) {
          console.log('err', err);
          dialog.value = true;
        } finally {
          loading.value = false;
        }
      }
    };

    return {
      state,
      intervals,
      disabled,
      disabledText,
      submit,
      loading,
      dialog,
      v$,
    };
  },
});
</script>

<style lang="scss" scoped>
.loader {
  border-top-color: #6366f1;
  -webkit-animation: spinner 1.5s linear infinite;
  animation: spinner 1.5s linear infinite;
}

@-webkit-keyframes spinner {
  0% {
    -webkit-transform: rotate(0deg);
  }
  100% {
    -webkit-transform: rotate(360deg);
  }
}

@keyframes spinner {
  0% {
    transform: rotate(0deg);
  }
  100% {
    transform: rotate(360deg);
  }
}
</style>
