import { createApp } from 'vue'
import { createRouter, createWebHistory } from 'vue-router'
import axios from 'axios'
import App from './App.vue'
import RecommendedGames from './components/RecommendedGames.vue'
import AllGames from './components/AllGames.vue'
import MyGames from './components/MyGames.vue'
import AnalyticsDashboard from './components/AnalyticsDashboard.vue'

// Configure Axios
let apiUrl = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000'
if (apiUrl && !apiUrl.startsWith('http')) {
  apiUrl = `https://${apiUrl}`
}
axios.defaults.baseURL = apiUrl

const routes = [
  { path: '/', redirect: '/recommended' },
  { path: '/recommended', component: RecommendedGames },
  { path: '/all-games', component: AllGames },
  { path: '/my-games', component: MyGames },
  { path: '/analytics', component: AnalyticsDashboard }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

createApp(App).use(router).mount('#app')



