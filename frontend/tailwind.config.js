/** @type {import('tailwindcss').Config} */
export default {
    content: [
        "./index.html",
        "./src/**/*.{js,ts,jsx,tsx}",
    ],
    theme: {
        extend: {
            colors: {
                background: '#111315',
                card: '#1A1C1E',
                primary: '#FFFFFF',
                secondary: '#9BA0A5',
                accent: '#EAFD60',
                success: '#27C46B',
                error: '#FF4D4D',
            },
            fontFamily: {
                sans: ['Inter', 'system-ui', 'sans-serif'],
            },
        },
    },
    plugins: [],
}
