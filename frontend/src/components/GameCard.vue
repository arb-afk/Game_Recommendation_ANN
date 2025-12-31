<template>
  <div class="game-card" @click="$emit('click')">
    <div class="game-image-container">
      <img 
        v-if="game.appid" 
        :src="`https://cdn.akamai.steamstatic.com/steam/apps/${game.appid}/header.jpg`" 
        :alt="game.title"
        class="game-image"
        @error="handleImageError"
      />
      <div v-else class="game-image-placeholder">
        <span>{{ game.title ? game.title.charAt(0) : '?' }}</span>
      </div>
    </div>
    <div class="game-card-content">
      <h3 class="game-title" :title="game.title">{{ game.title }}</h3>
      <div class="game-meta-row">
        <div class="game-tags">
          <span 
            v-for="genre in (game.genre_list ? game.genre_list.slice(0, 3) : [])" 
            :key="genre" 
            class="genre-badge"
          >
            {{ genre }}
          </span>
          <span v-if="game.genre_list && game.genre_list.length > 3" class="more-tags">...</span>
          <span v-else-if="!game.genre_list" class="genre-badge">Game</span>
        </div>
        <div class="price-tag">
          {{ game.price ? '$' + game.price : 'Free' }}
        </div>
      </div>
      <div class="game-rating" v-if="game.average_rating">
        <span class="rating-value">
          <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="14" height="14" fill="#66c0f4" class="card-star">
            <path d="M12 17.27L18.18 21l-1.64-7.03L22 9.24l-7.19-.61L12 2 9.19 8.63 2 9.24l5.46 4.73L5.82 21z"/>
          </svg> 
          {{ game.average_rating }}
        </span>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'GameCard',
  props: {
    game: {
      type: Object,
      required: true
    }
  },
  methods: {
    handleImageError(e) {
      e.target.style.display = 'none'
      e.target.parentElement.classList.add('show-placeholder')
    }
  }
}
</script>