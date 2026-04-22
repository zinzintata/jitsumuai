/** @type {import('tailwindcss').Config} */
export default {
  content: ['./src/**/*.{astro,html,js,jsx,md,mdx,svelte,ts,tsx,vue}'],
  theme: {
    extend: {
      fontFamily: {
        sans: [
          '"Hiragino Kaku Gothic ProN"',
          '"Hiragino Sans"',
          'Meiryo',
          'sans-serif',
        ],
      },
      typography: {
        DEFAULT: {
          css: {
            maxWidth: 'none',
            color: '#1a1a1a',
            lineHeight: '1.9',
            h2: { fontWeight: '700', marginTop: '2em', marginBottom: '0.75em' },
            h3: { fontWeight: '700', marginTop: '1.5em', marginBottom: '0.5em' },
            'ul > li': { paddingLeft: '1.5em' },
            blockquote: {
              borderLeftColor: '#3b82f6',
              backgroundColor: '#eff6ff',
              padding: '0.5em 1em',
              borderRadius: '0.25rem',
            },
            table: { fontSize: '0.9em' },
            code: {
              backgroundColor: '#f3f4f6',
              padding: '0.1em 0.4em',
              borderRadius: '0.25rem',
              fontWeight: '400',
            },
            'code::before': { content: '""' },
            'code::after': { content: '""' },
          },
        },
      },
    },
  },
  plugins: [
    require('@tailwindcss/typography'),
  ],
};
