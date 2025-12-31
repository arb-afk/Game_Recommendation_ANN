<template>
  <div class="games-page">
    <h2>Recommended Games</h2>
    <div class="search-bar">
      <input 
        type="text" 
        v-model="searchQuery" 
        placeholder="Search recommended..."
        class="search-input"
        @input="handleSearch"
      />
      <select v-model="genreFilter" class="genre-filter" @change="resetAndFetch">
        <option value="">All Genres</option>
        <option v-for="genre in availableGenres" :key="genre" :value="genre">{{ genre }}</option>
      </select>
      <input 
        type="number" 
        v-model.number="yearFilter" 
        placeholder="Year" 
        class="year-filter" 
        min="1950" 
        max="2030"
        @change="resetAndFetch"
      />
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
  name: 'RecommendedGames',
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
      yearFilter: null,
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
        this.availableGenres = [
          'Action', 'Adventure', 'Casual', 'Indie', 'RPG', 'Simulation', 'Strategy'
        ]
      }
    },
    async fetchGames(url = '/api/games/recommended/') {
      this.loading = true
      this.error = null
      try {
        // Prepare config with params only for the initial call or if preserving query params
        const config = {}
        if (url === '/api/games/recommended/') {
           config.params = { user_id: this.userId }
           if (this.searchQuery) config.params.search = this.searchQuery
           if (this.genreFilter) config.params.genre = this.genreFilter
           if (this.yearFilter) config.params.release_year = this.yearFilter
        }

        const response = await axios.get(url, config)
        
        // Handle paginated response
        const newGames = response.data.results || response.data
        
        if (url === '/api/games/recommended/') {
          this.games = newGames
        } else {
          this.games = [...this.games, ...newGames]
        }
        
        this.nextPage = response.data.next
      } catch (err) {
        this.error = 'Failed to load recommended games'
        console.error(err)
        if (err.response) {
          console.error('Error details:', err.response.data)
        }
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
  },
  watch: {
    userId() {
      // Refresh when user changes
      this.resetAndFetch()
    }
  }
}
</script>

