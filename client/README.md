Now that the backend is essentially done we need to work on the client.
We'll be using [Vite](https://vitejs.dev/) to scaffold a Vue 3 project and will be adding Tailwind CSS to the project as well.
In order to build this part you need to have [Node.js](https://nodejs.org/en/) installed on your machine.

# Project Setup

## Vite

Following up from the [previous post](https://jeffpohlmeyer.com/candlestick-docker-fastapi-vue-part-1), we'll be creating this project alongside the server, but in a slightly different directory.
For those who don't want to go to the other post, the server was set up at `/path/to/server` so we'll assume that this is going to be set up at `/path/to/client`
To set up a Vite project we'll type the following

```bash
cd /path/to/
npm init vite client
```

If you use Yarn then you likely already know how to do this part.
You will have two options within the Vite setup:

- Which framework you want to use (Vanilla, Vue, React, etc)
- Whether you want to use TypeScript or not

We will choose a Vue project and use JavaScript.
![img.png](img.png)
Once you've run the Vite scaffolding you'll simply run

```bash
cd client
npm install
```

to finish creation of the project.

## Tailwind

Per the [documentation](https://tailwindcss.com/docs/guides/vue-3-vite#setting-up-tailwind-css) we'll run the following commands

```bash
npm install -D tailwindcss@latest postcss@latest autoprefixer@latest
npx tailwindcss init -p
```

which will install the necessary dev dependencies and scaffold a tailwind project.
Again, per the instructions, we will modify the `tailwind.config.js` file to look in specific files to remove unused CSS in production.

```javascript
// tailwind.config.js
module.exports = {
  mode: 'jit',
  purge: ['./index.html', './src/**/*.{vue,js,ts,jsx,tsx}'],
  darkMode: false, // or 'media' or 'class'
  theme: {
    extend: {},
  },
  variants: {
    extend: {},
  },
  plugins: [],
};
```

You'll notice one other line that we added at the very beginning was `mode: 'jit'` which runs the Just-In-Time compiler for tailwind, which allows us to create variants on the fly, among other things.
We then need to create a base css file and place it at `src/index.css`, and inside of it we add

```css
/* ./src/index.css */
@tailwind base;
@tailwind components;
@tailwind utilities;
```

Finally we simply update `src/main.js` to include this newly created css file and have it pull in all of Tailwind's classes.
Here is the app before including Tailwind
![app-before-tailwind.png](app-before-tailwind.png)

```javascript
// src/main.js
import { createApp } from 'vue';
import App from './App.vue';
import './index.css';

createApp(App).mount('#app');
```

Now we can go back to the terminal, run `npm run dev` and we should see our fully scaffolded project using Tailwind styles.
![app-after-tailwind.png](app-after-tailwind.png)

## Extra dependencies

There are a few things I always like to install in client projects

- eslint
- prettier
- lint-staged
- heroicons
- headlessui

The last two are because we're using Tailwind and it's just easier to incorporate those.
In order to install these we simply run.

```bash
npm i -D eslint eslint-plugin-prettier eslint-plugin-vue prettier lint-staged @headlessui/vue @heroicons/vue
```

Then once these are installed we need to create `.eslintrc.js` and `.prettierrc.js` files at the root of the project (i.e. above the `src` directory).

```javascript
// .eslintrc.js

module.exports = {
  root: true,
  env: {
    node: true,
  },
  extends: ['plugin:vue/vue3-essential', 'eslint:recommended', '@vue/prettier'],
  parserOptions: {
    parser: 'babel-eslint',
  },
  rules: {
    'no-console': process.env.NODE_ENV === 'production' ? 'warn' : 'off',
    'no-debugger': process.env.NODE_ENV === 'production' ? 'warn' : 'off',
  },
};

// .prettierrc.js
module.exports = {
  singleQuote: true,
  semi: true,
  htmlWhitespaceSensitivity: 'ignore',
};
```

The prettier settings are just my personal preferences, your mileage may vary.

# Project structure

The project will consist of two pieces

- The chart component that displays the data
- The selections component that receives user input for things like the ticker, interval, and start and end dates.

In the `App.vue` component we will hold the data and it will be updated from `Selections.vue` by emitting an event, and the necessary information will be passed down to `Chart.vue` as props.

## App.vue

`App.vue` will not care about the dates and will only need the symbol and interval to display in `Chart.vue` as informational pieces, so the initial setup of this main component will be

```vue
<template>
  <div>Hello world</div>
</template>

<script>
import { defineComponent, ref } from 'vue';

export default defineComponent({
  setup() {
    const series = ref([]);
    const symbol = ref('');
    const interval = ref('Daily');
    const volume = ref([]);

    return { series, symbol, interval, volume };
  },
});
</script>
```

The idea here is that the `series` and `volume` values will hold the actual data that was fetched from the API, and the `symbol` and `interval` values will be for display on the chart, as previously discussed.
The next step will be to create the `Selections.vue` component, which is where the user will input the ticker, interval, and dates; it will fetch data from the server; it will emit this data back up to be passed to `Chart.vue`.

## Selections.vue

The `Selections.vue` component will have, at minimum, four inputs (one of which will be a select tag), and a submit button.
We add simple labels and inputs for basic functionality, and just a couple of Tailwind margin and border classes for better visibility.

```vue
<template>
  <form class="ml-5" @submit.prevent="handleSubmit">
    <div class="my-1">
      <label for="symbol">Symbol</label>
      <input
        v-model="state.symbol"
        id="symbol"
        name="symbol"
        type="text"
        class="mx-2 border"
      />
    </div>
    <div class="my-1">
      <label for="start-date">Start Date</label>
      <input
        v-model="state.startDate"
        id="start-date"
        name="startDate"
        type="text"
        class="mx-2 border"
      />
    </div>
    <div class="my-1">
      <label for="end-date">End Date</label>
      <input
        v-model="state.endDate"
        id="end-date"
        name="endDate"
        type="text"
        class="mx-2 border"
      />
    </div>
    <div class="my-1">
      <label for="interval">Interval</label>
      <select v-model="state.interval" id="interval" class="mx-2 border">
        <option v-for="choice in intervals" :key="choice" :name="choice">
          {{ choice }}
        </option>
      </select>
    </div>
    <button type="submit" class="border">Get Chart</button>
  </form>
</template>

<script>
import { defineComponent, reactive } from 'vue';

export default defineComponent({
  setup() {
    const intervals = ['Daily', 'Weekly', 'Monthly'];

    const state = reactive({
      symbol: '',
      interval: 'Daily',
      startDate: '',
      endDate: '',
    });

    const handleSubmit = () => {
      console.log('triggered handleSubmit');
    };

    return {
      intervals,
      state,
      handleSubmit,
    };
  },
});
</script>
```

We then update `App.vue` via inclusion of `Selections.vue`

```vue
<template>
  <div class="h-screen">
    <Selections />
  </div>
</template>

<script>
import { defineComponent, ref } from 'vue';
import Selections from './components/Selections.vue';

export default defineComponent({
  components: { Selections },
  setup() {
    const series = ref([]);
    const symbol = ref('');
    const interval = ref('Daily');
    const volume = ref([]);

    return { series, symbol, interval, volume };
  },
});
</script>
```

And we see the result of this is the not-so-beautiful image below.
In the next article we'll create custom input and select components and incorporate them into the `Selections.vue` component.

# Part 3

This short article will continue along what was alluded to in [part 2](https://jeffpohlmeyer.com/candlestick-docker-fastapi-vue-part-2).  
Within `Selections.vue` we have three input elements and one select element that are used to receive input regarding stock selection.
We would like to have uniform styling and will be implementing things like input validation so it make sense to compartmentalize these components.
Also, what the hell is the point of using Vue if we're not going to do something like this?

## Custom `JVPInput.vue` Component

We start by creating a simple, generic component

```vue
<template>
  <div>
    <label :for="id">{{ label }}</label>
    <input
      :value="modelValue"
      :type="type"
      :name="id"
      :id="id"
      :placeholder="placeholder"
      class="mx-2 border"
      @input="updateValue"
    />
  </div>
</template>

<script>
import { defineComponent } from 'vue';
import inputProps from '../utils/input-props';

export default defineComponent({
  props: {
    type: {
      type: String,
      required: false,
      default: 'text',
    },
    placeholder: {
      type: String,
      required: false,
    },
    ...inputProps,
  },
  emits: ['update:modelValue'],
  setup(props, { emit }) {
    // This is simply cleaner than putting emit code in the HTML
    const updateValue = (e) => emit('update:modelValue', e.target.value);

    return { updateValue };
  },
});
</script>
```

The functionality of the component is fairly simple: split up the `v-model` directive into `:value` and `@input` functionality, and use passed-in props for the `type`, `id`, and `name`.

We can see that it looks like some information is missing, namely the `modelValue`, `id`, and `label` values that are referenced within the `template` tag.
These can be found in the `inputProps` object, which is defined in a separate file as

```javascript
// input-props.js

export default {
  id: {
    type: String,
    required: true,
  },
  modelValue: {
    required: true,
  },
  label: {
    type: String,
    required: true,
  },
  hint: {
    type: String,
    required: false,
    default: '',
  },
};
```

The `hint` that is included in `input-props.js` is something that will be used later.

## Custom `JVPSelect.vue` Component

In a similar manner, but somewhat simpler, we create the `JVPSelect.vue` component

```vue
<template>
  <div>
    <label :for="id">{{ label }}</label>
    <select :value="item" :id="id" class="mx-2 border" @input="updateItem">
      <option
        v-for="option in options"
        :key="option"
        :name="option"
        :selected="modelValue"
      >
        {{ option }}
      </option>
    </select>
  </div>
</template>

<script>
import { defineComponent, computed } from 'vue';
import inputProps from '../utils/input-props';

export default defineComponent({
  props: {
    options: {
      type: Array,
      required: true,
    },
    ...inputProps,
  },
  emits: ['update:modelValue'],
  setup(props, { emit }) {
    const item = computed(() => props.modelValue);
    const updateItem = (e) => emit('update:modelValue', e.target.value);
    return { item, updateItem };
  },
});
</script>
```

Like the `JVPInput.vue` component, this is simply moving the functionality that existed in `Selections.vue` into its own component.

### Updating `Selections.vue`

Now with these two components created we will update `Selections.vue` to utilize them.
We then update `Selections.vue` to use this component instead of the generic input component.

```vue
<template>
  <form class="ml-5" @submit.prevent="handleSubmit">
    <div class="my-1">
      <JVPInput
        v-model="state.symbol"
        label="Symbol"
        id="symbol"
        name="symbol"
        type="text"
        placeholder="eg. MSFT"
      />
    </div>
    <div class="my-1">
      <JVPInput
        v-model="state.startDate"
        label="Start Date"
        id="start-date"
        name="startDate"
        type="text"
      />
    </div>
    <div class="my-1">
      <JVPInput
        v-model="state.endDate"
        label="End Date"
        id="end-date"
        name="endDate"
        type="text"
      />
    </div>
    <div class="my-1">
      <JVPSelect
        v-model="state.interval"
        label="Interval"
        id="interval"
        :options="intervals"
      />
    </div>
    <button type="submit" class="border">Get Chart</button>
  </form>
</template>

<script>
import { defineComponent, reactive } from 'vue';
import JVPInput from './JVPInput.vue';
import JVPSelect from './JVPSelect.vue';

export default defineComponent({
  components: { JVPInput, JVPSelect },
  setup() {
    const intervals = ['Daily', 'Weekly', 'Monthly'];

    const state = reactive({
      symbol: '',
      interval: 'Daily',
      startDate: '',
      endDate: '',
    });

    const handleSubmit = () => {
      console.log('triggered handleSubmit');
    };

    return {
      intervals,
      state,
      handleSubmit,
    };
  },
});
</script>
```

and the app will look no different than before, which is the goal, but it will make further customization much easier.

## Styling

As we saw in part 2, the general app look is fairly ugly. We'll show it again here for reference.
![img_1.png](img_1.png)
We want to add some Tailwind styles to clean this up a little. In regard to the `JVPSelect.vue` component it won't make much difference than if we had left functionality in the `Selections.vue` component, but for organization it's better this way.

### `JVPSelect.vue`

We'll add simple font styling to the `label`:

- block
- text-sm
- font-medium
- text-gray-700

and slightly more complex styling to the actual `<select>` tag:

- block
- w-full
- pl-3
- pr-10
- py-2
- mt-1
- text-base
- border-gray-300
- focus:outline-none
- focus:ring-indigo-500
- focus:border-indigo-500
- sm:text-sm
- rounded-md

To see what each of these classes do to the element I encourage you to check out the [Tailwind docs](https://tailwindcss.com/docs).
Full disclosure, though, I have purchased a license to [Tailwind UI](https://tailwindui.com/) so a lot of this came from there because I'm terrible when it comes to design independently.
Now, the updated `JVPSelect.vue` component looks like this

```vue
<template>
  <div>
    <label :for="id" class="block text-sm font-medium text-gray-700">
      {{ label }}
    </label>
    <select
      :value="item"
      :id="id"
      class="
        mt-1
        block
        w-full
        pl-3
        pr-10
        py-2
        text-base
        border-gray-300
        focus:outline-none focus:ring-indigo-500 focus:border-indigo-500
        sm:text-sm
        rounded-md
      "
      @input="updateItem"
    >
      <option
        v-for="option in options"
        :key="option"
        :name="option"
        :selected="modelValue"
      >
        {{ option }}
      </option>
    </select>
  </div>
</template>

<script>
import { defineComponent, computed } from 'vue';
import inputProps from '../utils/input-props';

export default defineComponent({
  props: {
    options: {
      type: Array,
      required: true,
    },
    ...inputProps,
  },
  emits: ['update:modelValue'],
  setup(props, { emit }) {
    const item = computed(() => props.modelValue);
    const updateItem = (e) => emit('update:modelValue', e.target.value);
    return { item, updateItem };
  },
});
</script>
```

### `JVPInput.vue`

This component is going to be slightly more complicated.
One of the reasons for this is because we're going to be handling input validation in the `JVPInput.vue` component so we want to have `<p>` tag to display error messages or hints (remember the `hint` element in `input-props.js`???).
We want the labels to match what we already created for `JVPSelect.vue`, though, so that will be the same.
We will also wrap the `<input>` in a `div` element to make alignment a bit better as well as placement of any messages.
To this `div` we will add just a couple of classes:

- mt-1
- relative
- rounded-md
- shadow-sm

and then to the actual `input` element we will add

- block
- w-full
- sm:text-sm
- rounded-md
- shadow-sm

Now the `JVPInput.vue` component looks like

```vue
<template>
  <div>
    <label :for="id" class="block text-sm font-medium text-gray-700">
      {{ label }}
    </label>
    <div class="mt-1 relative rounded-md shadow-sm">
      <input
        :value="modelValue"
        :type="type"
        :name="id"
        :id="id"
        class="block w-full sm:text-sm rounded-md shadow-sm"
        @input="updateValue"
      />
    </div>
  </div>
</template>

<script>
import { defineComponent } from 'vue';
import inputProps from '../utils/input-props';

export default defineComponent({
  props: {
    type: {
      type: String,
      required: false,
      default: 'text',
    },
    placeholder: {
      type: String,
      required: false,
    },
    ...inputProps,
  },
  emits: ['update:modelValue'],
  setup(props, { emit }) {
    // This is simply cleaner than putting emit code in the HTML
    const updateValue = (e) => emit('update:modelValue', e.target.value);

    return { updateValue };
  },
});
</script>
```

And in order to make the actual app look half decent, we'll add a `bg-gray-200` class to the main `div` in `App.vue` and a `px-4` class to the `<Selections />` element in `App.vue`

```vue
<template>
  <div class="h-screen bg-gray-200">
    <Selections class="px-4" />
  </div>
</template>
```

and the app now looks like
![img_2.png](img_2.png)
which is still objectively terrible, but we're making progress.
The benefit of what we've done in this step is that we will be able to compartmentalize the error display in the `JVPInput.vue` component and it will keep `Selections.vue` relatively clean.

In the next article we'll add input validation to the three `JVPInput.vue` elements, add error and hint message display, and add dynamic styling of the component itself for when it is in an error state.

# Part 4

In the _last article_ we created custom `JVPSelect` and `JVPInput` components that look horrendous and also that have no data validation.
In this article we will add input validation using a third-party library called [Vuelidate](https://vuelidate-next.netlify.app/).

## Initial setup

We will be instantiating the `Vuelidate` object in `Selections.vue` instead of in `JVPInput.vue`.
We do this because the `JVPInput` component is, in effect, simply a wrapper.
We want to be able to use validation, but the rules and validation state for the purposes of form submission need to reside where the full form data resides.
The first thing we need to do is install Vuelidate

```bash
npm install @vuelidate/core @vuelidate/validators
```

From here we can either incorporate it globally in the project or import it into each component we want to use it.
We will use Vuelidate in the latter way.
We first import the library and necessary validators into our component

```javascript
import useVuelidate from '@vuelidate/core';
import { required, maxLength } from '@vuelidate/validators';
```

Then we instantiate the object and set the validation rules for the `symbol` attribute of the form

```javascript
const rules = {
  symbol: { required, maxLength: maxLength(5) },
};
const v$ = useVuelidate(rules, state);
```

where the `state` element is the `reactive` element that we've already set in the component.
The above rules set the `symbol` attribute to be required and to be no longer than 5 characters, though you can set it to whatever you want.

### Custom validators

We also want to check that if we've included data for both the `startDate` and `endDate` attributes that the former is earlier than the latter.

We first need to extend the `rules` that were initially created before

```javascript
const rules = {
  symbol: { required, maxLength: maxLength(5) },
  startDate: {
    validateDateFormat,
    mustBeEarlierDate,
  },
  endDate: {
    validateDateFormat,
  },
};
const v$ = useVuelidate(rules, state, { $lazy: true });
```

The first thing we want to do is first check to see if the value passed in is a valid date.

```javascript
const checkDateFormat = (param) => {
  if (!param) return true;
  return new Date(param).toString() !== 'Invalid Date';
};

const validateDateFormat = helpers.withMessage(
  'Please enter a valid date.',
  checkDateFormat
);
```
The `checkDateFormat` function follows methodology in the [Custom error messages](https://vuelidate-next.netlify.app/custom_validators.html#custom-error-messages) documentation on the Vuelidate docs.  

Then we want to check that the value passed in is earlier than the `reactive` state's `endDate` value.

```javascript
const mustBeEarlierDate = helpers.withMessage(
  'Start date must be earlier than end date.',
  (value) => {
    const endDate = computed(() => state.endDate);
    if (!value || !endDate.value) return true;
    if (!checkDateFormat(endDate.value)) return true;
    return new Date(value) < new Date(endDate.value)
  }
);
```

The `mustBeEarlierDate` function follows methodology in the [Passing extra properties to validators](https://vuelidate-next.netlify.app/custom_validators.html#passing-extra-properties-to-validators) documentation on the Vuelidate docs.
We need to be careful, though, as we don't care about this validation if either of the dates is not included, but _only_ if both are set.

We can now check to see that the functionality works properly by inputting valid and invalid values to the form and clicking the `Get Chart` button.
We should see the `triggered handleSubmit` text any time we click the button except when both the start and end date being included **and** the start date is not strictly less than the end date.

The updated `Selections.vue` component should now look like this

```vue
<template>
  <form class="ml-5" @submit.prevent="handleSubmit">
    <div class="my-1">
      <JVPInput
        v-model="state.symbol"
        label="Symbol"
        id="symbol"
        name="symbol"
        type="text"
        placeholder="eg. MSFT"
        :vuelidate="v$.symbol"
      />
    </div>
    <div class="my-1">
      <JVPInput
        v-model="state.startDate"
        label="Start Date"
        id="start-date"
        name="startDate"
        type="text"
        :vuelidate="v$.startDate"
      />
    </div>
    <div class="my-1">
      <JVPInput
        v-model="state.endDate"
        label="End Date"
        id="end-date"
        name="endDate"
        type="text"
        :vuelidate="v$.endDate"
      />
    </div>
    <div class="my-1">
      <JVPSelect
        v-model="state.interval"
        label="Interval"
        id="interval"
        :options="intervals"
      />
    </div>
    <button type="submit" class="border-4 border-indigo-500">Get Chart</button>
  </form>
</template>

<script>
import { defineComponent, reactive, computed } from 'vue';
import useVuelidate from '@vuelidate/core';
import { required, maxLength, helpers } from '@vuelidate/validators';
import JVPInput from './JVPInput.vue';
import JVPSelect from './JVPSelect.vue';

export default defineComponent({
  components: { JVPInput, JVPSelect },
  setup() {
    const intervals = ['Daily', 'Weekly', 'Monthly'];

    const state = reactive({
      symbol: '',
      interval: 'Daily',
      startDate: '',
      endDate: '',
    });

    const mustBeEarlierDate = helpers.withMessage(
      'Start date must be earlier than end date.',
      (value) => {
        const endDate = computed(() => state.endDate);
        if (!value || !endDate.value) return true;
        if (!checkDateFormat(endDate.value)) return true;
        return new Date(value) < new Date(endDate.value);
      }
    );

    const checkDateFormat = (param) => {
      if (!param) return true;
      return new Date(param).toString() !== 'Invalid Date';
    };

    const validateDateFormat = helpers.withMessage(
      'Please enter a valid date.',
      checkDateFormat
    );

    const rules = {
      symbol: { required, maxLength: maxLength(5) },
      startDate: {
        validateDateFormat,
        mustBeEarlierDate,
      },
      endDate: {
        validateDateFormat,
      },
    };
    const v$ = useVuelidate(rules, state);

    const disabled = computed(() => {
      return v$.value.$invalid;
    });

    const handleSubmit = () => {
      v$.value.$validate();
      if (!v$.value.$invalid) {
        console.log('triggered handleSubmit');
      }
    };

    return {
      intervals,
      state,
      disabled,
      v$,
      handleSubmit,
    };
  },
});
</script>
```

## Display error messages

This is all fine and good, but we need to somehow let the user know when the form is in an error state.
In order to do this we need to add `v$` to the return of the `setup` function in the component so that we can access it in the template and pass it down to the `JVPInput.vue` components.
Next we need to update the props in the `JVPInput.vue` component to include this new object, which we'll simply call `vuelidate`.
The props for this component should now look like

```javascript
props: {
  type: {
    type: String,
    required: false,
    default: 'text',
  },
  placeholder: {
    type: String,
    required: false,
  },
  vuelidate: {
    type: Object,
    required: false,
    default: () => ({})
  },
  ...inputProps,
},
```
and we'll add in an extra attribute to each `JVPInput` instance in `Selections.vue`, calling the specific element of the `v$` object.
It will look something like
```html
<JVPInput
  v-model="state.startDate"
  label="Start Date"
  id="start-date"
  name="startDate"
  type="text"
  :vuelidate="v$.startDate"
/>
```
Once this is done we can then set some computed properties in the `JVPInput.vue` component to check if the input is in an error state and, if it is, create a dynamic `errorText` element.
```javascript
// Vuelidate is used as a validation library.
// We use built-in functionality to determine if any rules are violated
// as well as display of the associated error text
const isError = computed(() => props.vuelidate.$error);
const errorText = computed(() => {
  const messages =
    props.vuelidate.$errors?.map((err) => err.$message) ?? [];
  return messages.join(' ');
});
```
We then want to add the `isError` and `errorText` elements to the `return` statement in the `setup` function in `JVPInput.vue` and add in some markup to display the text if and only if there is an error.
We can add in a simple `<p>` tag to conditionally display the error messages, and the updated `JVPInput.vue` component should look like
```vue
<template>
  <div>
    <label :for="id" class="block text-sm font-medium text-gray-700">
      {{ label }}
    </label>
    <div class="mt-1 relative rounded-md shadow-sm">
      <input
        :value="modelValue"
        :type="type"
        :name="id"
        :id="id"
        class="block w-full sm:text-sm rounded-md shadow-sm"
        @input="updateValue"
      />
    </div>
    <p v-if="isError">{{ errorText }}</p>
  </div>
</template>

<script>
import { defineComponent, computed } from 'vue';
import inputProps from '../utils/input-props';

export default defineComponent({
  props: {
    type: {
      type: String,
      required: false,
      default: 'text',
    },
    placeholder: {
      type: String,
      required: false,
    },
    vuelidate: {
      type: Object,
      required: false,
      default: () => ({}),
    },
    ...inputProps,
  },
  emits: ['update:modelValue'],
  setup(props, { emit }) {
    // This is simply cleaner than putting emit code in the HTML
    const updateValue = (e) => emit('update:modelValue', e.target.value);

    // Vuelidate is used as a validation library.
    // We use built-in functionality to determine if any rules are violated
    // as well as display of the associated error text
    const isError = computed(() => props.vuelidate.$error);
    const errorText = computed(() => {
      const messages =
        props.vuelidate.$errors?.map((err) => err.$message) ?? [];
      console.log(messages)
      return messages.join(' ');
    });

    return { updateValue, isError, errorText };
  },
});
</script>
```
Now we can see that if we don't include a symbol, set the date fields to be random text, and click the `Get Chart` button then we should see something that looks like

In the next article we'll add in hint text, then we'll add in some conditional styling based on whether the form is in an error state or not.


# Part 5
In the [last article](https://jeffpohlmeyer.com/candlestick-docker-fastapi-vue-part-4) we added validation to the `JVPInput.vue` components using a library called Vuelidate.
Upon an invalid entry to any of these components, we had a line of text appear below the input to indicate that it was invalid.
Now that we have a place to put error text, we should make use of that space in case we want a hint to go there.  

We have already included the `hint` prop in our `input-props.js` file, so we don't need to add anything there.
Now all we need to do to pass the hint to the `JVPInput` component is add it anywhere we want it displayed.
For example, we want to tell the user that the `symbol` attribute is required and the dates are optional, so we would pass these in as hints.
```vue
<div class="my-1">
  <JVPInput
    v-model="state.symbol"
    label="Symbol"
    id="symbol"
    name="symbol"
    type="text"
    placeholder="eg. MSFT"
    :vuelidate="v$.symbol"
    hint="Required, less than 6 characters"
  />
</div>
<div class="my-1">
  <JVPInput
    v-model="state.startDate"
    label="Start Date"
    id="start-date"
    name="startDate"
    type="text"
    :vuelidate="v$.startDate"
    hint="Optional"
  />
</div>
<div class="my-1">
  <JVPInput
    v-model="state.endDate"
    label="End Date"
    id="end-date"
    name="endDate"
    type="text"
    :vuelidate="v$.endDate"
    hint="Optional"
  />
</div>
```
### Hint/error logic
The next thing we need to do is incorporate the hint vs. error logic within the component script itself.
We will be using the same space to display hints and errors, but we don't want to display a hint when an input is in an error state.
We also want the text displayed to be dynamic depending on the state of the input.
To that end, we'll add another computed property to `JVPInput.vue`
```javascript
const hintText = computed(() => {
  if (errorText.value.length > 0) return errorText.value;
  if (!!props.hint) return props.hint;
  return '';
})
```
What this little property does is it displays any error messages, if they exist.
If they don't, but a hint was passed down as a prop, then display the hint, otherwise just remain empty.
We can then add
```javascript
const hasHint = computed(() => !!hintText.value.length);
```
which will be truthy whether there is a hint _or_ there are any error messages.
Now the error text markup will be replaced with
```html
<p v-if="hasHint">{{ hintText }}</p>
```
after having included both `hasHint` and `hintText` in the `return` section of the `setup` function.

### Styling
Now we need to add some styling.
The app still looks pretty horrendous so we need to clean it up a bit.
The first thing we notice, though, is that there seems to be no highlighting around the `JVPSelect.vue` element.
If we think back a bit, we included `focus:ring-indigo-500` and `focus:border-indigo-500` as classes on this element but as we tab through we don't see any of those.
The reason for this is because we need to install
```bash
npm i @tailwindcss/forms
```
and include an extra plugin for Tailwind
```javascript
// tailwind.config.js
module.exports = {
  mode: 'jit',
  purge: ['./index.html', './src/**/*.{vue,js,ts,jsx,tsx}'],
  darkMode: false, // or 'media' or 'class'
  theme: {
    extend: {},
  },
  variants: {
    extend: {},
  },
  plugins: [require('@tailwindcss/forms')], // <-- *** New line ***
}
```
By simply adding this plugin the form looks a bit better and we can see that in the focus state the `JVPSelect.vue` component has the correct highlighting.

What we want to do next for the `JVPInput.vue` component is create a sort of dynamic class that will display certain properties when in a valid state and other properties in an error state.
```javascript
// This is solely to style the input based on whether it is in an error state or not
const dynamicClass = computed(() => {
  // This is to remove padding on the right for the built-in calendar icon when using a date type
  let val = props.type === 'date' ? '' : 'pr-10';
  return isError.value
    ? `${val} border-red-300 text-red-900 placeholder-red-300 focus:outline-none focus:ring-red-500 focus:border-red-500`
    : `${val} focus:ring-indigo-500 focus:border-indigo-500 border-gray-300`;
});
```
We will then update the class of the hint slightly and dynamically set the `id` value for the hint
```javascript
// The "hint" text will display any necessary hints as well as any error messages.
// Styling and values of said hint text are primarily based on whether an input is in an error state.
const hintClass = computed(() =>
  isError.value ? 'text-red-600' : 'text-gray-500'
);
const hintId = computed(() =>
  isError.value ? `${props.id}-error` : `${props.id}-input`
);

```
We then pass the `dynamicClass` variable into the `return` statement of the `setup` function and add an extra line to the `input` tag
```html
<input
  :value="modelValue"
  :type="type"
  :name="id"
  :id="id"
  class="block w-full sm:text-sm rounded-md shadow-sm"
  :class="dynamicClass"
  @input="updateValue"
/>
```
What this will do is always set the class to be `block w-full sm:text-sm rounded-md shadow-sm` regardless of the error state, but then it also adds on the extra elements defined in `dynamicClass`, which are dependent on the error state of the `input`.  

We then want to add a bit of extra styling to the hint text itself just to give it a secondary focus.
```html
<p v-if="hasHint" class="mt-0 text-sm" :class="hintClass" :id="hintId">
  {{ hintText }}
</p>
```
after having added the `hintClass` and `hintId` elements to the `return` statement of the `setup` function, of course.  

### Finishing touches on `JVPInput.vue`
To tie off the loose ends on the `JVPInput.vue` component there are just a few more things we want to add
- A couple of `aria` attributes
- Tell `vuelidate` to validate each input on a `blur` event
- Add autofocus as a prop and bind it to the input
```html
<input
  :value="modelValue"
  :type="type"
  :name="id"
  :id="id"
  class="block w-full sm:text-sm rounded-md shadow-sm"
  :class="dynamicClass"
  :aria-invalid="isError"
  :aria-describedby="hintId"
  :autofocus="autofocus"
  @input="updateValue"
  @blur="vuelidate.$touch"
/>
```
You can see in the code snippet above we're accessing `vuelidate` and `autofocus` directly instead of via the `props`.
In order to do this we simply need to update the `return` statement like so
```javascript
return {
  hasHint,
  hintText,
  hintClass,
  hintId,
  dynamicClass,
  isError,
  autofocus: props.autofocus,
  vuelidate: props.vuelidate,
  updateValue,
};
```
To tie a final bow on this component, we will actually update two things in `Selections.vue`.
You'll notice when creating the `dynamicClass` variable we allowed for a class of `pr-10` if the `type` prop passed in is "date".
This will automatically add in the calendar icon, so in `Selections.vue` we'll change the type of `startDate` and `endDate` to be "date".

## Summary
Now that all of that is done, we've _nearly_ finished with the `form` components.
What we will do in the next, short, article will be adding in svg icons to the project so that we can easily include them in our code wherever we need.
We will also style the button because the rest of the form is starting to look nice and clean and the button is still pretty ugly.
For the purpose of copy-pasting, the two components we updated in this section are `Selections.vue` and `JVPInput.vue`, the updated versions of both of which are presented now.
#### ```Selections.vue```
```vue
<template>
  <form class="ml-5" @submit.prevent="handleSubmit">
    <div class="my-1">
      <JVPInput
        v-model="state.symbol"
        label="Symbol"
        id="symbol"
        name="symbol"
        type="text"
        placeholder="eg. MSFT"
        :vuelidate="v$.symbol"
        hint="Required, less than 6 characters"
        :autofocus="true"
      />
    </div>
    <div class="my-1">
      <JVPInput
        v-model="state.startDate"
        label="Start Date"
        id="start-date"
        name="startDate"
        type="date"
        :vuelidate="v$.startDate"
        hint="Optional"
      />
    </div>
    <div class="my-1">
      <JVPInput
        v-model="state.endDate"
        label="End Date"
        id="end-date"
        name="endDate"
        type="date"
        :vuelidate="v$.endDate"
        hint="Optional"
      />
    </div>
    <div class="my-1">
      <JVPSelect
        v-model="state.interval"
        label="Interval"
        id="interval"
        :options="intervals"
      />
    </div>
    <button type="submit" class="border-4 border-indigo-500">Get Chart</button>
  </form>
</template>

<script>
import { defineComponent, reactive, computed } from 'vue';
import useVuelidate from '@vuelidate/core';
import { required, maxLength, helpers } from '@vuelidate/validators';
import JVPInput from './JVPInput.vue';
import JVPSelect from './JVPSelect.vue';

export default defineComponent({
  components: { JVPInput, JVPSelect },
  setup() {
    const intervals = ['Daily', 'Weekly', 'Monthly'];

    const state = reactive({
      symbol: '',
      interval: 'Daily',
      startDate: '',
      endDate: '',
    });

    const mustBeEarlierDate = helpers.withMessage(
      'Start date must be earlier than end date.',
      (value) => {
        const endDate = computed(() => state.endDate);
        if (!value || !endDate.value) return true;
        if (!checkDateFormat(endDate.value)) return true;
        return new Date(value) < new Date(endDate.value);
      }
    );

    const checkDateFormat = (param) => {
      if (!param) return true;
      return new Date(param).toString() !== 'Invalid Date';
    };

    const validateDateFormat = helpers.withMessage(
      'Please enter a valid date.',
      checkDateFormat
    );

    const rules = {
      symbol: { required, maxLength: maxLength(5) },
      startDate: {
        validateDateFormat,
        mustBeEarlierDate,
      },
      endDate: {
        validateDateFormat,
      },
    };
    const v$ = useVuelidate(rules, state);

    const disabled = computed(() => {
      return v$.value.$invalid;
    });

    const handleSubmit = () => {
      v$.value.$validate();
      if (!v$.value.$invalid) {
        console.log('triggered handleSubmit');
      }
    };

    return {
      intervals,
      state,
      disabled,
      v$,
      handleSubmit,
    };
  },
});
</script>
```

#### ```JVPInput.vue```
```vue
<template>
  <div>
    <label :for="id" class="block text-sm font-medium text-gray-700">
      {{ label }}
    </label>
    <div class="mt-1 relative rounded-md shadow-sm">
      <input
        :value="modelValue"
        :type="type"
        :name="id"
        :id="id"
        class="block w-full sm:text-sm rounded-md shadow-sm"
        :class="dynamicClass"
        :aria-invalid="isError"
        :aria-describedby="hintId"
        :autofocus="autofocus"
        @input="updateValue"
        @blur="vuelidate.$touch"
      />
    </div>
    <p v-if="hasHint" class="mt-0 text-sm" :class="hintClass" :id="hintId">
      {{ hintText }}
    </p>
  </div>
</template>

<script>
import { defineComponent, computed } from 'vue';
import inputProps from '../utils/input-props';

export default defineComponent({
  props: {
    type: {
      type: String,
      required: false,
      default: 'text',
    },
    placeholder: {
      type: String,
      required: false,
    },
    vuelidate: {
      type: Object,
      required: false,
      default: () => ({}),
    },
    autofocus: {
      type: Boolean,
      required: false,
      default: false
    },
    ...inputProps,
  },
  emits: ['update:modelValue'],
  setup(props, { emit }) {
    // This is simply cleaner than putting emit code in the HTML
    const updateValue = (e) => emit('update:modelValue', e.target.value);

    // Vuelidate is used as a validation library.
    // We use built-in functionality to determine if any rules are violated
    // as well as display of the associated error text
    const isError = computed(() => props.vuelidate.$error);
    const errorText = computed(() => {
      const messages =
        props.vuelidate.$errors?.map((err) => err.$message) ?? [];
      return messages.join(' ');
    });

    // This is solely to style the input based on whether it is in an error state or not
    const dynamicClass = computed(() => {
      // This is to remove padding on the right for the built-in calendar icon when using a date type
      let val = props.type === 'date' ? '' : 'pr-10';
      return isError.value
        ? `${val} border-red-300 text-red-900 placeholder-red-300 focus:outline-none focus:ring-red-500 focus:border-red-500`
        : `${val} focus:ring-indigo-500 focus:border-indigo-500 border-gray-300`;
    });

    // The "hint" text will display any necessary hints as well as any error messages.
    // Styling and values of said hint text are primarily based on whether an input is in an error state.
    const hintClass = computed(() =>
      isError.value ? 'text-red-600' : 'text-gray-500'
    );
    const hintId = computed(() =>
      isError.value ? `${props.id}-error` : `${props.id}-input`
    );

    const hintText = computed(() => {
      if (errorText.value.length > 0) return errorText.value;
      if (!!props.hint) return props.hint;
      return '';
    });

    const hasHint = computed(() => !!hintText.value.length);

    return {
      hasHint,
      hintText,
      hintClass,
      hintId,
      dynamicClass,
      isError,
      autofocus: props.autofocus,
      vuelidate: props.vuelidate,
      updateValue,
    };
  },
});
</script>
```
and the updated form looks much better


# Part 6
In the [last article](https://jeffpohlmeyer.com/candlestick-docker-fastapi-vue-part-5) we styled the form a bit better and added conditional styling based on the data validation from Vuelidate.
The button still looks pretty ugly, though, so we'll style that in this article as well as add in any necessary functionality.
We'll also add in some icon functionality to make it easy to include them wherever we need, as well.

## Styling the button
We initially added in "placeholder" classes so the button actually looked like something.
We'll remove the `border-4` and `border-indigo-500` classes and replace them with the following:
- `w-full` -> take up the full width of the parent container
- `h-12` -> fixing height, this will be beneficial for a loading icon later
- `px-6` -> some horizontal padding
- `mt-6` -> margin on the top to clear it from the `JVPSelect.vue` component
- `lg:mt-0` -> removing said margin when on `lg` or `xl` [breakpoints](https://tailwindcss.com/docs/breakpoints), as declared by Tailwind
- `rounded-lg` -> just rounding the corners a bit to look nicer
- `bg-indigo-700` -> background coloring
- `text-indigo-100` -> a similar text shade to the background, but with enough contrast
- `transition-colors` -> a transition class that will only transition the color attributes that will be updated
- `duration-150` -> setting a duration for the aforementioned transitions
- `hover:bg-indigo-800` -> a slightly darker color on hover (this is where the `transition-colors` will have an affect)
- `focus:shadow-outline` -> a subtle outline when the button is focused, as in when tabbing through inputs
- `disabled:opacity-50` -> setting the opacity to be 50% if the button is disabled
- `disabled:cursor-not-allowed` -> disable the standard pointer cursor for a button when the button is disabled

### Button logic
In the previous article we didn't include any disabled functionality on the button because we wanted to include good feedback for error handling.
Now we can include disabled functionality, which we started in the previous article where we set up a computed property:
```javascript
const disabled = computed(() => {
  return v$.value.$invalid;
});
```
All we need to do now is add a dynamic `:disabled` property to the button in the template.
Now the button markup looks like this
```html
<button
  type="submit"
  class="
    w-full
    h-12
    px-6
    mt-6
    lg:mt-0
    rounded-lg
    bg-indigo-700
    text-indigo-100
    transition-colors
    duration-150
    hover:bg-indigo-800
    focus:shadow-outline
    disabled:opacity-50
    disabled:cursor-not-allowed
  "
  :disabled="disabled"
>
  Get Chart
</button>
```
and the form, with the disabled button, looks like
![](C:/Users/jeffp/Pictures/Screenshot hashnode button.png)

## Icons
We hold off on handling logic on a valid form submission until the next article because we first want to include display of icons.
We will use this functionality to add a loading spinner to the button while awaiting a response so it makes sense to handle this now.
We can use icons from libraries like [FontAwesome](https://fontawesome.com/), [Material Design Icons](https://materialdesignicons.com/), [Google Font Icons](https://fonts.google.com/icons), but since we're using Vue, and Tailwind CSS integrates very well with React and Vue (TailwindUI was built for those two frameworks), we can simply install [heroicons](https://heroicons.com/).
We open a terminal/command prompt and type
```bash
npm i -D @heroicons/vue
```
and we should have a set of free icons created by [https://twitter.com/steveschoger](Steve Schoger), who is a partner/designer at Tailwind Labs.
Now that we've installed the icons, we can import the icons we need.
### Exclamation
We want to add in a little warning icon in the `JVPInput.vue` component any time data validation fails.
In order to do this, we just need to import the component and register it
```javascript
import { defineComponent, computed } from 'vue';
import { ExclamationCircleIcon } from '@heroicons/vue/solid';
import inputProps from '../utils/input-props';

export default defineComponent({
  components: { ExclamationCircleIcon },
  props: {
  ...    
```
Then we can very simply add it, conditionally on error state, to the markup inside the `<div class="mt-1 relative..."` but after the actual `input` tag
```html
<div
  v-if="isError"
  class="absolute inset-y-0 right-0 flex items-center pointer-events-none"
  :class="type === 'date' ? 'pr-9' : 'pr-3'"
>
  <ExclamationCircleIcon
    class="h-5 w-5 text-red-500"
    aria-hidden="true"
  />
</div>
```
It is here that we see the importance of including the `relative` class on the wrapping div, because we want to absolutely position this icon inside of the input.
We also conditionally render the right-padding based on whether the input type is a date, because if it is a date it shows the calendar icon and we don't want to cover that.
Now an invalid input will include the exclamation icon as needed.
![](C:/Users/jeffp/Pictures/Screenshot hashnode button icon.png)

### Loading spinner
This is not _technically_ an icon, but we'll add it in the same section because it behaves similarly.
The first thing we need to do is add in an element called `loading` in the script itself.
It will be a simple boolean that will be false on initialization.
We then need to conditionally render either the loading spinner, if `loading === true`, or the previously set text, "Get Chart" if not.
Thus, the generic slot in the `<button>` element is replaced by
```html
<span
  v-if="loading"
  class="
    animate-spin-1.5
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
```
The `animate-spin-1.5` class is a custom class that we'll define in a minute, but the rest are all default Tailwind classes.
- `ease-linear` -> the linear transition-timing-function
- `rounded-full` -> makes the element a circle
- `border-4 border-t-4 border-gray-200` -> border styling around this empty element; this will be what is actually displayed
- `h-10 w-10` -> forcing a specific height and width
- `mx-auto` -> centering the element in its container
- `block` -> making the element a block-level (span is an inline element)

We then need to set up the custom `loader` class.
This is a simple addition of a `<style>` tag at the bottom of the component
```html
<style scoped>
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
```
We are setting a separate color for the top border, which will look like it's the only thing rotating.
Now to test this we can update `handleSubmit` with to look like
```javascript
const handleSubmit = () => {
  v$.value.$validate();
  if (!v$.value.$invalid) {
    loading.value = true;
    setTimeout(() => {
      console.log('triggered handleSubmit');
      loading.value = false
    }, 5000)
  }
}
```
We should now have a loader that is running for 5 seconds, and the console still logs "triggered handleSubmit" on a valid form submission.
In the next article we'll handle form submission properly and fetch the data from the FastAPI server that we previously set up.

## Code
As a reference, the updated `Selections.vue` and `JVPInput.vue` components should look like

`Selections.vue`
```vue
<template>
  <form class="ml-5" @submit.prevent="handleSubmit">
    <div class="my-1">
      <JVPInput
        v-model="state.symbol"
        label="Symbol"
        id="symbol"
        name="symbol"
        type="text"
        placeholder="eg. MSFT"
        :vuelidate="v$.symbol"
        hint="Required, less than 6 characters"
        :autofocus="true"
      />
    </div>
    <div class="my-1">
      <JVPInput
        v-model="state.startDate"
        label="Start Date"
        id="start-date"
        name="startDate"
        type="date"
        :vuelidate="v$.startDate"
        hint="Optional"
      />
    </div>
    <div class="my-1">
      <JVPInput
        v-model="state.endDate"
        label="End Date"
        id="end-date"
        name="endDate"
        type="date"
        :vuelidate="v$.endDate"
        hint="Optional"
      />
    </div>
    <div class="my-1">
      <JVPSelect
        v-model="state.interval"
        label="Interval"
        id="interval"
        :options="intervals"
      />
    </div>
    <button
      type="submit"
      class="w-full h-12 px-6 mt-6 lg:mt-0 rounded-lg bg-indigo-700 text-indigo-100 transition-colors duration-150 hover:bg-indigo-800 focus:shadow-outline disabled:opacity-50 disabled:cursor-not-allowed"
      :disabled="disabled"
    >
      <span
        v-if="loading"
        class="loader ease-linear rounded-full border-4 border-t-4 border-gray-200 h-10 w-10 mx-auto block"
      ></span>
      <span v-else>Get Chart</span>
    </button>
  </form>
</template>

<script>
import { defineComponent, reactive, ref, computed } from 'vue';
import useVuelidate from '@vuelidate/core';
import { required, maxLength, helpers } from '@vuelidate/validators';
import JVPInput from './JVPInput.vue';
import JVPSelect from './JVPSelect.vue';

export default defineComponent({
  components: { JVPInput, JVPSelect },
  setup() {
    const intervals = ['Daily', 'Weekly', 'Monthly'];

    const state = reactive({
      symbol: '',
      interval: 'Daily',
      startDate: '',
      endDate: '',
    });

    const mustBeEarlierDate = helpers.withMessage(
      'Start date must be earlier than end date.',
      (value) => {
        const endDate = computed(() => state.endDate);
        if (!value || !endDate.value) return true;
        if (!checkDateFormat(endDate.value)) return true;
        return new Date(value) < new Date(endDate.value);
      }
    );

    const checkDateFormat = (param) => {
      if (!param) return true;
      return new Date(param).toString() !== 'Invalid Date';
    };

    const validateDateFormat = helpers.withMessage(
      'Please enter a valid date.',
      checkDateFormat
    );

    const rules = {
      symbol: { required, maxLength: maxLength(5) },
      startDate: {
        validateDateFormat,
        mustBeEarlierDate,
      },
      endDate: {
        validateDateFormat,
      },
    };
    const v$ = useVuelidate(rules, state);

    const disabled = computed(() => {
      return v$.value.$invalid;
    });

    const loading = ref(false);

    const handleSubmit = () => {
      v$.value.$validate();
      if (!v$.value.$invalid) {
        loading.value = true;
        setTimeout(() => {
          console.log('triggered handleSubmit');
          loading.value = false;
        }, 5000);
      }
    };

    return {
      intervals,
      state,
      disabled,
      loading,
      v$,
      handleSubmit,
    };
  },
});
</script>

<style scoped>
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
```
`JVPInput.vue`
```vue
<template>
  <div>
    <label :for="id" class="block text-sm font-medium text-gray-700">
      {{ label }}
    </label>
    <div class="mt-1 relative rounded-md shadow-sm">
      <input
        :value="modelValue"
        :type="type"
        :name="id"
        :id="id"
        class="block w-full sm:text-sm rounded-md shadow-sm"
        :class="dynamicClass"
        :aria-invalid="isError"
        :aria-describedby="hintId"
        :autofocus="autofocus"
        @input="updateValue"
        @blur="vuelidate.$touch"
      />
      <div
        v-if="isError"
        class="absolute inset-y-0 right-0 flex items-center pointer-events-none"
        :class="type === 'date' ? 'pr-9' : 'pr-3'"
      >
        <ExclamationCircleIcon
          class="h-5 w-5 text-red-500"
          aria-hidden="true"
        />
      </div>
    </div>
    <p v-if="hasHint" class="mt-0 text-sm" :class="hintClass" :id="hintId">
      {{ hintText }}
    </p>
  </div>
</template>

<script>
import { defineComponent, computed } from 'vue';
import { ExclamationCircleIcon } from '@heroicons/vue/solid';
import inputProps from '../utils/input-props';

export default defineComponent({
  components: { ExclamationCircleIcon },
  props: {
    type: {
      type: String,
      required: false,
      default: 'text',
    },
    placeholder: {
      type: String,
      required: false,
    },
    vuelidate: {
      type: Object,
      required: false,
      default: () => ({}),
    },
    autofocus: {
      type: Boolean,
      required: false,
      default: false,
    },
    ...inputProps,
  },
  emits: ['update:modelValue'],
  setup(props, { emit }) {
    // This is simply cleaner than putting emit code in the HTML
    const updateValue = (e) => emit('update:modelValue', e.target.value);

    // Vuelidate is used as a validation library.
    // We use built-in functionality to determine if any rules are violated
    // as well as display of the associated error text
    const isError = computed(() => props.vuelidate.$error);
    const errorText = computed(() => {
      const messages =
        props.vuelidate.$errors?.map((err) => err.$message) ?? [];
      return messages.join(' ');
    });

    // This is solely to style the input based on whether it is in an error state or not
    const dynamicClass = computed(() => {
      // This is to remove padding on the right for the built-in calendar icon when using a date type
      let val = props.type === 'date' ? '' : 'pr-10';
      return isError.value
        ? `${val} border-red-300 text-red-900 placeholder-red-300 focus:outline-none focus:ring-red-500 focus:border-red-500`
        : `${val} focus:ring-indigo-500 focus:border-indigo-500 border-gray-300`;
    });

    // The "hint" text will display any necessary hints as well as any error messages.
    // Styling and values of said hint text are primarily based on whether an input is in an error state.
    const hintClass = computed(() =>
      isError.value ? 'text-red-600' : 'text-gray-500'
    );
    const hintId = computed(() =>
      isError.value ? `${props.id}-error` : `${props.id}-input`
    );

    const hintText = computed(() => {
      if (errorText.value.length > 0) return errorText.value;
      if (!!props.hint) return props.hint;
      return '';
    });

    const hasHint = computed(() => !!hintText.value.length);

    return {
      hasHint,
      hintText,
      hintClass,
      hintId,
      dynamicClass,
      isError,
      autofocus: props.autofocus,
      vuelidate: props.vuelidate,
      updateValue,
    };
  },
});
</script>
```

# Part 7
The next step in our journey is to hook up our frontend to the backend.
In the [last article](https://jeffpohlmeyer.com/candlestick-docker-fastapi-vue-part-6) we made things look a bit better and we set up some logic so that a loading spinner appears when we click on the `submit` button.
Now we need to use the `handleSubmit` method to actually fetch data from our server.

## Spin up the server
In case we don't recall from [Part 1](https://jeffpohlmeyer.com/candlestick-docker-fastapi-vue-part-1) of this series, our server is set up in a Python environment using `FastAPI`.
If our directory structure is like this
```
.
├── fast-api-vue-stock
│   ├── client
│   └── server
│       └── main.py
```
we can open a terminal/command prompt and type the following
```bash
cd /path/to/server
env\Scripts\activate
uvicorn main:app --reload
```
This assumes that we already have the same setup as was described in Part 1 of the tutorial.
By typing this then our server should be running at port 8000.

## Connecting to the server
### Create a querystring
For those who may not recall, the format of the url that we will be consuming in the backend is of the format `/quote/{ticker}/{interval}`.
Then, any date information, as it is optional, is passed in via query parameters in the format `YYYY-mm-dd`.
So, within the `handleSubmit` method in `Selections.vue` we first need to create a query object and add the start and end dates if they exist.
```javascript
const query = {}
if (!!state.startDate) query.start = state.startDate;
if (!!state.endDate) query.end = state.endDate;
```
Then, we can just map through the keys of the query and use the [encodeURIComponent](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/encodeURIComponent) built-in method to convert our dates into the correct format.
It should be noted that since we're only doing this with two values the method that will be presented below may be a little overkill, but the idea is that this method can be used for any number of query parameters so it's worth it to present.
```javascript
const queryString = Object.keys(query)
  .filter((key) => !!query[key])
  .map((key) => {
    return (
      `${encodeURIComponent(key)}=${encodeURIComponent(query[key])}`
    );
  })
  .join('&')
```
To see what this method does, let's use the following object as an example

```javascript
query = {
  "hello": "world",
  "hashnode": [1,2,3],
  "vue": {
    "is": "cool"
  },
  "fastapi": "is as well"
}
```
If we then look at the resulting string, we get
`'hello=world&hashnode=1%2C2%2C3&vue=%5Bobject%20Object%5D&fastapi=is%20as%20well'`
and we notice that there is an `object%20Object` where the value for the `vue` key should be.
This shows us that we can't just use this method for any deeply nested structures, but it instead works for simple key-value stores.
If we instead set 
```javascript
query = {
  "hello": "world",
  "hashnode": [1,2,3],
  "vue": ["is", "cool"],
  "fastapi": "is as well"
}
```
then the resulting string would look like `'hello=world&hashnode=1%2C2%2C3&vue=is%2Ccool&fastapi=is%20as%20well'` which would work much better.
There is an argument that you shouldn't need to do something like this when you're passing in the data yourself, but I've found that it can't hurt to just be extra careful with these sorts of things.
Now we should have a valid query string for our `start` and `end` dates, if they exist.

### Convert human-readable interval into yfinance style
The next step is to convert the interval into the style that `yfinance` needs.
For human readability, we're presenting our intervals as "Daily", "Weekly", and "Monthly", but these won't work in `yfinance` and we should actually get errors if we try to pass these values in because we've set the allowable input values to be one of `1d`, `1wk`, or `1mo`.
So, this is as simple as just using a nested JavaScript [ternary operator](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Operators/Conditional_Operator).
```javascript
const interval = 
  state.interval === 'Daily'
    ? '1d'
    : state.interval === 'Weekly'
    ? '1wk'
    : '1mo';
```
This sets the `interval` constant to `1d` if the state's interval value is `Daily`, otherwise if the state's interval value is `Weekly` it sets it to `1wk`, otherwise it sets it to `1mo`.
The equivalent code in `if` statements would be
```javascript
let interval;

if (state.interval === 'Daily') {
  interval = '1d'
} else if (state.interval === 'Weekly') {
  interval = '1wk'
} else {
  interval = '1mo'
}
```

### Create the URL string and add the query if it exists
We can now create the URL that will be used to fetch the data from our server.
We first set up the basic url with the `symbol` and `interval` values
```javascript
let url = `http://localhost:8000/quote/${state.symbol}/${interval}`;
```
and we then need to append any query string, if it exists.
```javascript
if (queryString.length) url = `${url}?${queryString}`;
```
We do this because we need to put a `?` at the beginning of the query string.
The next step is to fetch the data from the server using the built-in `fetch` API.
```javascript
const response = await fetch(url);
const res = await response.json();
```

### Parse the dates and format data
#### Parse dates
The next step is to update the `state`'s `startDate` and `endDate` with the values obtained from the server.
This is done because one or both of the dates input by the user may have been weekends or holidays, or any other myriad possibilities.
We assume that the data we've received from the server contains valid dates, so the simplest way to do this is to just set `state.startDate` to the earliest date, and `state.endDate` to the latest date.
First, we want to create an anonymous function that will format the dates into the format we're currently using on the site.
```javascript
const formatDate = (d) => new Date(d).toISOString().substr(0, 10);
```
and then we sort the dates, and set each one
```javascript
const dates = res.data.map((e) => e.date).sort();
state.startDate = formatDate(dates[0])
state.endDate = formatDate(dates[dates.length - 1])
```

#### Format the data into our desired output
This last step is going to come slightly out of left field; we are going to format the data in a format that will eventually be used by our charting platform.
We're going to have the `x` coordinates be the dates and the `y` coordinates be the data, whether volume or stock prices.
```javascript
const data = res.data.map((e) => ({
  x: new Date(e.date),
  y: e.data
}));
const volData = res.data.map((e) => ({
  x: new Date(e.date),
  y: e.volume ?? 0
}));
```

The entire code of the `handleSubmit` method should now look like this
```javascript
const handleSubmit = async () => {
  v$.value.$validate();
  if (!v$.value.$invalid) {
    loading.value = true;

    // Create the querystring
    const query = {}
    if (!!state.startDate) query.start = state.startDate;
    if (!!state.endDate) query.end = state.endDate;

    const queryString = Object.keys(query)
      .filter((key) => !!query[key])
      .map((key) => {
        return (
          `${encodeURIComponent(key)}=${encodeURIComponent(query[key])}`
        );
      })
      .join('&')

    // Convert human-readable interval into yfinance style
    const interval =
      state.interval === 'Daily'
        ? '1d'
        : state.interval === 'Weekly'
          ? '1wk'
          : '1mo';

    // Create URL string and add query if it exists
    let url = `http://localhost:8000/quote/${state.symbol}/${interval}`;
    if (queryString.length) url = `${url}?${queryString}`;
    const response = await fetch(url);
    const res = await response.json();

    // Parse dates
    const formatDate = (d) => new Date(d).toISOString().substr(0, 10);
    const dates = res.data.map((e) => e.date).sort();
    state.startDate = formatDate(dates[0])
    state.endDate = formatDate(dates[dates.length - 1])

    // Format the data
    const data = res.data.map((e) => ({
      x: new Date(e.date),
      y: e.data
    }));
    const volData = res.data.map((e) => ({
      x: new Date(e.date),
      y: e.volume ?? 0
    }));
    
    loading.value = false;
  }
};
```
You'll notice that we removed the setTimeout and added an entry at the bottom to set the `loading` spinner to false.
Also, we needed to make the function itself `async` in order to utilize the `await` keyword.

In the next article we'll discuss error handling, because having this type of functionality not wrapped in `try` and `catch` blocks is a recipe for disaster.
We'll also add in a dialog to alert the user when an error has taken place.