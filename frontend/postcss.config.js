/** @type {import('postcss-load-config').Config} */
const config = {
  plugins: {
    // Tailwind CSS v4 uses the new @tailwindcss/postcss plugin
    '@tailwindcss/postcss': {},
  },
};

module.exports = config;
