/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './templates/**/*.html',       // Sucht in Ihrem Haupt-Template-Ordner
    './**/templates/**/*.html',    // Sucht in den Template-Ordnern Ihrer Apps (z.B. belege/templates/)
    './**/forms.py'                // Falls Sie Klassen in Forms.py verwenden
  ],
  theme: {
    extend: {},
  },
  plugins: [],
}