<template>
  <div class="games-page">
    <h2>All Games</h2>
    <div class="search-bar">
      <input 
        type="text" 
        v-model="searchQuery" 
        placeholder="Search games..."
        class="search-input"
        @input="handleSearch"
      />
      <select v-model="genreFilter" class="genre-filter" @change="resetAndFetch">
        <option value="">All Genres</option>
        <option v-for="genre in availableGenres" :key="genre" :value="genre">{{ genre }}</option>
      </select>
    </div>
    
    <div v-if="loading && games.length === 0" class="loading">Loading games...</div>
    <div v-else-if="error" class="error">{{ error }}</div>
    <div v-else>
      <div class="games-grid">
        <GameCard 
          v-for="game in games" 
          :key="game.id" 
          :game="game"
          @click="openModal(game)"
        />
      </div>
      <div v-if="nextPage" class="load-more-container">
        <button @click="fetchGames(nextPage)" :disabled="loading" class="load-more-button">
          {{ loading ? 'Loading...' : 'Load More Games' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios'
import GameCard from './GameCard.vue'

export default {
  name: 'AllGames',
  components: {
    GameCard
  },
  props: {
    userId: {
      type: Number,
      default: 1
    }
  },
  data() {
    return {
      games: [],
      nextPage: null,
      loading: true,
      error: null,
      searchQuery: '',
      genreFilter: '',
      availableGenres: [],
      searchTimeout: null
    }
  },
  methods: {
    async fetchGenres() {
      try {
        const response = await axios.get('/api/games/genres/')
        this.availableGenres = response.data
      } catch (err) {
        console.error('Failed to fetch genres:', err)
        // Fallback to basic genres
        this.availableGenres = [
          'Action', 'Adventure', 'Casual', 'Indie', 'RPG', 'Simulation', 'Strategy'
        ]
      }
    },
    async fetchGames(url = '/api/games/') {
      this.loading = true
      this.error = null
      try {
        const params = {}
        if (!url.includes('?')) {
          if (this.searchQuery) params.search = this.searchQuery
          if (this.genreFilter) params.genre = this.genreFilter
        }
        
        const response = await axios.get(url, { params })
        
        if (url === '/api/games/') {
          this.games = response.data.results
        } else {
          this.games = [...this.games, ...response.data.results]
        }
        this.nextPage = response.data.next
      } catch (err) {
        this.error = 'Failed to load games'
        console.error(err)
      } finally {
        this.loading = false
      }
    },
    handleSearch() {
      clearTimeout(this.searchTimeout)
      this.searchTimeout = setTimeout(() => {
        this.resetAndFetch()
      }, 500)
    },
    resetAndFetch() {
      this.games = []
      this.fetchGames()
    },
    openModal(game) {
      this.$emit('show-game-modal', game)
    }
  },
  mounted() {
    this.fetchGenres()
    this.fetchGames()
  }
}
</script>

