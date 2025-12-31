<template>
  <div class="modal-overlay" @click.self="close">
    <div class="modal-content">
      <button class="close-button" @click="close">×</button>
      
      <div v-if="loading" class="loading">Loading game details...</div>
      <div v-else-if="gameDetails">
        <div class="modal-header">
          <h2>{{ gameDetails.game.title || gameDetails.game.name }}</h2>
        </div>
        
        <div class="modal-body">
          <div class="game-main-area">
            <div class="game-banner">
              <img 
                v-if="gameDetails.game.appid" 
                :src="`https://cdn.akamai.steamstatic.com/steam/apps/${gameDetails.game.appid}/header.jpg`" 
                :alt="gameDetails.game.title"
                @error="handleImageError"
              />
              <span v-else>{{ gameDetails.game.title.charAt(0) }}</span>
            </div>
            <div class="game-sidebar">
              <div v-if="gameDetails.game.developer"><strong>Developer:</strong> {{ gameDetails.game.developer }}</div>
              <div v-if="gameDetails.game.publisher"><strong>Publisher:</strong> {{ gameDetails.game.publisher }}</div>
              <div v-if="gameDetails.game.release_date"><strong>Release Date:</strong> {{ gameDetails.game.release_date }}</div>
              <div class="game-tags">
                <span v-for="genre in gameDetails.game.genre_list" :key="genre" class="genre-badge">{{ genre }}</span>
              </div>
            </div>
          </div>

          <div class="game-stats-section">
            <div class="stat-card">
              <div :class="['stat-value', getRatingClass(gameDetails.game.average_rating)]">
                {{ formatRating(gameDetails.game.average_rating) }}
              </div>
              <div class="stat-label">Average Rating</div>
            </div>
            <div class="stat-card">
              <div class="stat-value">{{ formatNumber(gameDetails.game.total_downloads) }}</div>
              <div class="stat-label">Total Downloads</div>
            </div>
            <div class="stat-card">
              <div class="stat-value">{{ formatNumber(gameDetails.game.total_reviews) }}</div>
              <div class="stat-label">Total Reviews</div>
            </div>
          </div>
          
          <div class="description-section steam-description">
            <h3>About This Game</h3>
            <p>{{ gameDetails.game.description || 'No description available' }}</p>
          </div>
          
          <div class="steam-actions-bar">
            <div class="steam-price" v-if="gameDetails.game.price !== null">
              {{ gameDetails.game.price > 0 ? '$' + gameDetails.game.price : 'Free to Play' }}
            </div>
            <button 
              v-if="userId"
              @click="toggleDownload"
              @mouseenter="hoveringLibrary = true"
              @mouseleave="hoveringLibrary = false"
              :class="['steam-btn-green', { downloaded: gameDetails.has_downloaded, remove: gameDetails.has_downloaded && hoveringLibrary }]"
            >
              {{ libraryButtonText }}
            </button>
          </div>

          <div class="rating-section" v-if="userId">
            <h3>Your Rating</h3>
            <div class="rating-input">
              <button
                v-for="star in 5"
                :key="star"
                @click="submitRating(star)"
                :class="['star-button', { active: star <= (gameDetails.user_rating || 0) }]"
              >
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="24" height="24" fill="currentColor">
                  <path d="M12 17.27L18.18 21l-1.64-7.03L22 9.24l-7.19-.61L12 2 9.19 8.63 2 9.24l5.46 4.73L5.82 21z"/>
                </svg>
              </button>
              <span v-if="gameDetails.user_rating" class="current-rating">
                Your rating: {{ gameDetails.user_rating }} stars
                <button @click="deleteRating" class="delete-rating-btn" title="Remove rating">🗑️</button>
              </span>
            </div>
          </div>

          <div class="review-form-section" v-if="userId">
            <h3>Write a Review</h3>
            <textarea 
              v-model="newReviewContent" 
              placeholder="What did you think of this game?"
              class="review-textarea"
            ></textarea>
            <button @click="submitReview" :disabled="!newReviewContent.trim() || submittingReview" class="steam-btn-green">
              {{ submittingReview ? 'Posting...' : 'Post Review' }}
            </button>
          </div>
          
          <div class="reviews-section review-area">
            <h3>Recent Reviews</h3>
            <div v-if="gameDetails.reviews.length === 0" class="no-reviews">
              No reviews yet. Be the first to review!
            </div>
            <div v-else class="reviews-list">
              <div v-for="review in gameDetails.reviews" :key="review.id" class="review-item steam-review-card">
                <div class="review-header">
                  <div class="review-user-info">
                    <strong>{{ review.user.username }}</strong>
                    <span class="review-date">{{ formatDate(review.created_at) }}</span>
                  </div>
                  <button 
                    v-if="userId && review.user.id === parseInt(userId)" 
                    @click="deleteReview(review.id)" 
                    class="delete-review-btn"
                    title="Delete your review"
                  >
                    🗑️
                  </button>
                </div>
                <p class="review-content">{{ review.content }}</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios'

export default {
  name: 'GameModal',
  props: {
    game: {
      type: Object,
      required: true
    },
    userId: {
      type: Number,
      default: null
    }
  },
  data() {
    return {
      gameDetails: null,
      loading: true,
      error: null,
      newReviewContent: '',
      submittingReview: false,
      hoveringLibrary: false
    }
  },
  computed: {
    libraryButtonText() {
      if (!this.gameDetails) return ''
      if (this.gameDetails.has_downloaded) {
        return this.hoveringLibrary ? 'Remove from Library' : 'In Library'
      }
      return 'Add to Library'
    }
  },
  methods: {
    async fetchGameDetails() {
      this.loading = true
      try {
        const url = this.userId 
          ? `/api/games/${this.game.id}/details/?user_id=${this.userId}`
          : `/api/games/${this.game.id}/details/`
        const response = await axios.get(url)
        this.gameDetails = response.data
      } catch (err) {
        this.error = 'Failed to load game details'
        console.error(err)
      } finally {
        this.loading = false
      }
    },
    async submitReview() {
      if (!this.userId) {
        alert('Please enter a User ID in the top navigation bar to post a review.')
        return
      }
      
      const userIdInt = parseInt(this.userId)
      if (isNaN(userIdInt)) {
        alert('Invalid User ID. Please enter a number.')
        return
      }
      
      this.submittingReview = true
      try {
        await axios.post('/api/reviews/', {
          user: userIdInt,
          game: this.game.id,
          content: this.newReviewContent
        })
        this.newReviewContent = ''
        // Refresh game details to show the new review
        await this.fetchGameDetails()
      } catch (err) {
        console.error('Failed to submit review:', err)
        if (err.response && err.response.data) {
           console.error('Backend error:', err.response.data)
           alert(`Failed to post review: ${JSON.stringify(err.response.data)}`)
        } else {
           alert('Failed to post review. Check console for details.')
        }
      } finally {
        this.submittingReview = false
      }
    },
    async deleteReview(reviewId) {
      if (!confirm('Are you sure you want to delete this review?')) return
      
      try {
        await axios.delete(`/api/reviews/${reviewId}/`)
        // Refresh game details
        await this.fetchGameDetails()
      } catch (err) {
        console.error('Failed to delete review:', err)
        alert('Failed to delete review. Check console for details.')
      }
    },
    async submitRating(rating) {
      if (!this.userId) {
        alert('Please enter a User ID in the top navigation bar to rate games')
        return
      }

      const userIdInt = parseInt(this.userId)
      if (isNaN(userIdInt)) {
        alert('Invalid User ID. Please enter a number.')
        return
      }
      
      try {
        // Check if user already rated this game
        const existingRatings = await axios.get(`/api/ratings/?user_id=${userIdInt}&game_id=${this.game.id}`)
        
        if (existingRatings.data.length > 0) {
          // Update existing rating
          await axios.put(`/api/ratings/${existingRatings.data[0].id}/`, {
            user: userIdInt,
            game: this.game.id,
            rating: rating
          })
        } else {
          // Create new rating
          await axios.post('/api/ratings/', {
            user: userIdInt,
            game: this.game.id,
            rating: rating
          })
        }
        
        // Refresh game details
        await this.fetchGameDetails()
        this.$emit('rating-updated')
      } catch (err) {
        console.error('Failed to submit rating:', err)
        if (err.response && err.response.data) {
            console.error('Backend error:', err.response.data)
            alert(`Failed to submit rating: ${JSON.stringify(err.response.data)}`)
        } else {
            alert('Failed to submit rating. Make sure the user ID is valid.')
        }
      }
    },
    async deleteRating() {
      if (!this.gameDetails.user_rating_id) return
      if (!confirm('Are you sure you want to remove your rating?')) return

      try {
        await axios.delete(`/api/ratings/${this.gameDetails.user_rating_id}/`)
        await this.fetchGameDetails()
        this.$emit('rating-updated')
      } catch (err) {
        console.error('Failed to delete rating:', err)
        alert('Failed to delete rating.')
      }
    },
    async toggleDownload() {
      if (!this.userId) {
        alert('Please enter a User ID in the top navigation bar to download games')
        return
      }
      
      const userIdInt = parseInt(this.userId)
      if (isNaN(userIdInt)) {
        alert('Invalid User ID. Please enter a number.')
        return
      }

      try {
        if (this.gameDetails.has_downloaded) {
          // Remove download
          const response = await axios.get(`/api/downloads/?user_id=${userIdInt}&game_id=${this.game.id}`)
          // Handle potential pagination
          const downloads = response.data.results || response.data
          
          if (downloads.length > 0) {
            await axios.delete(`/api/downloads/${downloads[0].id}/`)
          }
        } else {
          // Add download
          await axios.post('/api/downloads/', {
            user: userIdInt,
            game: this.game.id
          })
        }
        
        // Refresh game details
        await this.fetchGameDetails()
      } catch (err) {
        console.error('Failed to toggle download:', err)
        if (err.response && err.response.data) {
            alert(`Failed to update download status: ${JSON.stringify(err.response.data)}`)
        } else {
            alert('Failed to update download status. Make sure the user ID is valid.')
        }
      }
    },
    close() {
      this.$emit('close')
    },
    formatDate(dateString) {
      const date = new Date(dateString)
      return date.toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric' })
    },
    formatRating(rating) {
      if (rating === null || rating === undefined || rating === 0) return 'N/A'
      return Number(rating).toFixed(1)
    },
    formatNumber(num) {
      if (num === null || num === undefined) return '0'
      if (num >= 1000000) {
        return (num / 1000000).toFixed(1) + 'M'
      }
      if (num >= 1000) {
        return (num / 1000).toFixed(1) + 'K'
      }
      return num.toString()
    },
    getRatingClass(rating) {
      if (!rating) return ''
      if (rating >= 4) return 'rating-high'
      if (rating >= 2.5) return 'rating-mid'
      return 'rating-low'
    },
    handleImageError(e) {
      e.target.style.display = 'none'
    }
  },
  mounted() {
    this.fetchGameDetails()
  },
  watch: {
    game() {
      if (this.game) {
        this.fetchGameDetails()
      }
    }
  }
}
</script>

