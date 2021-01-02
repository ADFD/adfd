module.exports = {
  purge: [
    '../web/view/*.html',
],
  darkMode: false, // or 'media' or 'class'
  theme: {
    extend: {},
  },
  variants: {
    extend: {},
  },
  plugins: [
      require('@tailwindcss/typography')
  ],
}
