import { createApp } from 'vue'
import { createRouter, createWebHistory } from 'vue-router'
import axios from 'axios'
import App from './App.vue'
import RecommendedGames from './components/RecommendedGames.vue'
import AllGames from './components/AllGames.vue'
import MyGames from './components/MyGames.vue'

// Configure Axios
axios.defaults.baseURL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000'

const routes = [
  { path: '/', redirect: '/recommended' },
  { path: '/recommended', component: RecommendedGames },
  { path: '/all-games', component: AllGames },
  { path: '/my-games', component: MyGames }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

createApp(App).use(router).mount('#app')

