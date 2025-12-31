<template>
  <div class="games-page">
    <h2>My Games</h2>
    <div v-if="!userId" class="info-message">
      Please enter a User ID in the navigation bar to view your games.
    </div>
    <div v-else>
      <div class="search-bar">
        <input 
          type="text" 
          v-model="searchQuery" 
          placeholder="Search my games..."
          class="search-input"
          @input="handleSearch"
        />
        <select v-model="genreFilter" class="genre-filter" @change="resetAndFetch">
          <option value="">All Genres</option>
          <option v-for="genre in availableGenres" :key="genre" :value="genre">{{ genre }}</option>
        </select>
      </div>

      <div v-if="loading && games.length === 0" class="loading">Loading your games...</div>
      <div v-else-if="error" class="error">{{ error }}</div>
      <div v-else-if="games.length === 0" class="info-message">
        {{ hasFilters ? 'No games found matching your search.' : "You haven't downloaded any games yet." }}
      </div>
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
  </div>
</template>

<script>
import axios from 'axios'
import GameCard from './GameCard.vue'

export default {
  name: 'MyGames',
  components: {
    GameCard
  },
  props: {
    userId: {
      type: Number,
      default: null
    }
  },
  data() {
    return {
      games: [],
      nextPage: null,
      loading: false,
      error: null,
      searchQuery: '',
      genreFilter: '',
      availableGenres: [],
      searchTimeout: null
    }
  },
  computed: {
    hasFilters() {
      return this.searchQuery || this.genreFilter
    }
  },
  watch: {
    userId() {
      if (this.userId) {
        this.resetAndFetch()
      } else {
        this.games = []
      }
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
    async fetchGames(url = null) {
      if (!this.userId) return
      
      this.loading = true
      this.error = null
      
      try {
        const endpoint = url || '/api/games/my_games/'
        const params = {}
        
        if (!url) {
           params.user_id = this.userId
           if (this.searchQuery) params.search = this.searchQuery
           if (this.genreFilter) params.genre = this.genreFilter
        }
        
        const response = await axios.get(endpoint, { params })
        const newGames = response.data.results || response.data
        
        if (!url) {
          this.games = newGames
        } else {
          this.games = [...this.games, ...newGames]
        }
        this.nextPage = response.data.next
        
      } catch (err) {
        this.error = 'Failed to load your games'
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
    if (this.userId) {
      this.fetchGames()
    }
  }
}
</script>

