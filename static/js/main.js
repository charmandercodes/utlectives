// Add this at the beginning of your app entry.
import { sayHello } from './important.js';
import '@/css/main.css';
import 'flowbite';
import htmx from 'htmx.org';
import Alpine from 'alpinejs'
console.log('Hello from main.js');
sayHello('World!');
window.htmx = htmx
window.Alpine = Alpine
Alpine.start()