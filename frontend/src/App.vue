<template>
  <div id="app">
    <nav class="navbar">
      <div class="nav-container">
        <h1 class="logo">Game Recommender</h1>
        <div class="nav-links">
          <router-link to="/recommended" class="nav-link">Recommended</router-link>
          <router-link to="/all-games" class="nav-link">All Games</router-link>
          <router-link to="/my-games" class="nav-link">My Games</router-link>
          <div class="user-info">
            <label>User ID</label>
            <div class="user-id-wrapper">
              <button @click="decrementUserId" :disabled="userId <= 1" class="user-id-btn">−</button>
              <input 
                type="number" 
                v-model.number="userId" 
                @change="updateUserId"
                class="user-id-input"
                placeholder="ID"
                min="1"
              />
              <button @click="incrementUserId" class="user-id-btn">+</button>
            </div>
          </div>
        </div>
      </div>
    </nav>
    
    <main class="main-content">
      <router-view :userId="userId" :key="refreshKey" @show-game-modal="showGameModal" />
    </main>
    
    <GameModal 
      v-if="selectedGame" 
      :game="selectedGame" 
      :userId="userId"
      @close="closeModal"
      @rating-updated="handleRatingUpdate"
    />
  </div>
</template>

<script>
import GameModal from './components/GameModal.vue'

export default {
  name: 'App',
  components: {
    GameModal
  },
  data() {
    return {
      userId: 1,
      selectedGame: null,
      refreshKey: 0
    }
  },
  methods: {
    incrementUserId() {
      this.userId++
      this.updateUserId()
    },
    decrementUserId() {
      if (this.userId > 1) {
        this.userId--
        this.updateUserId()
      }
    },
    updateUserId() {
      // If empty or invalid, default to 1
      if (!this.userId || this.userId < 1) {
        this.userId = 1
      }
      // Store user ID in localStorage
      localStorage.setItem('userId', this.userId)
      // Force refresh when user changes
      this.refreshKey++
    },
    showGameModal(game) {
      this.selectedGame = game
    },
    closeModal() {
      this.selectedGame = null
    },
    handleRatingUpdate() {
      // Increment key to force router-view to re-render and fetch fresh data
      this.refreshKey++
    }
  },
  mounted() {
    // Load user ID from localStorage if available
    const savedUserId = localStorage.getItem('userId')
    if (savedUserId) {
      const parsedId = parseInt(savedUserId)
      this.userId = isNaN(parsedId) || parsedId < 1 ? 1 : parsedId
    }
  }
}
</script>

