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
