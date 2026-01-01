<template>
  <div class="analytics-dashboard">
    <div class="header-section">
      <h2 class="dashboard-title">System Analytics & Model Intelligence</h2>
      <p class="dashboard-subtitle">Real-time performance metrics and dataset distribution analysis</p>
    </div>

    <div v-if="loading" class="loading-state">
      <div class="spinner"></div>
      <span>Computing Neural Metrics...</span>
    </div>
    
    <div v-else-if="error" class="error-state">
      <div class="error-icon">⚠️</div>
      <p>{{ error }}</p>
    </div>
    
    <div v-else class="dashboard-grid">
      
      <!-- 1. Model Metrics Table -->
      <div class="card full-width animate-in">
        <div class="card-header">
          <div class="header-icon sse-icon"></div>
          <h3 class="card-title">Neural Network Performance</h3>
        </div>
        <div class="table-container">
          <table class="analytics-table">
            <thead>
              <tr>
                <th>Metric</th>
                <th>Value</th>
                <th>Interpretation</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td class="metric-name">SSE</td>
                <td class="metric-value highlight">{{ metrics.sse }}</td>
                <td class="metric-desc">Sum of Squared Errors. Measures the total error magnitude in the network's predictions.</td>
              </tr>
              <tr>
                <td class="metric-name">MSE</td>
                <td class="metric-value">{{ metrics.mse }}</td>
                <td class="metric-desc">Mean Squared Error. The average squared distance between predicted and actual ratings.</td>
              </tr>
              <tr>
                <td class="metric-name">RMSE</td>
                <td class="metric-value highlight">{{ metrics.rmse }}</td>
                <td class="metric-desc">Root Mean Squared Error. Represents the average prediction error in star units (0-1 range).</td>
              </tr>
              <tr class="status-row">
                <td class="metric-name">Engine Status</td>
                <td class="metric-value status-badge" :class="metrics.status.toLowerCase()">{{ metrics.status }}</td>
                <td class="metric-desc">Current state of the TensorFlow recommender core.</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- 2. Genre Distribution -->
      <div class="card animate-in delay-1">
        <div class="card-header">
          <div class="header-icon genre-icon"></div>
          <h3 class="card-title">Catalog Diversity (Top Genres)</h3>
        </div>
        <div class="chart-box">
          <Bar :data="genreChartData" :options="barOptions" />
        </div>
      </div>

      <!-- 3. Rating Distribution (Line/Area) -->
      <div class="card">
        <div class="card-header">
          <div class="header-icon rating-icon"></div>
          <h3 class="card-title">Dataset: Rating Distribution</h3>
        </div>
        <div class="chart-box">
          <LineChart :data="ratingChartData" :options="lineOptions" />
        </div>
      </div>

      <!-- NEW: Per-User Accuracy Distribution (Bar) -->
      <div class="card animate-in delay-2">
        <div class="card-header">
          <div class="header-icon accuracy-icon"></div>
          <h3 class="card-title">Per-User Model Accuracy (RMSE)</h3>
        </div>
        <p class="chart-description">How many users have low vs. high prediction error. Left-skewed is better.</p>
        <div class="chart-box">
          <Bar :data="accuracyChartData" :options="barOptions" />
        </div>
      </div>

      <!-- NEW: Learning Curve (Activity Scatter) -->
      <div class="card animate-in delay-2">
        <div class="card-header">
          <div class="header-icon learning-icon"></div>
          <h3 class="card-title">Learning Curve (Activity vs. Error)</h3>
        </div>
        <p class="chart-description">Does the model get smarter as users rate more games? (Trend should go down).</p>
        <div class="chart-box">
          <Scatter :data="activityChartData" :options="activityOptions" />
        </div>
      </div>

      <!-- 4. Bias Analysis (Scatter) -->
      <div class="card full-width animate-in delay-3">
        <div class="card-header">
          <div class="header-icon bias-icon"></div>
          <h3 class="card-title">Algorithmic Bias: Popularity vs. User Quality</h3>
        </div>
        <p class="chart-description">Each dot is a game. This analyzes if the system is biased toward high-volume games regardless of quality.</p>
        <div class="chart-box scatter-box">
          <Scatter :data="biasChartData" :options="scatterOptions" />
        </div>
      </div>

    </div>
  </div>
</template>

<script>
import axios from 'axios'
// ... rest of imports
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend,
  Filler
} from 'chart.js'
import { Bar, Line as LineChart, Scatter } from 'vue-chartjs'

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend,
  Filler
)

export default {
  name: 'AnalyticsDashboard',
  components: { Bar, LineChart, Scatter },
  data() {
    return {
      loading: true,
      error: null,
      metrics: {},
      researchData: {},
      genreChartData: { labels: [], datasets: [] },
      ratingChartData: { labels: [], datasets: [] },
      accuracyChartData: { labels: [], datasets: [] },
      activityChartData: { datasets: [] },
      biasChartData: { datasets: [] },
      
      barOptions: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: { legend: { display: false } },
        scales: {
          y: { grid: { color: 'rgba(255,255,255,0.05)' }, ticks: { color: '#9ca3af' } },
          x: { grid: { display: false }, ticks: { color: '#9ca3af' } }
        }
      },
      activityOptions: {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
          x: { 
            title: { display: true, text: 'User Activity (Ratings Count)', color: '#6b7280' },
            grid: { color: 'rgba(255,255,255,0.05)' }, 
            ticks: { color: '#9ca3af' } 
          },
          y: { 
            title: { display: true, text: 'Prediction Error (RMSE)', color: '#6b7280' },
            grid: { color: 'rgba(255,255,255,0.05)' }, 
            ticks: { color: '#9ca3af' }
          }
        },
        plugins: { legend: { display: false } }
      },
      lineOptions: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: { legend: { display: false } },
        scales: {
          y: { grid: { color: 'rgba(255,255,255,0.05)' }, ticks: { color: '#9ca3af' } },
          x: { grid: { display: false }, ticks: { color: '#9ca3af' } }
        }
      },
      scatterOptions: {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
          x: { 
            title: { display: true, text: 'Popularity (Steam Recs)', color: '#6b7280' },
            grid: { color: 'rgba(255,255,255,0.05)' }, 
            ticks: { color: '#9ca3af' } 
          },
          y: { 
            title: { display: true, text: 'Avg User Rating (1-5)', color: '#6b7280' },
            grid: { color: 'rgba(255,255,255,0.05)' }, 
            ticks: { color: '#9ca3af' },
            min: 1,
            max: 5
          }
        },
        plugins: {
          tooltip: {
            backgroundColor: '#1f2937',
            titleColor: '#10b981',
            padding: 12,
            cornerRadius: 8,
            callbacks: {
              label: (ctx) => {
                return ` ${ctx.raw.game} | Rating: ${ctx.raw.y} | Pop: ${ctx.raw.x.toLocaleString()}`
              }
            }
          }
        }
      }
    }
  },
  methods: {
    async fetchData() {
      try {
        const res = await axios.get('/api/analytics/')
        const d = res.data
        this.metrics = d.model_metrics
        this.researchData = d.qualitative_analysis || {}
        
        // Genre Bar
        
        this.genreChartData = {
          labels: d.genre_dist.labels,
          datasets: [{
            label: 'Games',
            backgroundColor: '#3b82f6',
            borderRadius: 4,
            data: d.genre_dist.data
          }]
        }
        
        this.ratingChartData = {
          labels: d.rating_dist.labels,
          datasets: [{
            label: 'Count',
            borderColor: '#10b981',
            backgroundColor: 'rgba(16, 185, 129, 0.1)',
            fill: true,
            tension: 0.4,
            pointRadius: 4,
            data: d.rating_dist.data
          }]
        }

        // Accuracy Histogram
        if (d.user_error_dist) {
          this.accuracyChartData = {
            labels: d.user_error_dist.labels,
            datasets: [{
              label: 'Number of Users',
              backgroundColor: '#8b5cf6', // Violet
              borderRadius: 4,
              data: d.user_error_dist.data
            }]
          }
        }
        
        // Activity Scatter
        if (d.activity_scatter) {
          this.activityChartData = {
            datasets: [{
              label: 'Users',
              backgroundColor: '#ec4899', // Pink
              data: d.activity_scatter.map(u => ({ x: u.count, y: u.rmse }))
            }]
          }
        }
        
        const scatterPoints = d.bias_analysis.rating.map((rating, i) => ({
          x: d.bias_analysis.popularity[i],
          y: rating,
          game: d.bias_analysis.labels[i]
        }))
        
        this.biasChartData = {
          datasets: [{
            label: 'Games',
            backgroundColor: '#f59e0b',
            pointRadius: 6,
            pointHoverRadius: 8,
            data: scatterPoints
          }]
        }
        
        this.loading = false
      } catch (e) {
        console.error(e)
        this.error = "Telemetry connection failed. Is the backend running?"
        this.loading = false
      }
    }
  },
  mounted() {
    this.fetchData()
  }
}
</script>

<style scoped>
.analytics-dashboard {
  color: #f3f4f6;
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem 1rem;
}

/* Header */
.header-section {
  margin-bottom: 3rem;
  border-left: 4px solid #10b981;
  padding-left: 1.5rem;
}
.dashboard-title {
  font-size: 2.25rem;
  font-weight: 800;
  letter-spacing: -0.025em;
  margin-bottom: 0.5rem;
}
.dashboard-subtitle {
  color: #9ca3af;
  font-size: 1.1rem;
}

/* Grid & Cards */
.dashboard-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 2rem;
}
.full-width {
  grid-column: span 2;
}

.card {
  background: #111827;
  border: 1px solid #374151;
  border-radius: 1rem;
  padding: 1.5rem;
  transition: transform 0.2s, box-shadow 0.2s;
}
.card:hover {
  box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.4);
  border-color: #4b5563;
}

.card-header {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin-bottom: 1.5rem;
}
.card-title {
  font-size: 1.25rem;
  font-weight: 700;
  color: #f9fafb;
}

/* Table Design */
.table-container {
  background: rgba(0,0,0,0.2);
  border-radius: 0.75rem;
  overflow: hidden;
  border: 1px solid #1f2937;
}
.analytics-table {
  width: 100%;
  border-collapse: collapse;
}
.analytics-table th {
  background: #1f2937;
  padding: 1rem;
  text-align: left;
  font-size: 0.875rem;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: #9ca3af;
  border-bottom: 2px solid #374151;
}
.analytics-table td {
  padding: 1.25rem 1rem;
  border-bottom: 1px solid #1f2937;
}
.analytics-table tr:last-child td {
  border-bottom: none;
}
.analytics-table tr:hover {
  background: rgba(255,255,255,0.02);
}

.metric-name {
  font-weight: 700;
  color: #9ca3af;
  font-family: 'Fira Code', monospace;
}
.metric-value {
  font-size: 1.1rem;
  font-weight: 600;
  color: #fff;
}
.metric-value.highlight {
  color: #10b981;
}
.metric-desc {
  color: #6b7280;
  font-size: 0.875rem;
}

.status-badge {
  display: inline-block;
  padding: 0.25rem 0.75rem;
  border-radius: 9999px;
  background: #064e3b;
  color: #34d399;
  font-size: 0.75rem;
  font-weight: 700;
}

/* Charts */
.chart-box {
  height: 300px;
  position: relative;
}
.scatter-box {
  height: 400px;
}
.chart-description {
  color: #9ca3af;
  font-size: 0.875rem;
  margin-bottom: 1rem;
}

/* Loading & Error */
.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 5rem;
  gap: 1rem;
  color: #10b981;
}
.spinner {
  width: 40px;
  height: 40px;
  border: 4px solid rgba(16, 185, 129, 0.1);
  border-left-color: #10b981;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }

/* Animations */
.animate-in {
  animation: slideUp 0.5s ease-out forwards;
  opacity: 0;
}
.delay-1 { animation-delay: 0.1s; }
.delay-2 { animation-delay: 0.2s; }
.delay-3 { animation-delay: 0.3s; }

@keyframes slideUp {
  from { transform: translateY(20px); opacity: 0; }
  to { transform: translateY(0); opacity: 1; }
}

@media (max-width: 768px) {
  .dashboard-grid { grid-template-columns: 1fr; }
  .full-width { grid-column: span 1; }
  .dashboard-title { font-size: 1.75rem; }
}
</style>