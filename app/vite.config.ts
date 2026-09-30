import react from '@vitejs/plugin-react'
import prefixSelector from 'postcss-prefix-selector'
import { defineConfig } from 'vite'

// https://vite.dev/config/
export default defineConfig({
  base: '/crossdockpoc/',
  plugins: [react()],
  css: {
    postcss: {
      plugins: [
        // Bootstrap 4 collides with theme.css (.btn, .btn-primary, …), so its rules are
        // only ever applied under a `.bs4` wrapper. `:root`/`html`/`body` map onto the wrapper itself.
        prefixSelector({
          prefix: '.bs4',
          includeFiles: [/node_modules[\\/]bootstrap[\\/]dist[\\/]css[\\/]/],
        }),
      ],
    },
  },
})
