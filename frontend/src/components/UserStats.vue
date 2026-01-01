<template>
  <div class="stats-container" v-if="chartData.labels && chartData.labels.length > 0">
    <h3 class="text-xl font-bold mb-4 text-center">Your Taste Profile</h3>
    <div class="chart-wrapper">
      <Radar :data="chartData" :options="chartOptions" />
    </div>
    <p class="text-sm text-gray-500 text-center mt-2">
      The neural network learns from your interactions. This shape represents the "Genre Bias" vector in your hidden profile.
    </p>
  </div>
</template>

<script>
import {
  Chart as ChartJS,
  RadialLinearScale,
  PointElement,
  LineElement,
  Filler,
  Tooltip,
  Legend
} from 'chart.js'
import { Radar } from 'vue-chartjs'
import axios from 'axios'

ChartJS.register(
  RadialLinearScale,
  PointElement,
  LineElement,
  Filler,
  Tooltip,
  Legend
)

export default {
  name: 'UserStats',
  components: { Radar },
  props: ['userId'],
  data() {
    return {
      chartData: { labels: [], datasets: [] },
      chartOptions: {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
          r: {
            angleLines: { color: 'rgba(255, 255, 255, 0.2)' },
            grid: { color: 'rgba(255, 255, 255, 0.2)' },
            pointLabels: { color: '#e5e7eb', font: { size: 12 } },
            ticks: { display: false }
          }
        },
        plugins: {
          legend: { display: false }
        }
      }
    }
  },
  watch: {
    userId: {
      immediate: true,
      handler(newId) {
        if (newId) this.fetchStats(newId)
      }
    }
  },
  methods: {
    async fetchStats(uid) {
      try {
        const res = await axios.get(`/api/user-stats/?user_id=${uid}`)
        this.chartData = res.data
      } catch (e) {
        console.error("Stats error", e)
      }
    }
  }
}
</script>

<style scoped>
.stats-container {
  background: #1f2937;
  padding: 1.5rem;
  border-radius: 1rem;
  margin-bottom: 2rem;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
}
.chart-wrapper {
  height: 300px;
  position: relative;
}
</style>
